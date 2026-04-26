"""
Stdout filter for smolagents output.
Keeps:  - "New run" header box
        - "Step N" separator
        - "Calling tool: ..." box
        - [Step N: Duration X.Xs | Input tokens: X | Output tokens: X]
Strips: - Observations: ... plain-text block
        - Final answer: ... bold block
"""

import sys
import re
from typing import IO


# Patterns that mark the START of a block we want to suppress.
# NOTE: [Step N: Duration ...] is intentionally NOT here — it stays visible.
_SUPPRESS_START = re.compile(
    r"^(Observations\s*:|Final answer\s*:)",
    re.IGNORECASE,
)


class AgentOutputFilter:
    """
    Wraps sys.stdout and drops unwanted smolagents log lines.

    smugagets prints chunks line-by-line (Rich console), so we filter
    at the newline boundary. A suppression block starts when a line
    matches _SUPPRESS_START and ends at the next Rich rule/separator
    (a line of ━ or ─ characters, or a box border │ at col 0, or empty).
    """

    def __init__(self, wrapped: IO[str]):
        self._wrapped = wrapped
        self._suppressing = False
        self._buf = ""

    # ── IO interface ──────────────────────────────────────────────────────────

    def write(self, text: str) -> int:
        self._buf += text
        # Process complete lines only
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._process_line(line)
        return len(text)

    def _process_line(self, raw: str):
        # Strip ANSI codes for matching, keep raw for printing
        clean = _strip_ansi(raw)

        # ── toggle suppression off ────────────────────────────────────
        if self._suppressing:
            # A separator, box border, or blank line ends suppression
            if _is_section_break(clean):
                self._suppressing = False
                # Print the break itself (it's a structural element)
                self._wrapped.write(raw + "\n")
            # else: swallow the line
            return

        # ── toggle suppression on ─────────────────────────────────────
        if _SUPPRESS_START.match(clean):
            self._suppressing = True
            return  # swallow this line too

        # ── always pass through ───────────────────────────────────────
        self._wrapped.write(raw + "\n")

    def flush(self):
        # Flush any partial line
        if self._buf:
            self._wrapped.write(self._buf)
            self._buf = ""
        self._wrapped.flush()

    def fileno(self):
        return self._wrapped.fileno()

    def __getattr__(self, name):
        return getattr(self._wrapped, name)


# ── helpers ───────────────────────────────────────────────────────────────────

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[mGKHF]")


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


def _is_section_break(clean: str) -> bool:
    """True for Rich rule lines (━━━, ───), box borders, or blank lines."""
    stripped = clean.strip()
    if not stripped:
        return True
    # Rich horizontal rules use box-drawing chars
    if all(c in "━─╌╍╸╺╼╾ " for c in stripped):
        return True
    return False


# ── context manager ───────────────────────────────────────────────────────────

class filtered_output:
    """Context manager: replace sys.stdout with AgentOutputFilter for the block."""

    def __enter__(self):
        self._original = sys.stdout
        sys.stdout = AgentOutputFilter(self._original)
        return self

    def __exit__(self, *_):
        # Flush remaining buffer before restoring
        sys.stdout.flush()
        sys.stdout = self._original
