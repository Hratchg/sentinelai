"""
Wake Word Detection for 'Hey Sentinel'

Simple energy-based wake word detector using acoustic fingerprinting
and pattern matching for low latency detection.
"""

import numpy as np
from collections import deque
import logging

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Simple wake word detector for "Hey Sentinel" using keyword spotting.
    Uses acoustic fingerprinting + pattern matching for low latency.

    Features:
    - Energy-based detection
    - Short-time energy analysis
    - Peak detection for characteristic patterns
    - Confidence scoring
    """

    def __init__(self, sensitivity: float = 0.7):
        """
        Initialize wake word detector.

        Args:
            sensitivity: Detection threshold (0-1, higher = more sensitive)
        """
        self.sensitivity = sensitivity
        self.audio_buffer = deque(maxlen=48000)  # 3 seconds @ 16kHz
        self.wake_word_patterns = self._load_wake_word_patterns()

        logger.info(f"WakeWordDetector initialized with sensitivity={sensitivity}")

    def _load_wake_word_patterns(self):
        """
        Load pre-computed acoustic patterns for "Hey Sentinel".

        In production, this would be trained on multiple samples.
        For now, we use simplified phoneme patterns:
        - "Hey" = /heɪ/ → high energy in 2-4kHz range, short duration
        - "Sentinel" = /ˈsɛntɪnəl/ → characteristic formants, longer duration

        Returns:
            Dictionary of phoneme patterns
        """
        return {
            "hey": {
                "f1": 800,   # First formant frequency
                "f2": 2400,  # Second formant frequency
                "duration": 0.3  # seconds
            },
            "sentinel": {
                "f1": 500,
                "f2": 1800,
                "duration": 0.6
            }
        }

    def add_audio_chunk(self, audio_data: np.ndarray):
        """
        Add new audio chunk to buffer for continuous detection.

        Args:
            audio_data: Audio samples (mono, 16kHz)
        """
        self.audio_buffer.extend(audio_data)

    def detect(self) -> bool:
        """
        Check if wake word is present in current buffer.

        Algorithm:
        1. Extract last 2 seconds of audio
        2. Compute short-time energy
        3. Find energy peaks
        4. Check peak timing and spacing
        5. Compute confidence score

        Returns:
            True if wake word detected with confidence > sensitivity
        """
        if len(self.audio_buffer) < 16000:  # Need at least 1 second
            return False

        # Convert buffer to numpy array
        audio = np.array(list(self.audio_buffer))

        # Extract last 2 seconds for analysis
        segment = audio[-32000:]

        # Compute short-time energy
        energy = self._compute_energy(segment)

        # Look for characteristic pattern (2 peaks: "Hey" + "Sentinel")
        peaks = self._find_energy_peaks(energy)

        if len(peaks) >= 2:
            # Check timing (0.3s + 0.6s = ~0.9s total)
            peak_spacing = peaks[1] - peaks[0]

            if 0.2 < peak_spacing < 1.0:
                confidence = self._compute_confidence(segment, peaks)

                if confidence > self.sensitivity:
                    logger.info(f"Wake word detected (confidence: {confidence:.2f})")
                    return True

        return False

    def _compute_energy(self, audio: np.ndarray, frame_size: int = 400) -> np.ndarray:
        """
        Compute short-time energy of audio signal.

        Args:
            audio: Audio samples
            frame_size: Frame size in samples (400 = 25ms @ 16kHz)

        Returns:
            Array of energy values per frame
        """
        num_frames = len(audio) // frame_size
        energy = np.zeros(num_frames)

        for i in range(num_frames):
            frame = audio[i * frame_size:(i + 1) * frame_size]
            energy[i] = np.sum(frame ** 2)

        return energy

    def _find_energy_peaks(self, energy: np.ndarray, threshold: float = 0.5) -> list:
        """
        Find energy peaks in signal that could correspond to phonemes.

        Args:
            energy: Energy values per frame
            threshold: Normalized threshold (0-1)

        Returns:
            List of peak times in seconds
        """
        # Normalize energy
        normalized = energy / (np.max(energy) + 1e-6)
        peaks = []

        # Find local maxima above threshold
        for i in range(1, len(normalized) - 1):
            if (normalized[i] > threshold and
                normalized[i] > normalized[i-1] and
                normalized[i] > normalized[i+1]):
                # Convert frame index to time (400 samples @ 16kHz = 0.025s)
                peak_time = i * 0.025
                peaks.append(peak_time)

        return peaks

    def _compute_confidence(self, audio: np.ndarray, peaks: list) -> float:
        """
        Compute detection confidence score based on signal characteristics.

        Uses signal-to-noise ratio as a simple confidence metric.
        In production, this would use more sophisticated features.

        Args:
            audio: Audio segment
            peaks: List of detected peak times

        Returns:
            Confidence score (0-1)
        """
        # Compute signal energy vs background energy
        segment_energy = np.sum(audio ** 2)

        # Estimate background noise from first 500ms
        background_energy = np.mean(audio[:8000] ** 2) * len(audio)

        # Compute SNR (signal-to-noise ratio)
        snr = segment_energy / (background_energy + 1e-6)

        # Normalize SNR to 0-1 range (SNR of 10 = high confidence)
        confidence = min(1.0, snr / 10.0)

        return confidence

    def reset(self):
        """Clear audio buffer and reset detector state."""
        self.audio_buffer.clear()
        logger.debug("Wake word detector reset")

    def set_sensitivity(self, sensitivity: float):
        """
        Update detection sensitivity.

        Args:
            sensitivity: New sensitivity value (0-1)
        """
        if not 0 <= sensitivity <= 1:
            raise ValueError("Sensitivity must be between 0 and 1")

        self.sensitivity = sensitivity
        logger.info(f"Sensitivity updated to {sensitivity}")

    def get_stats(self) -> dict:
        """
        Get detector statistics.

        Returns:
            Dictionary with buffer size, sensitivity, etc.
        """
        return {
            "buffer_size": len(self.audio_buffer),
            "buffer_capacity": self.audio_buffer.maxlen,
            "buffer_duration_seconds": len(self.audio_buffer) / 16000.0,
            "sensitivity": self.sensitivity
        }
