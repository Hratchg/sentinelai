"""
Performance monitoring utilities.
Tracks FPS, latency, and component-wise timing.
"""

import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Dict

import numpy as np


class PerformanceMonitor:
    """
    Performance monitoring for video processing pipeline.

    Features:
    - Context manager for easy timing
    - Per-component statistics (mean, p50, p95)
    - FPS calculation
    - Report generation
    """

    def __init__(self):
        """Initialize performance monitor."""
        self.timers: Dict[str, list] = defaultdict(list)
        self.frame_count = 0
        self.start_time = None
        self.end_time = None

    @contextmanager
    def measure(self, name: str):
        """
        Context manager for timing a code block.

        Usage:
            with perf_monitor.measure('detection'):
                detections = detector.detect(frame)

        Args:
            name: Name of the operation being timed
        """
        start = time.perf_counter()
        yield
        elapsed = time.perf_counter() - start
        self.timers[name].append(elapsed)

    def start_session(self):
        """Start a timing session."""
        self.start_time = time.perf_counter()

    def end_session(self):
        """End the timing session."""
        self.end_time = time.perf_counter()

    def increment_frame(self):
        """Increment frame counter."""
        self.frame_count += 1

    def get_fps(self) -> float:
        """
        Calculate overall FPS.

        Returns:
            Frames per second
        """
        if self.start_time is None or self.end_time is None:
            return 0.0

        elapsed = self.end_time - self.start_time
        return self.frame_count / elapsed if elapsed > 0 else 0.0

    def report(self) -> dict:
        """
        Generate performance report.

        Returns:
            Dict with timing statistics for each component
        """
        report = {
            "overall": {
                "total_frames": self.frame_count,
                "total_time_sec": (
                    self.end_time - self.start_time
                    if self.start_time and self.end_time
                    else 0.0
                ),
                "fps": self.get_fps(),
            },
            "components": {},
        }

        for name, times in self.timers.items():
            if not times:
                continue

            times_array = np.array(times)
            report["components"][name] = {
                "count": len(times),
                "mean_ms": float(np.mean(times_array) * 1000),
                "median_ms": float(np.median(times_array) * 1000),
                "p95_ms": float(np.percentile(times_array, 95) * 1000),
                "p99_ms": float(np.percentile(times_array, 99) * 1000),
                "min_ms": float(np.min(times_array) * 1000),
                "max_ms": float(np.max(times_array) * 1000),
                "fps": 1 / np.mean(times_array) if np.mean(times_array) > 0 else 0,
            }

        return report

    def print_report(self):
        """Print formatted performance report."""
        report = self.report()

        print("\n" + "=" * 60)
        print("PERFORMANCE REPORT")
        print("=" * 60)

        # Overall stats
        overall = report["overall"]
        print(f"\nOverall:")
        print(f"  Total Frames: {overall['total_frames']}")
        print(f"  Total Time: {overall['total_time_sec']:.2f}s")
        print(f"  FPS: {overall['fps']:.2f}")

        # Component stats
        print(f"\nComponent Timing:")
        print(f"{'Component':<20} {'Mean':<10} {'P95':<10} {'FPS':<10}")
        print("-" * 60)

        for name, stats in report["components"].items():
            print(
                f"{name:<20} {stats['mean_ms']:>8.2f}ms "
                f"{stats['p95_ms']:>8.2f}ms {stats['fps']:>8.1f}"
            )

        print("=" * 60 + "\n")

    def reset(self):
        """Reset all counters and timers."""
        self.timers.clear()
        self.frame_count = 0
        self.start_time = None
        self.end_time = None


class FPSCounter:
    """
    Simple FPS counter for real-time display.

    Uses moving average over recent frames.
    """

    def __init__(self, window_size: int = 30):
        """
        Initialize FPS counter.

        Args:
            window_size: Number of frames to average over
        """
        self.window_size = window_size
        self.frame_times = []
        self.last_time = time.perf_counter()

    def update(self) -> float:
        """
        Update FPS counter with new frame.

        Returns:
            Current FPS estimate
        """
        current_time = time.perf_counter()
        elapsed = current_time - self.last_time
        self.last_time = current_time

        self.frame_times.append(elapsed)

        # Keep only recent frames
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)

        # Calculate FPS
        if len(self.frame_times) > 0:
            avg_time = np.mean(self.frame_times)
            return 1.0 / avg_time if avg_time > 0 else 0.0

        return 0.0

    def get_fps(self) -> float:
        """Get current FPS estimate."""
        if len(self.frame_times) > 0:
            avg_time = np.mean(self.frame_times)
            return 1.0 / avg_time if avg_time > 0 else 0.0
        return 0.0
