"""
BRAWL Agent - Brand Identity & CLI Banner
All art uses ASCII-only characters for maximum Windows terminal compatibility.
"""

import os
import sys

# ── Force UTF-8 output on Windows ─────────────────────────────────────────────
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── ANSI color palette ────────────────────────────────────────────────────────
R    = "\033[0m"           # Reset
B    = "\033[1m"           # Bold
DIM  = "\033[2m"

# 256-colour purple→magenta gradient (safe on most modern terminals)
C1   = "\033[38;5;57m"    # Deep violet
C2   = "\033[38;5;99m"    # Purple
C3   = "\033[38;5;129m"   # Bright purple
C4   = "\033[38;5;165m"   # Hot magenta
C5   = "\033[38;5;201m"   # Vivid pink

CYAN = "\033[1;36m"
GRN  = "\033[1;32m"
YEL  = "\033[1;33m"
MAG  = "\033[1;35m"
WHT  = "\033[1;37m"
GREY = "\033[38;5;244m"
RED  = "\033[1;31m"

# ── ASCII Art (block-letter BRAWL, pure ASCII) ────────────────────────────────
# Width ~ 50 chars
BRAWL_LOGO = [
    (C1, r"  ___  ____   __   _    _  _    "),
    (C2, r" | _ \| _ \ / _' | |  | \/ |   "),
    (C3, r" | _ <|   /| |_| | |/\| \/  |  "),
    (C4, r" |___/|_|\_\\___|_|____\/|_||_| "),
    (C5, r"                                 "),
]

# Bigger, bolder version with slant-style art
BRAWL_LOGO = [
    (C1, r"  ____  ____    __   _    _ _     "),
    (C2, r"  | __ )| _ \  / \  | |  | | |    "),
    (C3, r"  |  _ \|   / / _ \ | |/\| | |    "),
    (C4, r"  | |_) | |_\/ ___ \|  /\  | |___ "),
    (C5, r"  |____/|___/_/   \_\_/  \_/_____|"),
]

VERSION  = "v3.1.0"
CODENAME = "Striker"
TAGLINE  = "Autonomous Intelligence. Relentlessly Capable."
SUBLINE  = "Powered by Ollama  |  smolagents  |  RTK Context"

BAR_CHAR = "-"
BAR_WIDTH = 54


def _bar(char: str = BAR_CHAR, width: int = BAR_WIDTH, color: str = GREY) -> str:
    return f"{color}{char * width}{R}"


def print_banner():
    """Print the full BRAWL launch banner."""
    print()
    # Logo
    for color, line in BRAWL_LOGO:
        print(f"  {B}{color}{line}{R}")

    print()
    print(f"  {MAG}{B}{TAGLINE}{R}")
    print(f"  {GREY}{SUBLINE}{R}")
    print()
    # Version pill
    print(f"  {C3}{B} {VERSION} {R}  {GREY}|{R}  {MAG}{B}* {CODENAME} {R}")
    print()
    print(f"  {_bar('=', BAR_WIDTH, C2)}")
    print()


def print_session_info(provider: str, model: str, context_tokens: int):
    """Print the session info block."""
    w = BAR_WIDTH
    print(f"  {GREY}+{'-' * (w - 2)}+{R}")

    def row(label: str, val: str, val_color: str = CYAN):
        padded = f"{val_color}{val}{R}"
        raw_len = len(label) + len(val) + 6  # approximate visible width
        pad = max(0, w - raw_len - 4)
        print(f"  {GREY}|{R}  {GREY}{label:<10}{R}  {padded}{' ' * pad}  {GREY}|{R}")

    row("Provider", provider.upper(), CYAN)
    row("Model",    model,            YEL)
    row("Context",  f"{context_tokens:,} tokens", GRN)
    row("Tools",    "Dynamic Loading", MAG)

    print(f"  {GREY}+{'-' * (w - 2)}+{R}")
    print()


def print_goodbye():
    """Print exit message."""
    print()
    print(f"  {C4}{B}[ BRAWL ]{R}  {GREY}Session ended. Stay lethal.{R}")
    print()
