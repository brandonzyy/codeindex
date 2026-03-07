"""Automatic tree-sitter parser installation."""

import logging
import subprocess
import sys
from typing import Dict, Set

log = logging.getLogger("codeindex.parser_installer")

# Language -> pip package mapping
# Specialized parsers (high-quality extraction)
LANG_TO_PACKAGE = {
    "python": "tree-sitter-python",
    "javascript": "tree-sitter-javascript",
    "typescript": "tree-sitter-typescript",
    "tsx": "tree-sitter-typescript",
    "php": "tree-sitter-php",
    "java": "tree-sitter-java",
    # Generic parsers (good-enough extraction via GenericParser)
    "go": "tree-sitter-go",
    "rust": "tree-sitter-rust",
    "c": "tree-sitter-c",
    "cpp": "tree-sitter-cpp",
    "c_sharp": "tree-sitter-c-sharp",
    "ruby": "tree-sitter-ruby",
    "swift": "tree-sitter-swift",
    "kotlin": "tree-sitter-kotlin",
    "scala": "tree-sitter-scala",
    "lua": "tree-sitter-lua",
    "r": "tree-sitter-r",
    "elixir": "tree-sitter-elixir",
    "dart": "tree-sitter-dart",
    "haskell": "tree-sitter-haskell",
    "ocaml": "tree-sitter-ocaml",
    "bash": "tree-sitter-bash",
    "zig": "tree-sitter-zig",
}

# Pip mirrors for faster installation
PIP_MIRRORS = [
    None,  # default PyPI
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple",
]


def check_parser_installed(language: str) -> bool:
    """Check if tree-sitter parser is installed.

    Dynamically checks for the corresponding tree_sitter_{language} module.
    Handles special cases like tsx → tree_sitter_typescript.
    """
    # Map language to Python module name
    if language in ("typescript", "tsx"):
        mod_name = "tree_sitter_typescript"
    else:
        mod_name = f"tree_sitter_{language}"
    try:
        __import__(mod_name)
        return True
    except ImportError:
        return False


def install_parsers(languages: Set[str]) -> Dict[str, str]:
    """Install missing parsers for detected languages.

    Returns:
        Dict mapping language -> status ("installed" | "already_installed" | "failed")
    """
    results = {}
    to_install = []

    # Check which parsers are missing
    for lang in languages:
        if check_parser_installed(lang):
            results[lang] = "already_installed"
        else:
            pkg = LANG_TO_PACKAGE.get(lang)
            if pkg and pkg not in to_install:
                to_install.append(pkg)
                results[lang] = "pending"

    if not to_install:
        return results

    log.info("Installing parsers: %s", ", ".join(to_install))

    # Try mirrors in order
    for mirror in PIP_MIRRORS:
        cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + to_install
        if mirror:
            cmd += ["-i", mirror]

        try:
            subprocess.check_call(cmd, timeout=60)
            for lang in languages:
                if results.get(lang) == "pending":
                    results[lang] = "installed"
            log.info("Parsers installed successfully")
            return results
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log.warning("Install via %s failed: %s", mirror or "PyPI", e)
            continue

    # All mirrors failed
    for lang in languages:
        if results.get(lang) == "pending":
            results[lang] = "failed"

    return results
