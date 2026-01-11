# Test Suite

This directory contains comprehensive tests for the interview audio processing pipeline.

## Test Structure

```
tests/
├── __init__.py
├── analysis/
│   └── test_emotions.py           # Sentiment analysis tests
├── audio_processing/
│   ├── test_converter.py          # Audio conversion tests
│   ├── test_rttm_to_json.py       # RTTM parsing tests
│   ├── test_merge_transcriptions.py  # Transcription merging tests
│   ├── test_split_segments.py     # Audio segmentation tests
│   └── test_transcribe_whisper.py # Whisper transcription tests
├── config/
│   ├── test_environment.py        # Environment configuration tests
│   └── test_paths.py              # Path configuration tests
├── pipeline/
│   ├── test_executor.py           # Pipeline execution tests
│   └── test_steps.py              # Pipeline step configuration tests
└── utils/
    └── test_cleanup.py            # Cleanup utilities tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/audio_processing/test_converter.py
```

### Run specific test class
```bash
pytest tests/audio_processing/test_converter.py::TestConvertMp3ToWav
```

### Run specific test function
```bash
pytest tests/audio_processing/test_converter.py::TestConvertMp3ToWav::test_convert_mp3_to_wav_success
```

### Run tests by marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

## Test Categories

### Unit Tests
- Test individual functions and classes in isolation
- Use mocks and patches for external dependencies
- Fast execution

### Integration Tests
- Test interaction between multiple components
- May use temporary files and directories
- Slower execution

## Writing New Tests

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<functionality>`

### Example Test Structure
```python
import pytest
from unittest.mock import patch, MagicMock

class TestMyFunction:
    """Tests for my_function."""
    
    def test_basic_functionality(self):
        """Test basic use case."""
        # Arrange
        input_data = "test"
        
        # Act
        result = my_function(input_data)
        
        # Assert
        assert result == expected_output
    
    @patch('module.dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency."""
        # Arrange
        mock_dep.return_value = "mocked"
        
        # Act
        result = my_function()
        
        # Assert
        assert result == "expected"
        mock_dep.assert_called_once()
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:
- `sample_segments`: Sample diarization segments
- `sample_transcriptions`: Sample transcription data
- `sample_rttm_content`: Sample RTTM file content
- `mock_audio_file`: Mock audio file path
- `mock_project_structure`: Complete project directory structure

## Dependencies

Test dependencies are specified in `requirements.txt`:
- pytest: Test framework
- pytest-cov: Coverage plugin
- pytest-mock: Mocking support

## Coverage Goals

- Aim for >80% code coverage
- Focus on critical paths and edge cases
- Document any intentionally uncovered code

## Continuous Integration

Tests are designed to run in CI/CD pipelines without requiring:
- Actual audio files
- External API tokens (mocked)
- Heavy ML models (mocked)

## Troubleshooting

### Import Errors
If you encounter import errors, ensure you're running tests from the project root:
```bash
cd interview-main
pytest
```

### Missing Dependencies
Install test dependencies:
```bash
pip install -r requirements.txt
```

### Path Issues
The test suite adds `src` to the Python path automatically via `conftest.py`.
