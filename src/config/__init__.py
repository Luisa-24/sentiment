"""Configuration module for environment and project paths."""

from .environment import setup_environment
from .paths import ProjectPaths, get_project_paths

__all__ = [
    'setup_environment',
    'ProjectPaths',
    'get_project_paths',
]
