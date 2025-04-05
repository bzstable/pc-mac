"""
Context manager for workspace handling.
Manages the current workspace state and file operations.
"""

from pathlib import Path
from typing import List, Optional
import os

class WorkspaceContext:
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or Path.cwd()
        self.current_path = self.workspace_path
        self._file_cache = {}
        
    def set_workspace(self, path: Path) -> None:
        """Set the workspace root directory."""
        self.workspace_path = path.resolve()
        self.current_path = self.workspace_path
        
    def get_current_path(self) -> Path:
        """Get the current working directory within workspace."""
        return self.current_path
        
    def change_directory(self, path: str) -> Path:
        """Change current directory within workspace."""
        new_path = (self.current_path / path).resolve()
        if not new_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not new_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        if not str(new_path).startswith(str(self.workspace_path)):
            raise PermissionError("Cannot navigate outside workspace")
        self.current_path = new_path
        return self.current_path
        
    def list_directory(self, path: Optional[str] = None) -> List[Path]:
        """List contents of specified directory."""
        target = self.current_path
        if path:
            target = (self.current_path / path).resolve()
        if not str(target).startswith(str(self.workspace_path)):
            raise PermissionError("Cannot access outside workspace")
        return list(target.iterdir())
        
    def read_file(self, path: str) -> str:
        """Read contents of a file within workspace."""
        file_path = (self.current_path / path).resolve()
        if not str(file_path).startswith(str(self.workspace_path)):
            raise PermissionError("Cannot read outside workspace")
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        return file_path.read_text()
        
    def get_relative_path(self, path: Path) -> str:
        """Get path relative to workspace root."""
        return str(path.relative_to(self.workspace_path))
        
    def get_project_files(self, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
        """Get all project files, excluding specified patterns."""
        exclude_patterns = exclude_patterns or [
            "**/__pycache__/**",
            "**/.git/**",
            "**/node_modules/**",
            "**/.env*"
        ]
        files = []
        for item in self.workspace_path.rglob("*"):
            if item.is_file():
                exclude = False
                for pattern in exclude_patterns:
                    if item.match(pattern):
                        exclude = True
                        break
                if not exclude:
                    files.append(item)
        return files 