#!/usr/bin/env python3
"""
Test script for transcription functionality
"""
import numpy as np
from transcriber import Transcriber
import config

def test_transcription_with_synthetic_data():
    """Test transcription with synthetic audio data that simulates speech."""
    print("Testing transcription with synthetic data...")

    # Create some synthetic "speech-like" audio (this won't transcribe to real words
    # but will test the pipeline)
    duration = 3.0  # seconds
    sample_rate = config.SAMPLE_RATE
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create synthetic audio with multiple frequency components
    audio = (np.sin(2 * np.pi * 200 * t) * 0.1 +  # Low frequency
             np.sin(2 * np.pi * 800 * t) * 0.05 +  # Mid frequency
             np.random.normal(0, 0.01, len(t)))    # Noise

    # Apply envelope to simulate speech patterns
    envelope = np.concatenate([
        np.linspace(0, 1, len(t)//4),     # fade in
        np.ones(len(t)//2),               # sustained
        np.linspace(1, 0, len(t)//4)      # fade out
    ])
    audio = audio * envelope

    # Ensure float32 type for Whisper
    audio = audio.astype(np.float32)

    print(f"Generated {duration}s of synthetic audio")
    print(f"Audio shape: {audio.shape}")
    print(f"Audio level (RMS): {np.sqrt(np.mean(audio**2)):.4f}")

    # Test transcription
    transcriber = Transcriber()
    result = transcriber.transcribe(audio)

    print(f"\nTranscription result:")
    print(f"Text: '{result['text']}'")
    print(f"Word count: {result['word_count']}")
    print(f"Duration: {result['duration']:.2f}s")

    # Test pace calculation
    if result['word_count'] > 0:
        wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
        pace_feedback = transcriber.get_speaking_pace_feedback(wpm)
        print(f"Speaking pace: {wpm:.0f} WPM - {pace_feedback['message']}")

    return result

def test_filler_word_detection():
    """Test filler word detection functionality."""
    print("\nTesting filler word detection...")

    transcriber = Transcriber()

    test_texts = [
        "Um, this is like, you know, a test of the, uh, filler word detection.",
        "I think this approach is actually quite good, basically.",
        "The meeting went well and we covered all the key points."
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: '{text}'")
        fillers = transcriber.count_filler_words(text)
        if fillers:
            print(f"Filler words found: {fillers}")
        else:
            print("No filler words detected")

if __name__ == "__main__":
    print("="*60)
    print("Testing Transcription Functionality")
    print("="*60)

    try:
        test_transcription_with_synthetic_data()
        test_filler_word_detection()
        print("\n✅ Transcription tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()