"""Pipeline step execution and subprocess handling."""

import subprocess
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config.paths import ProjectPaths


@dataclass
class PipelineStep:
    """
    Definition of a pipeline step.
    
    Attributes
    ----------
    name : str
        Name of the step for logging
    command : List[str]
        Command to execute as list of arguments
    description : str
        Description of what the step does
    """
    name: str
    command: List[str]
    description: str


@dataclass
class StepResult:
    """
    Result of a pipeline step execution.
    
    Attributes
    ----------
    success : bool
        Whether the step completed successfully
    step_name : str
        Name of the step that was executed
    stdout : str
        Standard output from the command
    stderr : str
        Standard error from the command
    return_code : Optional[int]
        Return code from the process (None if not started)
    """
    success: bool
    step_name: str
    stdout: str = ""
    stderr: str = ""
    return_code: Optional[int] = None


def execute_step(step: PipelineStep) -> StepResult:
    """
    Execute a single pipeline step and handle errors.
    
    Parameters
    ----------
    step : PipelineStep
        The step to execute
    
    Returns
    -------
    StepResult
        Structured result of the execution
    """
    print(f"\n{'='*80}")
    print(f"PASO: {step.name}")
    print(f"{'='*80}")
    print(f"{step.description}\n")
    
    try:
        result = subprocess.run(
            step.command,
            check=True,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"Warnings/Info:\n{result.stderr}")
        print(f" {step.name} completado exitosamente")
        
        return StepResult(
            success=True,
            step_name=step.name,
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode
        )
    
    except subprocess.CalledProcessError as e:
        print(f" Error en {step.name}")
        print(f"Codigo de salida: {e.returncode}")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
        
        return StepResult(
            success=False,
            step_name=step.name,
            stdout=e.stdout,
            stderr=e.stderr,
            return_code=e.returncode
        )
    
    except Exception as e:
        print(f"Error inesperado en {step.name}: {e}")
        
        return StepResult(
            success=False,
            step_name=step.name,
            stderr=str(e)
        )


def run_pipeline(steps: List[PipelineStep]) -> bool:
    """
    Execute all pipeline steps in sequence.
    
    Parameters
    ----------
    steps : List[PipelineStep]
        List of steps to execute in order
    
    Returns
    -------
    bool
        True if all steps completed successfully, False otherwise
    """
    for step in steps:
        result = execute_step(step)
        
        if not result.success:
            print(f"\n{'='*80}")
            print(" PIPELINE DETENIDO: Error en el paso anterior")
            print(f"{'='*80}")
            return False
    
    return True
