"""
YOLOv8 Person Detector.
Wraps Ultralytics YOLO for person-only detection with performance optimizations.
"""

import numpy as np
import torch
from ultralytics import YOLO

from backend.config import settings


class YOLOv8Detector:
    """
    YOLOv8-based person detector with optimizations.

    Features:
    - Person-only detection (class 0)
    - FP16 inference (if GPU available)
    - Confidence & NMS filtering
    - Batch processing support
    """

    def __init__(
        self,
        model_path: str = None,
        conf_threshold: float = None,
        iou_threshold: float = None,
        device: str = None,
        fp16: bool = None,
    ):
        """
        Initialize YOLOv8 detector.

        Args:
            model_path: Path to YOLO weights (default: yolov8n.pt)
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
            device: 'cuda' or 'cpu'
            fp16: Use half precision (FP16)
        """
        self.model_path = model_path or settings.DETECTOR_MODEL
        self.conf_threshold = conf_threshold or settings.DETECTOR_CONFIDENCE
        self.iou_threshold = iou_threshold or settings.DETECTOR_IOU
        self.device = device or settings.DETECTOR_DEVICE
        self.fp16 = fp16 if fp16 is not None else settings.DETECTOR_FP16

        # Load model
        print(f"Loading detector: {self.model_path} on {self.device}")
        self.model = YOLO(self.model_path)
        self.model.to(self.device)

        # Optimize model
        if hasattr(self.model, "fuse"):
            self.model.fuse()

        # Warmup
        self._warmup()

        print(f"✓ Detector ready (FP16: {self.fp16})")

    def _warmup(self):
        """Warmup model with dummy input."""
        dummy_input = np.zeros((640, 640, 3), dtype=np.uint8)
        try:
            self.detect(dummy_input)
            print("✓ Detector warmup complete")
        except Exception as e:
            print(f"⚠️  Warmup failed: {e}")

    def detect(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect persons in a frame.

        Args:
            frame: Input image (H, W, 3) in BGR format

        Returns:
            detections: Nx6 array of [x1, y1, x2, y2, conf, cls]
        """
        # Run inference
        results = self.model(
            frame,
            classes=[0],  # Person class only
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            half=self.fp16,
            verbose=False,
            device=self.device,
        )[0]

        # Extract boxes
        detections = []
        if results.boxes is not None and len(results.boxes) > 0:
            for box in results.boxes:
                # Get coordinates and confidence
                xyxy = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().item()
                cls = 0.0  # Person class (always 0 since we filter for person only)

                # Format: [x1, y1, x2, y2, conf, cls] (required by ByteTrack)
                detections.append([*xyxy, conf, cls])

        return np.array(detections, dtype=np.float32)

    def detect_batch(self, frames: list[np.ndarray]) -> list[np.ndarray]:
        """
        Batch detection for multiple frames.

        Args:
            frames: List of input images

        Returns:
            List of detection arrays
        """
        # Run batch inference
        results = self.model(
            frames,
            classes=[0],
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            half=self.fp16,
            verbose=False,
            device=self.device,
        )

        # Extract detections for each frame
        all_detections = []
        for result in results:
            detections = []
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().item()
                    cls = 0.0  # Person class
                    detections.append([*xyxy, conf, cls])

            all_detections.append(np.array(detections, dtype=np.float32))

        return all_detections

    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model_path": self.model_path,
            "device": self.device,
            "fp16": self.fp16,
            "conf_threshold": self.conf_threshold,
            "iou_threshold": self.iou_threshold,
        }
