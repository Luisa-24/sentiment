"""Tests for pipeline.executor module."""

from unittest.mock import patch, MagicMock
from src.pipeline.executor import PipelineStep, execute_step


@patch('src.pipeline.executor.subprocess.run')
def test_execute_step_success(mock_run):
    """Test successful step execution."""
    step = PipelineStep(
        name="Test Step",
        command=["python", "--version"],
        description="Check Python version"
    )
    mock_run.return_value = MagicMock(returncode=0, stdout="Python 3.9.0", stderr="")
    
    result = execute_step(step)
    
    assert result.success is True
    assert result.step_name == "Test Step"
    mock_run.assert_called_once()
