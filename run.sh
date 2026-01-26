#!/usr/bin/env bash
# Setup and run all CI/CD checks
# Usage: ./run.sh [clean|test|docker-build|docker-run]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

show_usage() {
    echo "Usage: ./run.sh [COMMAND] [-local]"
    echo ""
    echo "Commands:"
    echo "  clean        - Remove and recreate venv, then run all tests"
    echo "  test         - Run tests using existing venv (default)"
    echo "  docker-build - Build Docker image"
    echo "  docker-run   - Run tests in Docker container"
    echo "  -local       - Quick test run with lower coverage threshold (local development)"
    echo ""
    echo "Examples:"
    echo "  ./run.sh              # Run tests with existing venv"
    echo "  ./run.sh -local       # Quick local test (lower coverage requirements)"
    echo "  ./run.sh clean        # Clean install and test"
    echo "  ./run.sh docker-build # Build Docker image"
    echo "  ./run.sh docker-run   # Run in Docker container"
}

check_python() {
    if ! command -v python3.12 &> /dev/null; then
        echo "❌ Python 3.12 not found. Please install Python 3.12."
        exit 1
    fi
    PYTHON_VERSION=$(python3.12 --version)
    echo "✓ Found $PYTHON_VERSION"
}

create_venv() {
    echo ""
    echo "📦 Creating virtual environment..."
    python3.12 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created at $VENV_DIR"
}

activate_venv() {
    echo ""
    echo "🔧 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "❌ Failed to activate virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment activated"
}

run_docker_build() {
    echo "=== Building Docker Image ==="
    echo "Project: $PROJECT_DIR"
    echo ""
    
    cd "$PROJECT_DIR"
    
    echo "🐳 Building mindquest:test image..."
    docker build -f Dockerfile.test -t mindquest:test .
    
    echo ""
    echo "✅ Docker image built successfully!"
    echo ""
    echo "Run tests with: ./run.sh docker-run"
}

run_docker_run() {
    echo "=== Running Tests in Docker ==="
    echo "Project: $PROJECT_DIR"
    echo ""
    
    cd "$PROJECT_DIR"
    
    echo "🐳 Running tests in container..."
    docker run --rm mindquest:test
    
    echo ""
    echo "✅ Docker test completed!"
}

run_test() {
    echo "=== MindQuest Test Runner ==="
    echo "Project: $PROJECT_DIR"
    echo ""
    
    check_python
    
    if [ ! -d "$VENV_DIR" ]; then
        echo "⚠️  Virtual environment not found."
        create_venv
    else
        echo "✓ Virtual environment exists at $VENV_DIR"
    fi
    
    activate_venv
    
    echo ""
    echo "🚀 Running tests..."
    echo ""
    
    cd "$PROJECT_DIR"
    pytest tests/ -v --cov=mindquest --cov-report=term-missing --cov-fail-under=95
    
    echo ""
    echo "✅ All tests completed successfully!"
    echo ""
    echo "To activate this environment manually, run:"
    echo "  source $VENV_DIR/bin/activate"
}

run_clean() {
    echo "=== MindQuest Clean Install & Test ==="
    echo "Project: $PROJECT_DIR"
    echo ""
    
    check_python
    
    if [ -d "$VENV_DIR" ]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        echo "✓ Removed $VENV_DIR"
    fi
    
    create_venv
    activate_venv
    
    echo ""
    echo "🚀 Running tests..."
    echo ""
    
    cd "$PROJECT_DIR"
    pytest tests/ -v --cov=mindquest --cov-report=term-missing --cov-fail-under=95
    
    echo ""
    echo "✅ Clean install and all tests completed successfully!"
    echo ""
    echo "To activate this environment manually, run:"
    echo "  source $VENV_DIR/bin/activate"
}

run_local() {
    echo "=== MindQuest Local Test (Fast Mode) ==="
    echo "Project: $PROJECT_DIR"
    echo ""
    
    check_python
    
    if [ ! -d "$VENV_DIR" ]; then
        echo "⚠️  Virtual environment not found."
        create_venv
    else
        echo "✓ Virtual environment exists at $VENV_DIR"
    fi
    
    activate_venv
    
    echo ""
    echo "📦 Installing dependencies..."
    cd "$PROJECT_DIR"
    pip install -q -e . --no-deps 2>/dev/null || pip install -e . --no-deps
    pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt
    
    echo ""
    echo "🚀 Running tests with lower coverage threshold..."
    echo ""
    
    cd "$PROJECT_DIR"
    pytest tests/ -v --ignore=tests/test_gemini_integration.py --cov=mindquest --cov-report=term-missing --cov-fail-under=85 || true


    
    echo ""
    echo "✅ Local test run completed!"
    echo ""
    echo "To activate this environment manually, run:"
    echo "  source $VENV_DIR/bin/activate"
}

# Main command dispatch
COMMAND="${1:-test}"

case "$COMMAND" in
    clean)
        run_clean
        ;;
    test)
        run_test
        ;;
    -local)
        run_local
        ;;
    docker-build)
        run_docker_build
        ;;
    docker-run)
        run_docker_run
        ;;
    -h|--help|help)
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo ""
        show_usage
        exit 1
        ;;
esac
