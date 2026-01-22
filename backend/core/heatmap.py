"""
Heatmap Generation Module.

Generates activity heatmaps showing where people spend time in the scene.
"""

from pathlib import Path
from typing import Tuple

import cv2
import numpy as np

from backend.config import settings


class HeatmapGenerator:
    """
    Generate activity heatmaps from detection centroids.

    Features:
    - Grid-based accumulation (configurable cell size)
    - Gaussian blur for smooth visualization
    - Multiple colormap options (JET, HOT, etc.)
    - Overlay blending with video frames
    - Standalone heatmap export
    """

    def __init__(
        self,
        frame_size: Tuple[int, int],
        cell_size: int = None,
        colormap: str = None,
        alpha: float = None,
    ):
        """
        Initialize heatmap generator.

        Args:
            frame_size: (width, height) of video frames
            cell_size: Grid cell size in pixels (default from config)
            colormap: OpenCV colormap name (default: JET)
            alpha: Overlay transparency 0-1 (default: 0.4)
        """
        self.frame_width, self.frame_height = frame_size
        self.cell_size = cell_size or settings.HEATMAP_CELL_SIZE
        self.alpha = alpha if alpha is not None else settings.HEATMAP_ALPHA

        # Get colormap
        colormap_name = colormap or settings.HEATMAP_COLORMAP
        self.colormap = self._get_colormap(colormap_name)

        # Initialize heatmap grid
        self.grid_w = self.frame_width // self.cell_size
        self.grid_h = self.frame_height // self.cell_size
        self.heatmap = np.zeros((self.grid_h, self.grid_w), dtype=np.float32)

        self.total_detections = 0

    def add_detection(self, centroid: Tuple[float, float]):
        """
        Add a detection centroid to the heatmap.

        Args:
            centroid: (x, y) position in pixels
        """
        x, y = centroid

        # Convert to grid coordinates
        cell_x = int(x // self.cell_size)
        cell_y = int(y // self.cell_size)

        # Bounds check
        if 0 <= cell_x < self.grid_w and 0 <= cell_y < self.grid_h:
            self.heatmap[cell_y, cell_x] += 1.0
            self.total_detections += 1

    def add_detections_batch(self, centroids: list):
        """
        Add multiple detections at once.

        Args:
            centroids: List of (x, y) tuples
        """
        for centroid in centroids:
            self.add_detection(centroid)

    def render_heatmap(self, apply_blur: bool = True) -> np.ndarray:
        """
        Render heatmap as a colored image.

        Args:
            apply_blur: Apply Gaussian blur for smoothing

        Returns:
            Heatmap image (H, W, 3) in BGR format
        """
        if self.total_detections == 0:
            # Empty heatmap
            return np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)

        # Normalize to 0-255
        heatmap_normalized = cv2.normalize(
            self.heatmap, None, 0, 255, cv2.NORM_MINMAX
        )
        heatmap_u8 = heatmap_normalized.astype(np.uint8)

        # Apply Gaussian blur
        if apply_blur:
            kernel_size = max(3, self.cell_size // 4)
            if kernel_size % 2 == 0:
                kernel_size += 1  # Must be odd
            heatmap_u8 = cv2.GaussianBlur(
                heatmap_u8, (kernel_size, kernel_size), 0
            )

        # Upsample to frame size
        heatmap_upsampled = cv2.resize(
            heatmap_u8,
            (self.frame_width, self.frame_height),
            interpolation=cv2.INTER_LINEAR,
        )

        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_upsampled, self.colormap)

        return heatmap_colored

    def overlay_on_frame(
        self, frame: np.ndarray, alpha: float = None
    ) -> np.ndarray:
        """
        Overlay heatmap on a video frame.

        Args:
            frame: Input frame (H, W, 3) in BGR
            alpha: Overlay alpha (default: self.alpha)

        Returns:
            Frame with heatmap overlay
        """
        if alpha is None:
            alpha = self.alpha

        heatmap_colored = self.render_heatmap()

        # Blend with original frame
        blended = cv2.addWeighted(
            frame, 1.0 - alpha, heatmap_colored, alpha, 0
        )

        return blended

    def save_heatmap(self, output_path: Path):
        """
        Save standalone heatmap image.

        Args:
            output_path: Path to save PNG/JPG
        """
        heatmap_colored = self.render_heatmap()
        cv2.imwrite(str(output_path), heatmap_colored)
        print(f"✓ Heatmap saved to {output_path}")

    def get_stats(self) -> dict:
        """
        Get heatmap statistics.

        Returns:
            Statistics dict
        """
        active_cells = int(np.count_nonzero(self.heatmap))
        return {
            "total_detections": self.total_detections,
            "active_cells": active_cells,
            "grid_size": (self.grid_w, self.grid_h),
            "cell_size": self.cell_size,
            "max_density": float(np.max(self.heatmap)),
            "mean_density": float(np.mean(self.heatmap)),
        }

    def get_hotspots(self, threshold_percentile: float = 90) -> list:
        """
        Get hotspot locations (high-activity areas).

        Args:
            threshold_percentile: Percentile threshold for hotspots (0-100)

        Returns:
            List of hotspot (x, y) coordinates in pixel space
        """
        if self.total_detections == 0:
            return []

        threshold = np.percentile(self.heatmap, threshold_percentile)
        hotspot_cells = np.argwhere(self.heatmap >= threshold)

        # Convert grid coordinates to pixel coordinates (cell centers)
        hotspots = []
        for cell_y, cell_x in hotspot_cells:
            pixel_x = (cell_x + 0.5) * self.cell_size
            pixel_y = (cell_y + 0.5) * self.cell_size
            hotspots.append((int(pixel_x), int(pixel_y)))

        return hotspots

    def reset(self):
        """Reset heatmap data."""
        self.heatmap = np.zeros((self.grid_h, self.grid_w), dtype=np.float32)
        self.total_detections = 0

    def _get_colormap(self, colormap_name: str) -> int:
        """
        Get OpenCV colormap constant.

        Args:
            colormap_name: Colormap name (JET, HOT, etc.)

        Returns:
            OpenCV colormap constant
        """
        colormap_dict = {
            "JET": cv2.COLORMAP_JET,
            "HOT": cv2.COLORMAP_HOT,
            "VIRIDIS": cv2.COLORMAP_VIRIDIS,
            "PLASMA": cv2.COLORMAP_PLASMA,
            "INFERNO": cv2.COLORMAP_INFERNO,
            "MAGMA": cv2.COLORMAP_MAGMA,
            "TURBO": cv2.COLORMAP_TURBO,
            "RAINBOW": cv2.COLORMAP_RAINBOW,
        }

        return colormap_dict.get(
            colormap_name.upper(), cv2.COLORMAP_JET
        )
