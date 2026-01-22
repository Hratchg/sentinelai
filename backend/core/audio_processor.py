"""
Audio processing for name extraction from speech.

Uses:
- Whisper for speech-to-text transcription
- spaCy for Named Entity Recognition (NER)
"""

import whisper
import spacy
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
import pyaudio
import wave
from collections import deque
import threading
import time

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Audio processor for real-time speech recognition and name extraction.

    Features:
    - Real-time microphone capture
    - Whisper speech-to-text
    - spaCy NER for name extraction
    - Phrase detection ("I'm John", "My name is Sarah")
    """

    def __init__(
        self,
        whisper_model: str = "base",
        language: str = "en"
    ):
        """
        Initialize audio processor.

        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large)
            language: Language for transcription
        """
        self.language = language

        # Load Whisper model
        logger.info(f"Loading Whisper model '{whisper_model}'...")
        self.whisper_model = whisper.load_model(whisper_model)
        logger.info("Whisper model loaded")

        # Load spaCy NER model
        logger.info("Loading spaCy NER model...")
        self.nlp = spacy.load("en_core_web_sm")
        logger.info("spaCy model loaded")

        # Audio recording settings
        self.sample_rate = 16000  # Whisper expects 16kHz
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1

        # Audio buffer
        self.audio_buffer = deque(maxlen=16000 * 10)  # 10 seconds of audio

        # PyAudio instance
        self.pyaudio_instance = None
        self.stream = None
        self.recording = False
        self.record_thread = None

    def start_recording(self):
        """Start recording audio from microphone."""
        if self.recording:
            logger.warning("Already recording")
            return

        try:
            self.pyaudio_instance = pyaudio.PyAudio()

            # Open audio stream
            self.stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            self.recording = True

            # Start recording thread
            self.record_thread = threading.Thread(
                target=self._record_loop,
                daemon=True,
                name="AudioRecorder"
            )
            self.record_thread.start()

            logger.info("Started audio recording")

        except Exception as e:
            logger.error(f"Failed to start audio recording: {e}")

    def _record_loop(self):
        """Continuously record audio."""
        while self.recording:
            try:
                # Read audio chunk
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)

                # Convert to numpy array
                audio_chunk = np.frombuffer(data, dtype=np.int16)

                # Add to buffer
                self.audio_buffer.extend(audio_chunk)

            except Exception as e:
                logger.error(f"Audio recording error: {e}")
                time.sleep(0.1)

    def stop_recording(self):
        """Stop audio recording."""
        if not self.recording:
            return

        self.recording = False

        if self.record_thread:
            self.record_thread.join(timeout=2.0)

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()

        logger.info("Stopped audio recording")

    def transcribe_audio_buffer(self) -> Optional[str]:
        """
        Transcribe current audio buffer using Whisper.

        Returns:
            Transcribed text or None if failed
        """
        if len(self.audio_buffer) == 0:
            return None

        try:
            # Convert buffer to numpy array
            audio_data = np.array(list(self.audio_buffer), dtype=np.float32) / 32768.0

            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                audio_data,
                language=self.language,
                fp16=False
            )

            text = result.get("text", "").strip()

            if text:
                logger.info(f"Transcribed: '{text}'")
                return text

            return None

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

    def extract_person_name(self, text: str) -> Optional[str]:
        """
        Extract person name from transcribed text using spaCy NER.

        Looks for patterns like:
        - "I'm John"
        - "My name is Sarah"
        - "This is Michael"
        - "I am David"

        Args:
            text: Transcribed text

        Returns:
            Extracted name or None
        """
        try:
            # Process with spaCy
            doc = self.nlp(text)

            # Extract PERSON entities
            person_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

            if person_names:
                # Return first person name found
                name = person_names[0]
                logger.info(f"Extracted name: '{name}' from text: '{text}'")
                return name

            # If no NER match, try pattern matching
            name = self._pattern_match_name(text)
            if name:
                logger.info(f"Extracted name (pattern): '{name}' from text: '{text}'")
                return name

            return None

        except Exception as e:
            logger.error(f"Name extraction failed: {e}")
            return None

    def _pattern_match_name(self, text: str) -> Optional[str]:
        """
        Fallback pattern matching for name extraction.

        Args:
            text: Transcribed text

        Returns:
            Extracted name or None
        """
        import re

        text_lower = text.lower()

        # Common patterns
        patterns = [
            r"i'?m\s+([A-Z][a-z]+)",  # "I'm John" or "Im John"
            r"my name is\s+([A-Z][a-z]+)",  # "My name is Sarah"
            r"this is\s+([A-Z][a-z]+)",  # "This is Michael"
            r"i am\s+([A-Z][a-z]+)",  # "I am David"
            r"call me\s+([A-Z][a-z]+)"  # "Call me Alex"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()

        return None

    def process_audio_for_names(
        self,
        duration_seconds: float = 5.0
    ) -> List[Tuple[float, str]]:
        """
        Process recent audio and extract names with timestamps.

        Args:
            duration_seconds: Duration of audio to process

        Returns:
            List of (timestamp, name) tuples
        """
        # Transcribe audio
        transcript = self.transcribe_audio_buffer()

        if not transcript:
            return []

        # Extract names
        name = self.extract_person_name(transcript)

        if name:
            current_time = time.time()
            return [(current_time, name)]

        return []

    def clear_buffer(self):
        """Clear audio buffer."""
        self.audio_buffer.clear()
        logger.info("Cleared audio buffer")

    def __del__(self):
        """Cleanup on deletion."""
        self.stop_recording()
