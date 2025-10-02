#!/usr/bin/env python3
"""
Setup verification script for Teams Meeting Coach
Checks all dependencies and configuration
"""
import sys
import subprocess
import importlib

def check_python_version():
    """Check Python version requirements."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need >= 3.8)")
        return False

def check_python_packages():
    """Check required Python packages."""
    print("\n📦 Checking Python packages...")

    required_packages = [
        'faster_whisper',
        'pyaudio',
        'numpy',
        'ollama',
        'rumps'
    ]

    all_good = True
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            all_good = False

    return all_good

def check_ollama_installation():
    """Check Ollama installation and service."""
    print("\n🦙 Checking Ollama...")

    # Check if ollama command exists
    try:
        result = subprocess.run(['ollama', '--version'],
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ Ollama installed: {version}")
        else:
            print("   ❌ Ollama command failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Ollama not found (run: brew install ollama)")
        return False

    # Check if Ollama service is running
    try:
        result = subprocess.run(['ollama', 'list'],
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Ollama service is running")

            # Check for llama3 model
            if 'llama3' in result.stdout:
                print("   ✅ llama3 model available")
            else:
                print("   ⚠️  llama3 model not found (run: ollama pull llama3)")
                return False
        else:
            print("   ❌ Ollama service not running (run: ollama serve)")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ Ollama service timeout")
        return False

    return True

def check_blackhole_audio():
    """Check BlackHole audio device."""
    print("\n🎵 Checking BlackHole audio...")

    try:
        from audio_capture import AudioCapture
        capture = AudioCapture()

        if capture.device_index is not None:
            device_name = capture.get_device_name(capture.device_index)
            print(f"   ✅ BlackHole found: {device_name}")
            return True
        else:
            print("   ❌ BlackHole not found")
            print("      Install with: brew install blackhole-2ch")
            print("      Then configure Multi-Output Device in Audio MIDI Setup")
            return False
    except Exception as e:
        print(f"   ❌ Audio check failed: {e}")
        return False

def check_disk_space():
    """Check available disk space for models."""
    print("\n💾 Checking disk space...")

    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        free_gb = free / (1024**3)

        if free_gb >= 5.0:
            print(f"   ✅ {free_gb:.1f} GB free (OK)")
            return True
        else:
            print(f"   ⚠️  {free_gb:.1f} GB free (need ~5GB for models)")
            return False
    except Exception as e:
        print(f"   ❌ Disk check failed: {e}")
        return False

def run_quick_test():
    """Run a quick functionality test."""
    print("\n🧪 Running quick test...")

    try:
        # Test imports
        from audio_capture import AudioCapture
        from transcriber import Transcriber
        from analyzer import CommunicationAnalyzer
        from feedback_display import SimpleFeedbackDisplay

        # Test audio capture initialization
        capture = AudioCapture()
        print("   ✅ Audio capture initialized")

        # Test transcriber initialization
        transcriber = Transcriber()
        print("   ✅ Transcriber initialized")

        # Test analyzer initialization
        analyzer = CommunicationAnalyzer()
        print("   ✅ Analyzer initialized")

        # Test display initialization
        display = SimpleFeedbackDisplay()
        print("   ✅ Display initialized")

        # Test basic functionality
        test_text = "This is a test of the meeting coach system"
        fillers = transcriber.count_filler_words(test_text)
        emoji = analyzer.get_emotional_state_emoji('calm')
        print("   ✅ Basic functionality working")

        return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Run all setup checks."""
    print("="*60)
    print("🎯 Teams Meeting Coach - Setup Verification")
    print("="*60)

    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_python_packages),
        ("Ollama", check_ollama_installation),
        ("BlackHole Audio", check_blackhole_audio),
        ("Disk Space", check_disk_space),
        ("Quick Test", run_quick_test),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name} check failed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("📋 Setup Check Summary")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:8} {name}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 All checks passed! Teams Meeting Coach is ready to use.")
        print("\nTo start the application:")
        print("   ./run_with_venv.sh                    # Menu bar app")
        print("   ./run_with_venv.sh --console          # Console mode")
        print("   ./run_with_venv.sh --test-audio       # Test audio")
    else:
        print("⚠️  Some checks failed. Please address the issues above.")
        print("\nFor help with setup, see README.md")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
