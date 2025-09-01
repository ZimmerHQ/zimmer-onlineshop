# -*- coding: utf-8 -*-
"""
Shared CLI utilities for backend scripts.
Provides consistent output formatting, encoding handling, and configuration.
"""

import os
import sys
import io
from typing import Optional

# Fix stdout encoding for Windows compatibility
if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Emoji fallback for terminals that don't support UTF-8
SUPPORTS_EMOJI = sys.stdout.encoding and "utf" in sys.stdout.encoding.lower()
OK = "✅" if SUPPORTS_EMOJI else "OK"
FAIL = "❌" if SUPPORTS_EMOJI else "FAIL"
ROCKET = "🚀" if SUPPORTS_EMOJI else "[SMOKE]"
CHECK = "✓" if SUPPORTS_EMOJI else "✓"
CROSS = "✗" if SUPPORTS_EMOJI else "✗"


def get_base_url() -> str:
    """Get backend base URL from environment or default."""
    return os.getenv("BACKEND_URL", "http://localhost:8000")


def print_pass(label: str, detail: Optional[str] = None) -> None:
    """Print a PASS message with consistent formatting."""
    if detail:
        print(f"{CHECK} {label} ... {OK} ({detail})")
    else:
        print(f"{CHECK} {label} ... {OK}")


def print_fail(label: str, detail: str) -> None:
    """Print a FAIL message with consistent formatting."""
    print(f"{CROSS} {label} ... {FAIL} ({detail})")


def print_info(label: str, detail: Optional[str] = None) -> None:
    """Print an INFO message with consistent formatting."""
    if detail:
        print(f"{ROCKET} {label} ... {detail}")
    else:
        print(f"{ROCKET} {label}")


def print_header(title: str) -> None:
    """Print a section header."""
    print(f"\n{ROCKET} {title}")
    print("=" * 60)


def print_summary(passed: int, total: int) -> None:
    """Print test summary."""
    print(f"\n{ROCKET} SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"{OK} ALL SANITY TESTS PASSED")
    else:
        print(f"{FAIL} SOME TESTS FAILED")
    
    # Ensure stdout is flushed
    sys.stdout.flush()
