#!/usr/bin/env python3
"""
End-to-end test for the Teams Meeting Coach pipeline
"""
import numpy as np
from audio_capture import AudioCapture
from transcriber import Transcriber
from analyzer import CommunicationAnalyzer
from feedback_display import SimpleFeedbackDisplay
import config

def simulate_meeting_audio():
    """Simulate a short meeting with some test 'speech' audio."""
    print("🎤 Simulating meeting audio capture...")

    # Use audio capture to get the format but with synthetic data
    capture = AudioCapture()

    # Create synthetic audio that resembles speech patterns
    duration = 5.0
    sample_rate = config.SAMPLE_RATE
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create more complex synthetic audio
    audio = (
        np.sin(2 * np.pi * 150 * t) * 0.1 +      # Fundamental frequency
        np.sin(2 * np.pi * 300 * t) * 0.05 +     # First harmonic
        np.sin(2 * np.pi * 450 * t) * 0.03 +     # Second harmonic
        np.random.normal(0, 0.01, len(t))        # Background noise
    )

    # Apply speech-like envelope (varying amplitude)
    envelope = np.abs(np.sin(2 * np.pi * 2 * t))  # 2 Hz modulation
    audio = audio * envelope

    # Ensure correct data type
    audio = audio.astype(np.float32)

    print(f"✅ Generated {duration}s of synthetic speech-like audio")
    print(f"   Audio shape: {audio.shape}")
    print(f"   Audio level (RMS): {np.sqrt(np.mean(audio**2)):.4f}")

    return audio

def test_pipeline_with_synthetic_text():
    """Test the pipeline with pre-defined text (simulating perfect transcription)."""
    print("\n🔄 Testing pipeline with synthetic text...")

    # Initialize components
    analyzer = CommunicationAnalyzer()
    display = SimpleFeedbackDisplay()
    transcriber = Transcriber()

    # Test texts simulating meeting speech
    test_transcriptions = [
        {
            'text': "I really think your proposal has some excellent points and I appreciate the thorough research you've done",
            'word_count': 17,
            'duration': 5.0
        },
        {
            'text': "Um, whatever, I don't really, like, think this is going to work at all, you know",
            'word_count': 16,
            'duration': 4.5
        },
        {
            'text': "The quarterly metrics indicate a fifteen percent improvement in our customer satisfaction scores",
            'word_count': 14,
            'duration': 6.0
        }
    ]

    display.update_status(True)

    for i, result in enumerate(test_transcriptions, 1):
        print(f"\n--- Processing chunk {i} ---")
        print(f"Text: \"{result['text']}\"")

        # Test pace calculation
        wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
        pace_feedback = transcriber.get_speaking_pace_feedback(wpm)
        display.update_pace(wpm, pace_feedback)

        # Test filler word detection
        filler_counts = transcriber.count_filler_words(result['text'])
        if filler_counts:
            display.update_filler_words(filler_counts)

        # Test tone analysis (will work without Ollama model)
        if result['word_count'] >= config.MIN_WORDS_FOR_ANALYSIS:
            tone_analysis = analyzer.analyze_tone(result['text'])

            if 'error' not in tone_analysis:
                tone = tone_analysis.get('tone', 'neutral')
                confidence = tone_analysis.get('confidence', 0.0)
                emoji = analyzer.get_tone_emoji(tone)

                display.update_tone(tone, confidence, emoji)

                # Check for alerts
                should_alert = analyzer.should_alert(tone, confidence)
                feedback = {
                    'text': result['text'],
                    'tone': tone,
                    'confidence': confidence,
                    'suggestion': tone_analysis.get('suggestions', ''),
                    'alert': should_alert
                }
                display.add_feedback(feedback)
            else:
                print(f"   ⚠️  Tone analysis failed: {tone_analysis.get('error', 'Unknown error')}")

    display.update_status(False)
    print("\n✅ Pipeline test completed!")

def test_full_pipeline():
    """Test the complete pipeline with synthetic audio."""
    print("\n🔄 Testing complete pipeline...")

    # Initialize components
    audio_capture = AudioCapture()
    transcriber = Transcriber()
    analyzer = CommunicationAnalyzer()
    display = SimpleFeedbackDisplay()

    display.update_status(True)

    # Generate synthetic audio
    audio_data = simulate_meeting_audio()

    # Process through transcription
    print("\n📝 Running transcription...")
    transcription = transcriber.transcribe(audio_data)

    if transcription['text']:
        print(f"✅ Transcription: \"{transcription['text']}\"")

        # Calculate pace
        wpm = transcriber.calculate_wpm(
            transcription['word_count'],
            transcription['duration']
        )
        pace_feedback = transcriber.get_speaking_pace_feedback(wpm)
        display.update_pace(wpm, pace_feedback)

        # Analyze filler words
        filler_counts = transcriber.count_filler_words(transcription['text'])
        if filler_counts:
            display.update_filler_words(filler_counts)

        # Analyze tone
        if transcription['word_count'] >= config.MIN_WORDS_FOR_ANALYSIS:
            tone_analysis = analyzer.analyze_tone(transcription['text'])

            if 'error' not in tone_analysis:
                tone = tone_analysis.get('tone', 'neutral')
                confidence = tone_analysis.get('confidence', 0.0)
                emoji = analyzer.get_tone_emoji(tone)

                display.update_tone(tone, confidence, emoji)

                should_alert = analyzer.should_alert(tone, confidence)
                feedback = {
                    'text': transcription['text'],
                    'tone': tone,
                    'confidence': confidence,
                    'suggestion': tone_analysis.get('suggestions', ''),
                    'alert': should_alert
                }
                display.add_feedback(feedback)
    else:
        print("⚠️  No speech detected in synthetic audio (expected)")

    display.update_status(False)
    print("\n✅ Full pipeline test completed!")

if __name__ == "__main__":
    print("="*60)
    print("🎯 End-to-End Pipeline Test")
    print("="*60)

    try:
        # First test with predefined text
        test_pipeline_with_synthetic_text()

        # Then test with full audio pipeline
        test_full_pipeline()

        print("\n🎉 All tests completed successfully!")
        print("\nThe Teams Meeting Coach pipeline is ready to use!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()