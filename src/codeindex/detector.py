"""Lightweight language detection without full AST parsing."""

from pathlib import Path
from typing import Dict, Set

# Universal exclude patterns - always skip these
UNIVERSAL_EXCLUDES = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "target",
    ".gradle",
}


def quick_detect_languages(root: Path, file_extensions: Dict[str, str]) -> Set[str]:
    """Fast language detection by scanning file extensions only.

    Args:
        root: Project root directory
        file_extensions: Mapping of extension -> language (e.g., {'.py': 'python'})

    Returns:
        Set of detected language names
    """
    langs: Set[str] = set()

    for file in root.rglob("*"):
        # Skip universal exclude directories
        if any(part in UNIVERSAL_EXCLUDES for part in file.parts):
            continue

        if not file.is_file():
            continue

        ext = file.suffix.lower()
        if lang := file_extensions.get(ext):
            langs.add(lang)

    return langs
