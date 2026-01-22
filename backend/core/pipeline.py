"""
Main Video Processing Pipeline.
Orchestrates detection, tracking, action recognition, and event logging.
"""

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from tqdm import tqdm

from backend.config import settings
from backend.core.actions import ActionClassifier
from backend.core.detector import YOLOv8Detector
from backend.core.events import EventLogger
from backend.core.tracker import ByteTracker
from backend.core.video_io import VideoReader, VideoWriter
from backend.utils.performance import PerformanceMonitor
from backend.utils.visualization import draw_annotations, draw_fps

# Week 3 imports
from backend.core.fight_detector import FightDetector
from backend.core.heatmap import HeatmapGenerator
from backend.core.alerts import AlertGenerator
from backend.core.notifications import create_webhook_callback


class VideoPipeline:
    """
    End-to-end video processing pipeline.

    Pipeline stages:
    1. Video loading & frame extraction
    2. Person detection (YOLO)
    3. Multi-object tracking (ByteTrack)
    4. Action classification (rule-based)
    5. Event generation
    6. Video annotation & export
    """

    def __init__(
        self,
        detector: Optional[YOLOv8Detector] = None,
        tracker: Optional[ByteTracker] = None,
        action_classifier: Optional[ActionClassifier] = None,
        fight_detector: Optional[FightDetector] = None,
        frame_skip: int = None,
        show_progress: bool = True,
    ):
        """
        Initialize video processing pipeline.

        Args:
            detector: YOLOv8Detector instance (creates new if None)
            tracker: ByteTracker instance (creates new if None)
            action_classifier: ActionClassifier instance (creates new if None)
            fight_detector: FightDetector instance (creates new if None, Week 3)
            frame_skip: Process every Nth frame (default from config)
            show_progress: Show progress bar
        """
        self.detector = detector or YOLOv8Detector()
        self.tracker = tracker or ByteTracker()
        self.action_classifier = action_classifier or ActionClassifier()
        self.frame_skip = frame_skip or settings.FRAME_SKIP
        self.show_progress = show_progress

        # Week 3: Fight detection
        self.fight_detector = fight_detector
        if self.fight_detector is None and settings.FIGHT_DETECTION_ENABLED:
            self.fight_detector = FightDetector()

        self.perf_monitor = PerformanceMonitor()

        print(f"✓ Pipeline initialized (frame_skip={self.frame_skip}, "
              f"fight_detection={'ON' if self.fight_detector else 'OFF'})")

    def process_video(
        self,
        input_path: Path,
        output_path: Path,
        events_path: Optional[Path] = None,
        heatmap_path: Optional[Path] = None,
        alerts_path: Optional[Path] = None,
        job_id: str = "unknown",
    ) -> dict:
        """
        Process a video file end-to-end.

        Args:
            input_path: Path to input video
            output_path: Path to output annotated video
            events_path: Path to save events JSON (optional)
            heatmap_path: Path to save heatmap PNG (optional, Week 3)
            job_id: Job identifier for logging

        Returns:
            Processing results dict with events and performance stats
        """
        print(f"\n{'='*60}")
        print(f"Processing: {input_path.name}")
        print(f"{'='*60}\n")

        # Initialize components
        reader = VideoReader(input_path, frame_skip=self.frame_skip)
        writer = VideoWriter(
            output_path,
            fps=settings.OUTPUT_FPS,
            frame_size=(reader.width, reader.height),
            codec=settings.OUTPUT_CODEC,
        )
        event_logger = EventLogger(job_id=job_id, fps=reader.fps)

        # Update action classifier with actual frame height
        self.action_classifier.frame_height = reader.height
        if self.action_classifier.fall_detector:
            self.action_classifier.fall_detector.frame_height = reader.height

        # Initialize heatmap generator (Week 3)
        heatmap_gen = None
        if settings.HEATMAP_ENABLED and heatmap_path:
            heatmap_gen = HeatmapGenerator((reader.width, reader.height))

        # Initialize alert generator (Week 3)
        alert_gen = None
        if settings.ALERTS_ENABLED and alerts_path:
            alert_gen = AlertGenerator(fps=reader.fps)
            # Setup webhook callback if configured
            if settings.ALERT_WEBHOOK_URL:
                webhook_callback = create_webhook_callback()
                alert_gen.register_callback("fall_detected", webhook_callback)
                alert_gen.register_callback("fight_detected", webhook_callback)
                alert_gen.register_callback("prolonged_loitering", webhook_callback)
                alert_gen.register_callback("crowd_detected", webhook_callback)

        # Reset tracker and fight detector for new video
        self.tracker.reset()
        if self.fight_detector:
            self.fight_detector.reset()

        # Start performance monitoring
        self.perf_monitor.start_session()

        # Progress bar
        pbar = None
        if self.show_progress:
            total_frames = reader.total_frames // self.frame_skip
            pbar = tqdm(total=total_frames, desc="Processing", unit="frames")

        try:
            # Process frames
            for frame_id, frame in reader:
                # Validate frame
                if frame is None or not isinstance(frame, np.ndarray):
                    print(f"⚠️  Warning: Invalid frame at frame_id {frame_id}, skipping...")
                    continue

                if frame.size == 0:
                    print(f"⚠️  Warning: Empty frame at frame_id {frame_id}, skipping...")
                    continue

                with self.perf_monitor.measure("total_per_frame"):
                    # 1. Detection
                    with self.perf_monitor.measure("detection"):
                        try:
                            detections = self.detector.detect(frame)
                        except Exception as e:
                            print(f"⚠️  ERROR: Detection failed at frame {frame_id}")
                            print(f"   Frame info: shape={frame.shape}, dtype={frame.dtype}, type={type(frame)}")
                            print(f"   Error: {e}")
                            raise

                    # 2. Tracking
                    with self.perf_monitor.measure("tracking"):
                        tracks = self.tracker.update(detections, frame_id, frame)

                    # 2.5. Add to heatmap (Week 3)
                    if heatmap_gen:
                        for track in tracks:
                            centroid = track["state"].history[-1]["centroid"]
                            heatmap_gen.add_detection(centroid)

                    # 3. Action classification
                    with self.perf_monitor.measure("action_classification"):
                        for track in tracks:
                            action, conf = self.action_classifier.classify(track)
                            track["action"] = action
                            track["action_conf"] = conf

                            # 4. Event generation
                            event_logger.create_event(
                                frame_id, track, action, conf
                            )

                    # 3.5. Fight detection (Week 3)
                    if self.fight_detector and len(tracks) >= 2:
                        with self.perf_monitor.measure("fight_detection"):
                            fight_events = self.fight_detector.detect_fights(
                                tracks, frame_id
                            )
                            # Log fight events
                            for fight in fight_events:
                                event_logger.create_fight_event(
                                    frame_id,
                                    fight["participants"],
                                    fight["confidence"],
                                    metadata={
                                        "iou": fight["iou"],
                                        "velocities": fight["velocities"],
                                        "duration_frames": fight["duration_frames"],
                                    }
                                )

                    # 3.6. Alert generation (Week 3)
                    if alert_gen:
                        with self.perf_monitor.measure("alert_generation"):
                            alert_gen.check_alerts(
                                frame_id,
                                tracks,
                                event_logger.get_events(),
                                fight_events if self.fight_detector and len(tracks) >= 2 else []
                            )

                    # 5. Visualization
                    with self.perf_monitor.measure("visualization"):
                        annotated = draw_annotations(
                            frame,
                            tracks,
                            show_bbox=True,
                            show_id=True,
                            show_action=True,
                        )

                        # Add FPS overlay
                        current_fps = self.perf_monitor.get_fps()
                        annotated = draw_fps(annotated, current_fps)

                    # 6. Write output
                    with self.perf_monitor.measure("video_write"):
                        writer.write(annotated)

                self.perf_monitor.increment_frame()

                if pbar:
                    pbar.update(1)
                    # Update progress bar with current FPS
                    pbar.set_postfix(
                        {"fps": f"{self.perf_monitor.get_fps():.1f}"}
                    )

        except Exception as e:
            print(f"\n❌ Error during processing: {e}")
            raise

        finally:
            # Cleanup
            if pbar:
                pbar.close()
            reader.release()
            writer.release()

        # End performance monitoring
        self.perf_monitor.end_session()

        # Save events
        if events_path:
            event_logger.save_to_json(events_path)

        # Save heatmap (Week 3)
        heatmap_stats = None
        if heatmap_gen and heatmap_path:
            heatmap_gen.save_heatmap(heatmap_path)
            heatmap_stats = heatmap_gen.get_stats()

        # Save alerts (Week 3)
        alert_stats = None
        if alert_gen and alerts_path:
            alert_gen.export_alerts(alerts_path)
            alert_stats = alert_gen.get_summary()

        # Generate results
        results = {
            "input_video": str(input_path),
            "output_video": str(output_path),
            "events_file": str(events_path) if events_path else None,
            "heatmap_file": str(heatmap_path) if heatmap_path else None,
            "alerts_file": str(alerts_path) if alerts_path else None,
            "video_metadata": reader.get_metadata(),
            "events": event_logger.get_events(),
            "event_summary": event_logger.get_summary(),
            "performance": self.perf_monitor.report(),
            "tracker_stats": self.tracker.get_tracker_info(),
            "heatmap_stats": heatmap_stats,
            "alert_stats": alert_stats,
        }

        # Print summary
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """Print processing summary."""
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")

        # Event summary
        summary = results["event_summary"]
        print(f"\nEvents:")
        print(f"  Total: {summary['total_events']}")
        print(f"  Unique Tracks: {summary['unique_tracks']}")
        print(f"  Action Breakdown:")
        for action, count in summary["action_counts"].items():
            print(f"    {action.capitalize()}: {count}")

        # Performance summary
        perf = results["performance"]
        overall = perf["overall"]
        print(f"\nPerformance:")
        print(f"  Frames Processed: {overall['total_frames']}")
        print(f"  Total Time: {overall['total_time_sec']:.2f}s")
        print(f"  Average FPS: {overall['fps']:.2f}")

        # Top bottlenecks
        if perf["components"]:
            print(f"\nComponent Timing:")
            sorted_components = sorted(
                perf["components"].items(),
                key=lambda x: x[1]["mean_ms"],
                reverse=True,
            )
            for name, stats in sorted_components[:3]:
                print(f"  {name}: {stats['mean_ms']:.2f}ms/frame")

        print(f"{'='*60}\n")


# Convenience function for quick testing
def process_video_simple(
    input_path: str,
    output_path: str,
    events_path: Optional[str] = None,
) -> dict:
    """
    Simple wrapper for quick video processing.

    Args:
        input_path: Path to input video
        output_path: Path to output video
        events_path: Path to events JSON (optional)

    Returns:
        Processing results
    """
    pipeline = VideoPipeline()

    return pipeline.process_video(
        Path(input_path),
        Path(output_path),
        Path(events_path) if events_path else None,
    )
