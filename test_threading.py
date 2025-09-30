#!/usr/bin/env python3
"""
Test script for validating the threaded audio capture and processing implementation
"""
import sys
import time
import threading
import queue
import numpy as np

# Add project root to path
sys.path.append('.')

from main import MeetingCoach
import config

def test_threading_initialization():
    """Test that threading components are properly initialized"""
    print("Testing threading initialization...")
    
    coach = MeetingCoach(use_menu_bar=False)
    
    # Check queue initialization
    assert coach.audio_queue is not None, "Audio queue should be initialized"
    assert isinstance(coach.audio_queue, queue.Queue), "Should be a Queue instance"
    assert coach.audio_queue.maxsize == 50, "Queue should have max size of 50"
    
    # Check threading attributes
    assert hasattr(coach, 'capture_thread'), "Should have capture_thread attribute"
    assert hasattr(coach, 'processing_thread'), "Should have processing_thread attribute"
    assert hasattr(coach, 'stop_event'), "Should have stop_event attribute"
    
    # Check buffer lock
    assert coach.buffer_lock is not None, "Buffer lock should be initialized"
    assert isinstance(coach.buffer_lock, threading.Lock), "Should be a Lock instance"
    
    print("✅ Threading initialization test passed")
    return coach

def test_thread_safe_buffer():
    """Test thread-safe buffer operations"""
    print("Testing thread-safe buffer operations...")
    
    coach = MeetingCoach(use_menu_bar=False)
    
    # Test writing to buffer
    with coach.buffer_lock:
        coach.text_buffer = "Hello world"
        coach.buffer_word_count = 2
        coach.buffer_start_time = time.time()
    
    # Test reading from buffer
    with coach.buffer_lock:
        buffer_copy = coach.text_buffer
        word_count_copy = coach.buffer_word_count
        start_time_copy = coach.buffer_start_time
    
    assert buffer_copy == "Hello world", f"Expected 'Hello world', got '{buffer_copy}'"
    assert word_count_copy == 2, f"Expected 2 words, got {word_count_copy}"
    assert start_time_copy is not None, "Start time should be set"
    
    print("✅ Thread-safe buffer test passed")

def test_queue_operations():
    """Test audio queue operations"""
    print("Testing queue operations...")
    
    coach = MeetingCoach(use_menu_bar=False)
    
    # Create dummy audio data
    dummy_audio = np.random.random(1000).astype(np.float32)
    
    # Test putting data in queue
    coach.audio_queue.put(dummy_audio)
    assert not coach.audio_queue.empty(), "Queue should not be empty after putting data"
    
    # Test getting data from queue
    retrieved_audio = coach.audio_queue.get_nowait()
    assert np.array_equal(dummy_audio, retrieved_audio), "Retrieved audio should match original"
    assert coach.audio_queue.empty(), "Queue should be empty after getting data"
    
    print("✅ Queue operations test passed")

def test_stop_event():
    """Test stop event functionality"""
    print("Testing stop event...")
    
    coach = MeetingCoach(use_menu_bar=False)
    
    # Initially should not be set
    assert not coach.stop_event.is_set(), "Stop event should not be set initially"
    
    # Set the event
    coach.stop_event.set()
    assert coach.stop_event.is_set(), "Stop event should be set after calling set()"
    
    # Clear the event
    coach.stop_event.clear()
    assert not coach.stop_event.is_set(), "Stop event should not be set after calling clear()"
    
    print("✅ Stop event test passed")

def test_configuration():
    """Test that configuration values are appropriate for threading"""
    print("Testing configuration for threading...")
    
    print(f"Chunk duration: {config.CHUNK_DURATION} seconds")
    print(f"Sample rate: {config.SAMPLE_RATE} Hz")
    print(f"Min words for analysis: {config.MIN_WORDS_FOR_ANALYSIS}")
    
    # Check that chunk duration isn't too long (would cause delays)
    assert config.CHUNK_DURATION <= 10, f"Chunk duration ({config.CHUNK_DURATION}s) should be <= 10s for responsive threading"
    
    # Check that we have reasonable buffer settings
    coach = MeetingCoach(use_menu_bar=False)
    queue_size = coach.audio_queue.maxsize
    
    # With 5s chunks and 50 queue size, we can buffer 250s of audio
    max_buffer_time = config.CHUNK_DURATION * queue_size
    print(f"Maximum buffer time: {max_buffer_time} seconds")
    
    assert max_buffer_time >= 60, f"Should be able to buffer at least 60s, got {max_buffer_time}s"
    
    print("✅ Configuration test passed")

def main():
    """Run all tests"""
    print("="*60)
    print("TESTING THREADED AUDIO CAPTURE IMPLEMENTATION")
    print("="*60)
    print()
    
    try:
        # Run all tests
        test_threading_initialization()
        print()
        
        test_thread_safe_buffer()
        print()
        
        test_queue_operations()
        print()
        
        test_stop_event()
        print()
        
        test_configuration()
        print()
        
        print("="*60)
        print("✅ ALL THREADING TESTS PASSED!")
        print("✅ Implementation is ready for threaded audio processing")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)