"""
Safe wrapper tools for CrewAI agents.
Prevents agents from reading/writing files outside the designated workspace.
"""
import os
from typing import Any
from crewai.tools import BaseTool
from pydantic import BaseModel


class SafeFileWriterInput(BaseModel):
    filename: str
    directory: str | None = None
    overwrite: str | bool = False
    content: str


class SafeFileWriterTool(BaseTool):
    """
    A file writer tool that enforces all writes to stay within a designated
    workspace directory. Prevents path traversal attacks (e.g. ../../main.py).
    """
    name: str = "File Writer Tool"
    description: str = (
        "A tool to write content to a file in the workspace. "
        "Accepts filename, content, and optionally a subdirectory and overwrite flag. "
        "All files are written inside the workspace directory only."
    )
    args_schema: type[BaseModel] = SafeFileWriterInput
    workspace_path: str = ""

    def _run(self, **kwargs: Any) -> str:
        try:
            filename = kwargs["filename"]
            content = kwargs["content"]
            directory = kwargs.get("directory")
            overwrite = kwargs.get("overwrite", False)

            # Convert overwrite to boolean
            if isinstance(overwrite, str):
                overwrite = overwrite.lower() in ("y", "yes", "t", "true", "on", "1")

            # Handle "null" or "None" string for directory
            if isinstance(directory, str) and directory.lower() in ("null", "none"):
                directory = None

            # Resolve the workspace absolute path
            workspace_abs = os.path.abspath(self.workspace_path)

            # If a directory is provided, treat it as relative to workspace
            if directory:
                # Strip any leading slashes or drive letters to force relative path
                directory = directory.lstrip("/\\")
                # Remove any drive letter (e.g., C:)
                if len(directory) >= 2 and directory[1] == ":":
                    directory = directory[2:].lstrip("/\\")
                target_dir = os.path.join(workspace_abs, directory)
            else:
                target_dir = workspace_abs

            # Construct the full file path
            filepath = os.path.join(target_dir, filename)

            # SECURITY: Resolve to absolute path and verify it's within workspace
            filepath_abs = os.path.abspath(filepath)
            if not filepath_abs.startswith(workspace_abs + os.sep) and filepath_abs != workspace_abs:
                return (
                    f"BLOCKED: Path '{filepath_abs}' is outside the workspace directory "
                    f"'{workspace_abs}'. All file operations must stay within the workspace."
                )

            # Create the target directory if it doesn't exist
            target_dir_abs = os.path.dirname(filepath_abs)
            if not os.path.exists(target_dir_abs):
                os.makedirs(target_dir_abs, exist_ok=True)

            # Check if file exists and overwrite is not allowed
            if os.path.exists(filepath_abs) and not overwrite:
                return f"File {filepath_abs} already exists and overwrite option was not passed."

            # Write content to the file
            mode = "w" if overwrite else "x"
            with open(filepath_abs, mode) as file:
                file.write(content)
            return f"Content successfully written to {filepath_abs}"

        except FileExistsError:
            return f"File already exists and overwrite option was not passed."
        except Exception as e:
            return f"An error occurred while writing to the file: {e!s}"


class SafeFileReaderInput(BaseModel):
    file_path: str


class SafeFileReaderTool(BaseTool):
    """
    A file reader tool that enforces all reads to stay within a designated
    workspace directory.
    """
    name: str = "File Reader Tool"
    description: str = (
        "A tool to read the contents of a file from the workspace. "
        "Provide the file path relative to the workspace directory."
    )
    args_schema: type[BaseModel] = SafeFileReaderInput
    workspace_path: str = ""

    def _run(self, **kwargs: Any) -> str:
        try:
            file_path = kwargs["file_path"]

            # Resolve the workspace absolute path
            workspace_abs = os.path.abspath(self.workspace_path)

            # Strip any leading slashes or drive letters to force relative path
            file_path = file_path.lstrip("/\\")
            if len(file_path) >= 2 and file_path[1] == ":":
                file_path = file_path[2:].lstrip("/\\")

            # Construct the full file path
            filepath_abs = os.path.abspath(os.path.join(workspace_abs, file_path))

            # SECURITY: Verify it's within workspace
            if not filepath_abs.startswith(workspace_abs + os.sep) and filepath_abs != workspace_abs:
                return (
                    f"BLOCKED: Path '{filepath_abs}' is outside the workspace directory "
                    f"'{workspace_abs}'. All file operations must stay within the workspace."
                )

            if not os.path.exists(filepath_abs):
                return f"File not found: {filepath_abs}"

            with open(filepath_abs, "r", encoding="utf-8") as file:
                return file.read()

        except Exception as e:
            return f"An error occurred while reading the file: {e!s}"
