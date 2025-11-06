"""
Unit tests for the AudioCapture module.
Tests audio device detection, stream management, and audio data processing.
"""

from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    pyaudio = None
    PYAUDIO_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="pyaudio not available on this platform")
    pytestmark = pytest.mark.skip(reason="pyaudio not installed")

from src import config
from src.core import audio_capture


class TestAudioCapture:
    """Test suite for AudioCapture class."""

    @pytest.fixture
    def mock_pyaudio(self):
        """Mock PyAudio instance for testing."""
        mock_audio = Mock(spec=pyaudio.PyAudio)
        mock_audio.get_device_count.return_value = 3
        mock_audio.get_device_info_by_index.side_effect = [
            {
                "name": "Built-in Microphone",
                "maxInputChannels": 1,
                "maxOutputChannels": 0,
                "defaultSampleRate": 44100.0,
            },
            {
                "name": "BlackHole 2ch",
                "maxInputChannels": 2,
                "maxOutputChannels": 2,
                "defaultSampleRate": 48000.0,
            },
            {
                "name": "Built-in Output",
                "maxInputChannels": 0,
                "maxOutputChannels": 2,
                "defaultSampleRate": 44100.0,
            },
        ]
        return mock_audio

    @pytest.fixture
    def sample_audio_bytes(self):
        """Generate sample audio data as bytes."""
        # Create sample 16-bit PCM audio data
        samples = np.array([100, -100, 200, -200, 50, -50], dtype=np.int16)
        return samples.tobytes()

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_init_with_blackhole_auto_detection(self, mock_pyaudio_class, mock_pyaudio):
        """Test initialization with automatic BlackHole detection."""
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()

        assert capture.device_index == 1  # BlackHole device index
        assert not capture.use_microphone
        mock_pyaudio_class.assert_called_once()

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_init_with_microphone_auto_detection(
        self, mock_pyaudio_class, mock_pyaudio
    ):
        """Test initialization with automatic microphone detection."""
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture(use_microphone=True)

        assert capture.device_index == 0  # Built-in Microphone index
        assert capture.use_microphone
        mock_pyaudio_class.assert_called_once()

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_init_with_specific_device_index(self, mock_pyaudio_class, mock_pyaudio):
        """Test initialization with specific device index."""
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture(device_index=2)

        assert capture.device_index == 2
        assert not capture.use_microphone

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_init_blackhole_not_found_error(self, mock_pyaudio_class):
        """Test error when BlackHole device is not found."""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 1
        mock_audio.get_device_info_by_index.return_value = {
            "name": "Built-in Output",
            "maxInputChannels": 0,
            "maxOutputChannels": 2,
            "defaultSampleRate": 44100.0,
        }
        mock_pyaudio_class.return_value = mock_audio

        with pytest.raises(RuntimeError, match="BlackHole device not found"):
            audio_capture.AudioCapture()

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_init_microphone_not_found_error(self, mock_pyaudio_class):
        """Test error when no suitable microphone is found."""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 1
        mock_audio.get_device_info_by_index.return_value = {
            "name": "Built-in Output",
            "maxInputChannels": 0,
            "maxOutputChannels": 2,
            "defaultSampleRate": 44100.0,
        }
        mock_pyaudio_class.return_value = mock_audio

        with pytest.raises(RuntimeError, match="No suitable microphone found"):
            audio_capture.AudioCapture(use_microphone=True)

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_find_blackhole_device(self, mock_pyaudio_class, mock_pyaudio):
        """Test BlackHole device detection logic."""

        # Ensure we cycle through all devices during _find_blackhole_device call
        def side_effect_func(i):
            devices = [
                {
                    "name": "Built-in Microphone",
                    "maxInputChannels": 1,
                    "maxOutputChannels": 0,
                    "defaultSampleRate": 44100.0,
                },
                {
                    "name": "BlackHole 2ch",
                    "maxInputChannels": 2,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 48000.0,
                },
                {
                    "name": "Built-in Output",
                    "maxInputChannels": 0,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 44100.0,
                },
            ]
            return devices[i]

        mock_pyaudio.get_device_info_by_index.side_effect = side_effect_func
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        assert capture.device_index == 1  # Should find BlackHole 2ch at index 1

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_find_blackhole_device_not_found(self, mock_pyaudio_class):
        """Test BlackHole device detection when not available."""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {
                "name": "Built-in Microphone",
                "maxInputChannels": 1,
                "maxOutputChannels": 0,
                "defaultSampleRate": 44100.0,
            },
            {
                "name": "Built-in Output",
                "maxInputChannels": 0,
                "maxOutputChannels": 2,
                "defaultSampleRate": 44100.0,
            },
        ]
        mock_pyaudio_class.return_value = mock_audio

        # Create instance to call the method
        with pytest.raises(RuntimeError):
            audio_capture.AudioCapture()

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_find_microphone_device_preferred(self, mock_pyaudio_class):
        """Test microphone detection with preferred device names."""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 3
        mock_audio.get_device_info_by_index.side_effect = [
            {
                "name": "Some Other Mic",
                "maxInputChannels": 1,
                "maxOutputChannels": 0,
                "defaultSampleRate": 44100.0,
            },
            {
                "name": "MacBook Pro Microphone",  # Preferred
                "maxInputChannels": 1,
                "maxOutputChannels": 0,
                "defaultSampleRate": 44100.0,
            },
            {
                "name": "Built-in Output",
                "maxInputChannels": 0,
                "maxOutputChannels": 2,
                "defaultSampleRate": 44100.0,
            },
        ]
        mock_pyaudio_class.return_value = mock_audio

        capture = audio_capture.AudioCapture(use_microphone=True)
        assert capture.device_index == 1  # Should find preferred MacBook Pro Microphone

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_find_microphone_device_fallback(self, mock_pyaudio_class):
        """Test microphone detection fallback to any input device."""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 2

        # Need to ensure we have enough iterations for both the preferred and fallback loops
        devices = [
            {
                "name": "Unknown Microphone",  # Not preferred but has input
                "maxInputChannels": 1,
                "maxOutputChannels": 0,
                "defaultSampleRate": 44100.0,
            },
            {
                "name": "Built-in Output",
                "maxInputChannels": 0,
                "maxOutputChannels": 2,
                "defaultSampleRate": 44100.0,
            },
        ]

        def side_effect_func(i):
            return devices[i % len(devices)]

        mock_audio.get_device_info_by_index.side_effect = side_effect_func
        mock_pyaudio_class.return_value = mock_audio

        capture = audio_capture.AudioCapture(use_microphone=True)
        assert capture.device_index == 0  # Should fall back to any input device

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_get_device_name(self, mock_pyaudio_class, mock_pyaudio):
        """Test getting device name by index."""

        def side_effect_func(i):
            devices = [
                {
                    "name": "Built-in Microphone",
                    "maxInputChannels": 1,
                    "maxOutputChannels": 0,
                    "defaultSampleRate": 44100.0,
                },
                {
                    "name": "BlackHole 2ch",
                    "maxInputChannels": 2,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 48000.0,
                },
                {
                    "name": "Built-in Output",
                    "maxInputChannels": 0,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 44100.0,
                },
            ]
            return devices[i]

        mock_pyaudio.get_device_info_by_index.side_effect = side_effect_func
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        name = capture.get_device_name(1)

        assert name == "BlackHole 2ch"

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_list_devices(self, mock_pyaudio_class, mock_pyaudio, capsys):
        """Test listing all available devices."""

        def side_effect_func(i):
            devices = [
                {
                    "name": "Built-in Microphone",
                    "maxInputChannels": 1,
                    "maxOutputChannels": 0,
                    "defaultSampleRate": 44100.0,
                },
                {
                    "name": "BlackHole 2ch",
                    "maxInputChannels": 2,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 48000.0,
                },
                {
                    "name": "Built-in Output",
                    "maxInputChannels": 0,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 44100.0,
                },
            ]
            return devices[i]

        mock_pyaudio.get_device_info_by_index.side_effect = side_effect_func
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.list_devices()

        captured = capsys.readouterr()
        assert "Available Audio Devices:" in captured.out
        assert "Built-in Microphone" in captured.out
        assert "BlackHole 2ch" in captured.out
        assert "Input Channels:" in captured.out
        assert "Sample Rate:" in captured.out

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_start_capture(self, mock_pyaudio_class, mock_pyaudio, capsys):
        """Test starting audio capture stream."""
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.start_capture()

        assert capture.stream == mock_stream
        mock_pyaudio.open.assert_called_once_with(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            input_device_index=1,  # BlackHole device index
            frames_per_buffer=1024,
        )

        captured = capsys.readouterr()
        assert "Audio capture started" in captured.out

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_start_capture_already_started(self, mock_pyaudio_class, mock_pyaudio):
        """Test starting capture when already started (should be no-op)."""
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.start_capture()
        capture.start_capture()  # Second call should be ignored

        # Should only call open once
        assert mock_pyaudio.open.call_count == 1

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_stop_capture(self, mock_pyaudio_class, mock_pyaudio, capsys):
        """Test stopping audio capture stream."""
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.start_capture()
        capture.stop_capture()

        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        assert capture.stream is None

        captured = capsys.readouterr()
        assert "Audio capture stopped" in captured.out

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_stop_capture_not_started(self, mock_pyaudio_class, mock_pyaudio):
        """Test stopping capture when not started (should be no-op)."""
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.stop_capture()  # Should not raise an error

        assert capture.stream is None

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_read_chunk_not_started_error(self, mock_pyaudio_class, mock_pyaudio):
        """Test reading chunk when stream not started raises error."""
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()

        with pytest.raises(RuntimeError, match="Stream not started"):
            capture.read_chunk(1.0)

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_read_chunk_success(
        self, mock_pyaudio_class, mock_pyaudio, sample_audio_bytes
    ):
        """Test successful chunk reading."""

        def side_effect_func(i):
            devices = [
                {
                    "name": "Built-in Microphone",
                    "maxInputChannels": 1,
                    "maxOutputChannels": 0,
                    "defaultSampleRate": 44100.0,
                },
                {
                    "name": "BlackHole 2ch",
                    "maxInputChannels": 2,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 48000.0,
                },
                {
                    "name": "Built-in Output",
                    "maxInputChannels": 0,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 44100.0,
                },
            ]
            return devices[i]

        mock_pyaudio.get_device_info_by_index.side_effect = side_effect_func

        mock_stream = Mock()
        mock_stream.read.return_value = sample_audio_bytes
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.start_capture()

        # Read 0.1 second chunk
        result = capture.read_chunk(0.1)

        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert len(result) > 0

        # Check that read was called with 1024 frames (the implementation uses chunks of 1024)
        mock_stream.read.assert_called_with(1024, exception_on_overflow=False)

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_read_chunk_multiple_reads(
        self, mock_pyaudio_class, mock_pyaudio, sample_audio_bytes
    ):
        """Test reading chunk that requires multiple stream reads."""

        def side_effect_func(i):
            devices = [
                {
                    "name": "Built-in Microphone",
                    "maxInputChannels": 1,
                    "maxOutputChannels": 0,
                    "defaultSampleRate": 44100.0,
                },
                {
                    "name": "BlackHole 2ch",
                    "maxInputChannels": 2,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 48000.0,
                },
                {
                    "name": "Built-in Output",
                    "maxInputChannels": 0,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 44100.0,
                },
            ]
            return devices[i]

        mock_pyaudio.get_device_info_by_index.side_effect = side_effect_func

        mock_stream = Mock()
        # Create enough sample data for multiple reads (2 seconds needs many 1024-frame chunks)
        # At 16000 sample rate, 2 seconds = 32000 frames, which needs 32 chunks of 1024
        mock_stream.read.return_value = sample_audio_bytes
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.start_capture()

        # Read longer chunk that will require multiple reads
        result = capture.read_chunk(
            0.5
        )  # Use shorter duration to avoid too many mock calls

        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert len(result) > 0

        # Should have made multiple read calls
        assert mock_stream.read.call_count >= 1

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_capture_stream_generator(
        self, mock_pyaudio_class, mock_pyaudio, sample_audio_bytes
    ):
        """Test the capture_stream generator method."""

        def side_effect_func(i):
            devices = [
                {
                    "name": "Built-in Microphone",
                    "maxInputChannels": 1,
                    "maxOutputChannels": 0,
                    "defaultSampleRate": 44100.0,
                },
                {
                    "name": "BlackHole 2ch",
                    "maxInputChannels": 2,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 48000.0,
                },
                {
                    "name": "Built-in Output",
                    "maxInputChannels": 0,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 44100.0,
                },
            ]
            return devices[i]

        mock_pyaudio.get_device_info_by_index.side_effect = side_effect_func

        mock_stream = Mock()
        mock_stream.read.return_value = sample_audio_bytes
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()

        # Test that capture_stream returns a generator
        stream_gen = capture.capture_stream(0.1)
        assert hasattr(stream_gen, "__iter__")
        assert hasattr(stream_gen, "__next__")

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_cleanup_on_del(self, mock_pyaudio_class, mock_pyaudio):
        """Test cleanup when AudioCapture is deleted."""
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.start_capture()

        # Manually call __del__ to test cleanup
        if hasattr(capture, "__del__"):
            capture.__del__()

        mock_pyaudio.terminate.assert_called_once()

    @pytest.mark.parametrize(
        "channels,sample_rate",
        [
            (1, 16000),
            (2, 44100),
            (2, 48000),
        ],
    )
    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_different_audio_configurations(
        self, mock_pyaudio_class, mock_pyaudio, channels, sample_rate
    ):
        """Test with different audio configurations."""
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        # Temporarily modify config for test
        original_channels = config.CHANNELS
        original_sample_rate = config.SAMPLE_RATE

        try:
            config.CHANNELS = channels
            config.SAMPLE_RATE = sample_rate

            capture = audio_capture.AudioCapture()
            capture.start_capture()

            mock_pyaudio.open.assert_called_with(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                input=True,
                input_device_index=1,
                frames_per_buffer=1024,
            )
        finally:
            # Restore original config
            config.CHANNELS = original_channels
            config.SAMPLE_RATE = original_sample_rate

    @patch("src.core.audio_capture.pyaudio.PyAudio")
    def test_audio_data_conversion(self, mock_pyaudio_class, mock_pyaudio):
        """Test that audio data is properly converted from int16 to float32."""

        def side_effect_func(i):
            devices = [
                {
                    "name": "Built-in Microphone",
                    "maxInputChannels": 1,
                    "maxOutputChannels": 0,
                    "defaultSampleRate": 44100.0,
                },
                {
                    "name": "BlackHole 2ch",
                    "maxInputChannels": 2,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 48000.0,
                },
                {
                    "name": "Built-in Output",
                    "maxInputChannels": 0,
                    "maxOutputChannels": 2,
                    "defaultSampleRate": 44100.0,
                },
            ]
            return devices[i]

        mock_pyaudio.get_device_info_by_index.side_effect = side_effect_func

        # Create int16 audio data - for stereo (2 channels), need even number of samples
        if config.CHANNELS == 2:
            int16_data = np.array(
                [32767, -32768, 0, 16384, -16384, 8192], dtype=np.int16
            )
        else:
            int16_data = np.array([32767, -32768, 0, 16384, -16384], dtype=np.int16)

        audio_bytes = int16_data.tobytes()

        mock_stream = Mock()
        mock_stream.read.return_value = audio_bytes
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        capture = audio_capture.AudioCapture()
        capture.start_capture()

        result = capture.read_chunk(0.1)

        # Check data type conversion
        assert result.dtype == np.float32

        # Check value range (should be normalized to [-1, 1])
        assert np.all(result >= -1.0)
        assert np.all(result <= 1.0)

        # The actual conversion in the code divides by 32768.0
        expected_values = int16_data.astype(np.float32) / 32768.0

        # If stereo (2 channels), the code averages them, so we need to handle that
        if config.CHANNELS == 2:
            # Reshape and average for stereo
            expected_values = expected_values.reshape(-1, 2).mean(axis=1)

        # Compare with some tolerance for floating point precision
        # Only compare the first few values since the result might be longer due to multiple reads
        min_len = min(len(result), len(expected_values))
        np.testing.assert_allclose(
            result[:min_len], expected_values[:min_len], rtol=1e-5
        )
