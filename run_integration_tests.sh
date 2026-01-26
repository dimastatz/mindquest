#!/usr/bin/env bash
# Run integration tests with Gemini API
# Usage: ./run_integration_tests.sh <GEMINI_API_KEY>

set -e

if [ -z "$1" ]; then
    echo "Usage: ./run_integration_tests.sh <GEMINI_API_KEY>"
    echo ""
    echo "Example:"
    echo "  ./run_integration_tests.sh sk-abc123xyz..."
    exit 1
fi

API_KEY="$1"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "=== MindQuest Integration Tests ==="
echo "Project: $PROJECT_DIR"
echo ""

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "Please run './run.sh -local' first to set up the environment"
    exit 1
fi

# Activate venv
source "$VENV_DIR/bin/activate"

echo "🚀 Running integration tests with Gemini API..."
echo ""

cd "$PROJECT_DIR"
GEMINI_API_KEY="$API_KEY" pytest tests/test_gemini_integration.py -v -m integration

echo ""
echo "✅ Integration tests completed!"
