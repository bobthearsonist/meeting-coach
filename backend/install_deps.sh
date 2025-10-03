#!/bin/bash
# Installation script for Teams Meeting Coach dependencies

set -e  # Exit on any error

echo "🎯 Teams Meeting Coach - Dependency Installation"
echo "================================================"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS. Please install dependencies manually."
    exit 1
fi

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ Homebrew found"

# Install system dependencies
echo
echo "📦 Installing system dependencies..."

# Install BlackHole audio driver
if ! brew list blackhole-2ch &> /dev/null; then
    echo "   Installing BlackHole 2ch..."
    brew install blackhole-2ch
else
    echo "   ✅ BlackHole 2ch already installed"
fi

# Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "   Installing Ollama..."
    brew install ollama
else
    echo "   ✅ Ollama already installed"
fi

# Create virtual environment if it doesn't exist
echo
echo "🐍 Setting up Python environment..."

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
else
    echo "   ✅ Virtual environment already exists"
fi

# Activate virtual environment and install Python dependencies
echo "   Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "   ✅ Python dependencies installed"

# Start Ollama service
echo
echo "🦙 Setting up Ollama..."

echo "   Starting Ollama service..."
brew services start ollama

# Wait a bit for service to start
sleep 3

# Pull the llama3 model
echo "   Downloading llama3 model (this may take several minutes)..."
ollama pull llama3

echo "   ✅ Ollama setup complete"

# Setup audio configuration instructions
echo
echo "🎵 Audio Configuration Required"
echo "================================"
echo "You need to configure your audio routing manually:"
echo
echo "1. Open 'Audio MIDI Setup' application"
echo "2. Click the '+' button and select 'Create Multi-Output Device'"
echo "3. In the new Multi-Output Device:"
echo "   - Check 'BlackHole 2ch'"
echo "   - Check your speakers/headphones"
echo "   - Set as 'Use This Device For Sound Output' if desired"
echo "4. In Microsoft Teams:"
echo "   - Go to Settings > Devices"
echo "   - Set Speaker to the Multi-Output Device you created"
echo "   - Set Microphone to your preferred microphone"
echo
echo "This setup allows the coach to 'listen' to Teams audio while you still hear it."

# Run setup check
echo
echo "🧪 Running setup verification..."
python setup_check.py

echo
echo "🎉 Installation complete!"
echo
echo "To start the Teams Meeting Coach:"
echo "   ./run_with_venv.sh                    # Menu bar app"
echo "   ./run_with_venv.sh --console          # Console mode"
echo "   ./run_with_venv.sh --test-audio       # Test audio setup"