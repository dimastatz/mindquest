# Integration Tests Guide

## Running Integration Tests with Gemini API

The MindQuest project includes integration tests that create real podcasts using the Google Gemini API. These tests are excluded from the standard local test run.

### Prerequisites

1. Obtain a [Google Gemini API key](https://ai.google.dev/)
2. Ensure the virtual environment is set up: `./run.sh -local`

### Running Integration Tests

To run the integration tests with a real Gemini API key:

```bash
./run_integration_tests.sh YOUR_GEMINI_API_KEY
```

**Example:**
```bash
./run_integration_tests.sh "AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### What the Integration Tests Do

The integration test suite (`tests/test_gemini_integration.py`) includes:

1. **test_create_podcast_about_space** - Creates a podcast about "The Moon"
2. **test_create_podcast_about_animals** - Creates a podcast about "Penguins"
3. **test_voice_over_with_generated_script** - Generates script and voice-over for "Space Travel"
4. **test_create_two_different_podcasts** - Creates 2 podcasts about different topics:
   - "The Solar System"
   - "Ocean Life"
5. **test_full_podcast_pipeline** - Tests the complete pipeline:
   - Script generation
   - Voice-over synthesis
   - Result validation

### Expected Behavior

When integration tests run successfully:
- ✅ Scripts will be generated with Plato (wise professor) and Pixel (curious 10-year-old) characters
- ✅ Each script will be educational, age-appropriate, and 600-800 words
- ✅ Voice-over audio will be generated (or marked as None if not supported by API)
- ✅ Two different podcasts will be created with distinct content

### API Usage Notes

- Each test makes at least one API call to generate a script
- The model used is `gemini-2.0-flash`
- Requests may take 10-30 seconds to complete
- Consider your API quota and rate limits

### Skipping Integration Tests

Integration tests are automatically skipped if:
- No `GEMINI_API_KEY` environment variable is set
- Using the standard `./run.sh -local` command (which excludes integration tests)

To run all tests including integration tests (requires API key):
```bash
GEMINI_API_KEY="YOUR_KEY" pytest tests/ -v
```
