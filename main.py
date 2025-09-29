"""
Teams Meeting Coach - Main Application
Provides real-time feedback on speaking pace, tone, and communication style
"""
import sys
import time
import argparse
import numpy as np
from audio_capture import AudioCapture
from transcriber import Transcriber
from analyzer import CommunicationAnalyzer
from feedback_display import FeedbackDisplay, SimpleFeedbackDisplay
import config


class MeetingCoach:
    def __init__(self, use_menu_bar: bool = True):
        """
        Initialize the Meeting Coach system.
        
        Args:
            use_menu_bar: Use menu bar app (True) or console output (False)
        """
        print("Initializing Teams Meeting Coach...")
        
        # Initialize components
        if config.USE_MICROPHONE_INPUT:
            self.audio_capture = AudioCapture(config.MICROPHONE_DEVICE_INDEX, use_microphone=True)
        else:
            self.audio_capture = AudioCapture(config.BLACKHOLE_DEVICE_INDEX, use_microphone=False)
        self.transcriber = Transcriber()
        self.analyzer = CommunicationAnalyzer()
        
        # Initialize display
        if use_menu_bar:
            try:
                self.display = FeedbackDisplay()
            except Exception as e:
                print(f"Could not initialize menu bar app: {e}")
                print("Falling back to console display")
                self.display = SimpleFeedbackDisplay()
        else:
            self.display = SimpleFeedbackDisplay()
        
        self.is_running = False
    
    def process_audio_chunk(self, audio_data):
        """
        Process a single audio chunk through the pipeline.
        
        Args:
            audio_data: numpy array of audio samples
        """
        # Transcribe
        transcription = self.transcriber.transcribe(audio_data)
        text = transcription['text']
        
        # Skip if no speech detected
        if not text or transcription['word_count'] < 3:
            print(".", end="", flush=True)  # Show we're still running
            return
        
        print(f"\n\nTranscription: {text}")
        print("-" * 60)
        
        # Analyze speaking pace
        wpm = self.transcriber.calculate_wpm(
            transcription['word_count'],
            transcription['duration']
        )
        pace_feedback = self.transcriber.get_speaking_pace_feedback(wpm)
        self.display.update_pace(wpm, pace_feedback)
        
        # Count filler words
        filler_counts = self.transcriber.count_filler_words(text)
        if filler_counts:
            self.display.update_filler_words(filler_counts)
        
        # Analyze tone (only if enough content)
        if transcription['word_count'] >= config.MIN_WORDS_FOR_ANALYSIS:
            tone_analysis = self.analyzer.analyze_tone(text)
            
            tone = tone_analysis.get('tone', 'neutral')
            confidence = tone_analysis.get('confidence', 0.0)
            emoji = self.analyzer.get_tone_emoji(tone)
            
            self.display.update_tone(tone, confidence, emoji)
            
            # Add feedback if significant
            should_alert = self.analyzer.should_alert(tone, confidence)
            feedback = {
                'text': text,
                'tone': tone,
                'confidence': confidence,
                'suggestion': tone_analysis.get('suggestions', ''),
                'alert': should_alert
            }
            self.display.add_feedback(feedback)
    
    def run(self):
        """Start the meeting coach."""
        print("\n" + "="*60)
        print("Teams Meeting Coach is running!")
        print("="*60)
        print(f"Chunk duration: {config.CHUNK_DURATION} seconds")
        print(f"Whisper model: {config.WHISPER_MODEL}")
        print(f"Analysis model: {config.OLLAMA_MODEL}")
        print("\nMake sure:")
        if config.USE_MICROPHONE_INPUT:
            print("1. Your microphone is working and has permission")
            print("2. You're speaking clearly into your microphone")
            print("3. Ollama is running (ollama serve)")
        else:
            print("1. BlackHole is configured")
            print("2. Teams audio is routed through BlackHole Multi-Output")
            print("3. Ollama is running (ollama serve)")
        print("\nPress Ctrl+C to stop")
        print("="*60 + "\n")
        
        self.display.update_status(True)
        self.is_running = True
        
        try:
            # Start audio capture stream
            for audio_chunk in self.audio_capture.capture_stream(config.CHUNK_DURATION):
                if not self.is_running:
                    break
                
                self.process_audio_chunk(audio_chunk)
        
        except KeyboardInterrupt:
            print("\n\nStopping Meeting Coach...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        self.is_running = False
        self.display.update_status(False)
        print("Meeting Coach stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Teams Meeting Coach - Real-time meeting feedback"
    )
    parser.add_argument(
        '--console',
        action='store_true',
        help='Use console output instead of menu bar app'
    )
    parser.add_argument(
        '--test-audio',
        action='store_true',
        help='Test audio capture and list devices'
    )
    parser.add_argument(
        '--test-transcription',
        action='store_true',
        help='Test transcription with existing test_capture.wav'
    )
    
    args = parser.parse_args()
    
    # Test mode
    if args.test_audio:
        print("Testing audio capture...\n")
        if config.USE_MICROPHONE_INPUT:
            capture = AudioCapture(use_microphone=True)
            print("Testing MICROPHONE input (your speech will be analyzed)")
            print("Speak into your microphone during the test...")
        else:
            capture = AudioCapture(use_microphone=False)
            print("Testing BlackHole output (Teams audio will be analyzed)")

        capture.list_devices()

        print("\nCapturing 5 seconds of audio...")
        capture.start_capture()
        audio = capture.read_chunk(5.0)
        capture.stop_capture()

        print(f"Captured audio shape: {audio.shape}")
        print(f"Audio level (RMS): {np.sqrt(np.mean(audio**2)):.4f}")
        capture.save_chunk_to_wav(audio, "test_capture.wav")
        return
    
    if args.test_transcription:
        print("Testing transcription...\n")
        from transcriber import Transcriber
        import wave
        
        transcriber = Transcriber()
        
        try:
            with wave.open("test_capture.wav", 'rb') as wf:
                audio_bytes = wf.readframes(wf.getnframes())
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                
                result = transcriber.transcribe(audio_array)
                print(f"Transcription: {result['text']}")
                print(f"Word count: {result['word_count']}")
                
                wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
                print(f"Speaking pace: {wpm:.0f} WPM")
        except FileNotFoundError:
            print("test_capture.wav not found. Run with --test-audio first.")
        return
    
    # Run meeting coach
    use_menu_bar = not args.console
    coach = MeetingCoach(use_menu_bar=use_menu_bar)
    
    if use_menu_bar and isinstance(coach.display, FeedbackDisplay):
        # Run as menu bar app
        coach.display.run()
    else:
        # Run in console mode
        coach.run()


if __name__ == "__main__":
    main()
