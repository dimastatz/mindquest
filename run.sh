#!/usr/bin/env bash
# Setup and run all CI/CD checks
# Creates virtual environment and executes full test pipeline

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "=== MindQuest Development Setup & Test Runner ==="
echo "Project: $PROJECT_DIR"
echo ""

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created at $VENV_DIR"
else
    echo "✓ Virtual environment exists at $VENV_DIR"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✓ Virtual environment activated"

# Run the test pipeline
echo ""
echo "🚀 Running CI/CD test pipeline..."
echo ""

cd "$PROJECT_DIR"
bash docker.test

echo ""
echo "✅ All checks completed successfully!"
echo ""
echo "To activate this environment manually, run:"
echo "  source $VENV_DIR/bin/activate"
