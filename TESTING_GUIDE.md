# MindQuest Testing Guide

## Test Suite Overview

The MindQuest project has a comprehensive test suite with **38 unit tests** and **5 integration tests** covering all modules.

### Test Organization

- **Unit Tests**: 38 tests, 96% code coverage, ~1.2 seconds
- **Integration Tests**: 5 tests, requires Gemini API key, ~30-60 seconds
- **Total**: 43 tests available

## Running Tests

### Local Tests (No API Key Required)

```bash
./run.sh -local
```

**What it does:**
- Runs 38 unit tests
- Excludes integration tests (they require Gemini API key)
- Reports 96% code coverage
- Requires 85% minimum coverage

### Integration Tests (Requires Gemini API Key)

```bash
./run_integration_tests.sh YOUR_GEMINI_API_KEY
```

**What it tests:**
- Creates podcast about "The Moon" 
- Creates podcast about "Penguins"
- Generates voice-over for scripts
- Creates **2 different podcasts** with different topics
- Tests complete pipeline end-to-end

## Test Coverage Breakdown

| Module | Coverage | Status |
|--------|----------|--------|
| script.py | 100% | ✅ All paths covered |
| voice.py | 93.10% | ✅ Minor error path |
| types/__init__.py | 100% | ✅ All paths covered |
| utils/__init__.py | 95.12% | ✅ Fallback path |
| utils/gemini.py | 100% | ✅ All paths covered |

## Test Descriptions

### Unit Tests (38 total)

**test_script.py** (7 tests)
- Valid topic creation
- Input validation (empty, None, whitespace)
- API key validation
- Error handling

**test_voice.py** (10 tests)
- Script parsing
- Character detection
- Voice synthesis
- Multi-language support
- Error handling

**test_types.py** (4 tests)
- Character profile creation
- Predefined characters
- Profile attributes

**test_utils.py** (17 tests)
- WikiKids search
- WikiKids summaries
- Network error handling
- Gemini integration

### Integration Tests (5 total)

**test_gemini_integration.py**
1. Create podcast about space
2. Create podcast about animals
3. Voice-over generation
4. **Create 2 different podcasts** (main test)
5. Complete pipeline validation

## Quick Commands

**Run everything locally:**
```bash
./run.sh -local
```

**Run specific test file:**
```bash
source .venv/bin/activate
pytest tests/test_script.py -v
```

**Run with coverage report:**
```bash
pytest tests/ --cov=mindquest --cov-report=html
pytest tests/ --cov=mindquest --cov-report=term-missing
```

**Run integration tests:**
```bash
./run_integration_tests.sh YOUR_GEMINI_API_KEY
```

## Getting Gemini API Key

1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Create new API key
4. Copy and use with integration tests

## Expected Results

### Local Test Run
```
38 passed in 1.2s, 96% coverage
```

### Integration Test Run
```
5 passed in 45s
- Creates "The Moon" podcast
- Creates "Penguins" podcast
- Generates voice synthesis
- Tests 2-podcast creation
- Validates complete pipeline
```

## Troubleshooting

**Tests failing locally?**
- Ensure venv is activated: `source .venv/bin/activate`
- Check requirements: `pip install -r requirements.txt`

**Integration tests skipped?**
- Ensure GEMINI_API_KEY environment variable is set
- Run with: `./run_integration_tests.sh YOUR_KEY`

**Coverage below 85%?**
- Add tests for uncovered lines
- View missing lines: `pytest --cov-report=term-missing`

## CI/CD Integration

Tests are configured for:
- Local development: `./run.sh -local`
- Docker builds: `./run.sh docker-run`
- Coverage threshold: 85% minimum
- Exit code: 0 on pass, 1 on fail
