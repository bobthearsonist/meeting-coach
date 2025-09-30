"""
Audio capture from BlackHole virtual audio device
"""
import pyaudio
import numpy as np
import wave
from typing import Generator, Optional
import config


class AudioCapture:
    def __init__(self, device_index: Optional[int] = None, use_microphone: bool = False):
        """
        Initialize audio capture from BlackHole device or microphone.

        Args:
            device_index: Specific device index, or None to auto-detect
            use_microphone: If True, use default microphone instead of BlackHole
        """
        self.audio = pyaudio.PyAudio()
        self.use_microphone = use_microphone

        if use_microphone:
            self.device_index = device_index or self._find_microphone_device()
            if self.device_index is None:
                raise RuntimeError("No suitable microphone found.")
        else:
            self.device_index = device_index or self._find_blackhole_device()
            if self.device_index is None:
                raise RuntimeError("BlackHole device not found. Please install BlackHole and configure audio routing.")

        self.stream = None
        self.sample_rate = config.SAMPLE_RATE
        self.chunk_size = config.CHUNK_SIZE
        print(f"Using audio device: {self.get_device_name(self.device_index)}")

    def _find_blackhole_device(self) -> Optional[int]:
        """Auto-detect BlackHole device index."""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            name = device_info['name'].lower()
            if 'blackhole' in name and device_info['maxInputChannels'] > 0:
                return i
        return None

    def _find_microphone_device(self) -> Optional[int]:
        """Auto-detect a suitable microphone device."""
        # Priority order for microphone detection
        preferred_mics = ['macbook pro microphone', 'built-in microphone', 'blue snowball', 'yeti']

        # First, try to find preferred microphones
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            name = device_info['name'].lower()
            if device_info['maxInputChannels'] > 0:
                for preferred in preferred_mics:
                    if preferred in name:
                        return i

        # Fallback: find any device with input channels
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0 and 'blackhole' not in device_info['name'].lower():
                return i

        return None

    def get_device_name(self, index: int) -> str:
        """Get device name by index."""
        return self.audio.get_device_info_by_index(index)['name']

    def list_devices(self):
        """Print all available audio devices."""
        print("\nAvailable Audio Devices:")
        print("-" * 60)
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            print(f"{i}: {info['name']}")
            print(f"   Input Channels: {info['maxInputChannels']}")
            print(f"   Output Channels: {info['maxOutputChannels']}")
            print(f"   Sample Rate: {info['defaultSampleRate']}")
            print()

    def get_audio_format(self):
        """Get the audio format used for capture."""
        return pyaudio.paInt16

    def start_capture(self) -> None:
        """Start the audio capture stream."""
        if self.stream is not None:
            return

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=1024
        )
        print("Audio capture started")

    def stop_capture(self) -> None:
        """Stop the audio capture stream."""
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            print("Audio capture stopped")

    def read_chunk(self, duration: float) -> np.ndarray:
        """
        Read audio chunk of specified duration.

        Args:
            duration: Duration in seconds

        Returns:
            numpy array of audio samples
        """
        if self.stream is None:
            raise RuntimeError("Stream not started. Call start_capture() first.")

        frames_to_read = int(config.SAMPLE_RATE * duration)
        audio_data = []

        for _ in range(0, frames_to_read, 1024):
            data = self.stream.read(1024, exception_on_overflow=False)
            audio_data.append(data)

        # Convert to numpy array
        audio_bytes = b''.join(audio_data)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # Convert to float32 and normalize for Whisper
        audio_float = audio_array.astype(np.float32) / 32768.0

        # If stereo, convert to mono by averaging channels
        if config.CHANNELS == 2:
            audio_float = audio_float.reshape(-1, 2).mean(axis=1)

        return audio_float

    def capture_stream(self, chunk_duration: float) -> Generator[np.ndarray, None, None]:
        """
        Generator that yields audio chunks continuously.

        Args:
            chunk_duration: Duration of each chunk in seconds

        Yields:
            numpy arrays of audio samples
        """
        self.start_capture()
        try:
            while True:
                yield self.read_chunk(chunk_duration)
        except KeyboardInterrupt:
            print("\nStopping audio capture...")
        finally:
            self.stop_capture()

    def save_chunk_to_wav(self, audio_data: np.ndarray, filename: str):
        """Save audio chunk to WAV file (for debugging)."""
        # Convert back to int16
        audio_int16 = (audio_data * 32768).astype(np.int16)

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)  # Mono after conversion
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(config.SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        print(f"Saved audio to {filename}")

    def __del__(self):
        """Cleanup."""
        try:
            self.stop_capture()
            if hasattr(self, 'audio'):
                self.audio.terminate()
        except (AttributeError, Exception):
            # Ignore cleanup errors during destruction
            pass


if __name__ == "__main__":
    # Test the audio capture
    capture = AudioCapture()
    capture.list_devices()

    print("\nCapturing 5 seconds of audio...")
    capture.start_capture()
    audio = capture.read_chunk(5.0)
    capture.stop_capture()

    print(f"Captured audio shape: {audio.shape}")
    print(f"Audio duration: {len(audio) / config.SAMPLE_RATE:.2f} seconds")
    print(f"Audio level (RMS): {np.sqrt(np.mean(audio**2)):.4f}")

    # Save for testing
    capture.save_chunk_to_wav(audio, "test_capture.wav")
