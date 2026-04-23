"""
smolagents + Ollama — Codespaces / local
Config via .env  →  OLLAMA_BASE_URL and OLLAMA_MODEL
"""

import ast
import base64
import csv
import io
import json
import operator
import os
import platform
import re
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

from openai import OpenAI
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

# ── Config ────────────────────────────────────────────────────
load_dotenv()                                       # reads .env in cwd
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
MODEL_ID        = os.getenv("OLLAMA_MODEL")

_http = httpx.Client(
    headers={"ngrok-skip-browser-warning": "1"},   # harmless on localhost
    transport=httpx.HTTPTransport(retries=2),
    timeout=300.0,
)
openai_client = OpenAI(
    base_url=f"{OLLAMA_BASE_URL}/v1",
    api_key="ollama",
    http_client=_http,
    timeout=300.0,
)
model = OpenAIServerModel(model_id=MODEL_ID, client=openai_client)

# ── Safety ────────────────────────────────────────────────────
def _safe_path(path: str) -> Path:
    p = Path(path).resolve()
    p.relative_to(Path.cwd().resolve())
    return p

# ── Tools  (keep docstrings SHORT — gemma4:e2b has 4096-token ctx) ──

@tool
def web_search_tool(query: str, max_results: int = 5) -> str:
    """Search the web with DuckDuckGo. Returns titles, URLs, snippets.
    Args:
        query: search string.
        max_results: how many results (max 10).
    """
    max_results = min(max_results, 10)
    try:
        with DDGS() as d:
            results = list(d.text(query, max_results=max_results))
    except Exception as e:
        return f"Search error: {e}"
    if not results:
        return "No results found."
    return "\n".join(
        f"[{r.get('title','')}] {r.get('href','')}\n  {r.get('body','')}"
        for r in results
    )


@tool
def fetch_url_tool(url: str, max_chars: int = 3000) -> str:
    """Fetch visible text from a web page (strips HTML).
    Args:
        url: full URL starting with http/https.
        max_chars: character limit (default 3000).
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"
    try:
        r = requests.get(url, headers={"ngrok-skip-browser-warning": "1"}, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for t in soup(["script", "style", "nav", "footer"]):
            t.decompose()
        text = re.sub(r"\n{3,}", "\n\n", soup.get_text("\n", strip=True))
        return text[:max_chars]
    except Exception as e:
        return f"Error: {e}"


@tool
def read_file_tool(path: str) -> str:
    """Read a local file inside cwd and return its text.
    Args:
        path: relative file path.
    """
    try:
        return _safe_path(path).read_text(encoding="utf-8")
    except ValueError:
        return "Error: path outside working directory."
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error: {e}"


@tool
def write_file_tool(path: str, content: str, mode: str = "write") -> str:
    """Write or append text to a local file inside cwd. Creates parent dirs.
    Args:
        path: relative file path.
        content: text to write.
        mode: 'write' (overwrite) or 'append'.
    """
    if mode not in ("write", "append"):
        return "Error: mode must be 'write' or 'append'."
    try:
        p = _safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.open("w" if mode == "write" else "a", encoding="utf-8").write(content)
        return f"OK: {'wrote' if mode=='write' else 'appended'} {len(content)} chars to {path}"
    except Exception as e:
        return f"Error: {e}"


@tool
def list_directory_tool(path: str = ".") -> str:
    """List files and folders in a directory inside cwd.
    Args:
        path: relative directory path (default current dir).
    """
    try:
        p = _safe_path(path)
        entries = sorted(p.iterdir(), key=lambda e: (e.is_file(), e.name))
        lines = [f"📁 {p}"]
        for e in entries:
            if e.name.startswith("."):
                continue
            if e.is_dir():
                lines.append(f"  📂 {e.name}/")
            else:
                kb = e.stat().st_size / 1024
                lines.append(f"  📄 {e.name}  ({kb:.1f} KB)")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


@tool
def shell_tool(command: str, timeout: int = 30) -> str:
    """Run a shell command, return stdout+stderr. Auto-detects OS shell.
    Args:
        command: shell command string.
        timeout: kill after N seconds (default 30).
    """
    blocked = ["rm -rf /", "mkfs", ":(){:|:&};:", "format c:", "shutdown", "reboot"]
    if any(b in command.lower() for b in blocked):
        return "Error: command blocked for safety."
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: timed out after {timeout}s."
    except Exception as e:
        return f"Error: {e}"


@tool
def calculator_tool(expression: str) -> str:
    """Safely evaluate arithmetic. Supports + - * / ** // % abs round sqrt.
    Args:
        expression: e.g. '5000 * (1 + 0.07) ** 10'
    """
    import math
    NAMES = {"abs": abs, "round": round, "min": min, "max": max,
             "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
             "floor": math.floor, "ceil": math.ceil}
    OPS   = {ast.Add: operator.add, ast.Sub: operator.sub,
             ast.Mult: operator.mul, ast.Div: operator.truediv,
             ast.Pow: operator.pow, ast.FloorDiv: operator.floordiv,
             ast.Mod: operator.mod, ast.USub: operator.neg}

    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name):
            if n.id in NAMES: return NAMES[n.id]
            raise ValueError(f"Unknown: {n.id}")
        if isinstance(n, ast.BinOp):
            return OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp):
            return OPS[type(n.op)](ev(n.operand))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            return NAMES[n.func.id](*[ev(a) for a in n.args])
        raise ValueError(f"Unsupported: {type(n).__name__}")

    try:
        result = ev(ast.parse(expression.strip(), mode="eval").body)
        return str(int(result)) if isinstance(result, float) and result.is_integer() else str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def datetime_tool(timezone: str = "UTC") -> str:
    """Return current date and time in the given IANA timezone.
    Args:
        timezone: e.g. 'UTC', 'Africa/Nairobi', 'US/Eastern' (default UTC).
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
        return now.strftime(f"%Y-%m-%d %H:%M:%S {timezone}")
    except ZoneInfoNotFoundError:
        return f"Error: unknown timezone '{timezone}'."
    except Exception as e:
        return f"Error: {e}"


@tool
def regex_search_tool(text: str, pattern: str, flags: str = "") -> str:
    """Find all regex matches in text, with surrounding context.
    Args:
        text: text to search.
        pattern: regex pattern.
        flags: 'i' ignore-case, 'm' multiline, 's' dotall.
    """
    rf = 0
    if "i" in flags: rf |= re.IGNORECASE
    if "m" in flags: rf |= re.MULTILINE
    if "s" in flags: rf |= re.DOTALL
    try:
        matches = list(re.finditer(pattern, text, rf))
        if not matches:
            return f"No matches for '{pattern}'."
        out = [f"{len(matches)} match(es) for '{pattern}':"]
        for i, m in enumerate(matches[:20], 1):
            s, e = max(0, m.start()-20), min(len(text), m.end()+20)
            out.append(f"  [{i}] pos={m.start()} → …{text[s:e].replace(chr(10),'↵')}…")
        return "\n".join(out)
    except re.error as e:
        return f"Invalid regex: {e}"


@tool
def json_format_tool(json_string: str, mode: str = "pretty") -> str:
    """Parse and reformat JSON. mode='pretty' (indented) or 'minify'.
    Args:
        json_string: raw JSON text.
        mode: 'pretty' or 'minify'.
    """
    try:
        obj = json.loads(json_string)
        if mode == "minify":
            return json.dumps(obj, separators=(",", ":"))
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"


@tool
def base64_tool(text: str, mode: str = "encode") -> str:
    """Encode text to base64 or decode base64 back to text.
    Args:
        text: input string.
        mode: 'encode' or 'decode'.
    """
    try:
        if mode == "encode":
            return base64.b64encode(text.encode()).decode()
        return base64.b64decode(text.encode()).decode()
    except Exception as e:
        return f"Error: {e}"


@tool
def csv_reader_tool(path: str, max_rows: int = 20) -> str:
    """Read a local CSV and return a text table preview.
    Args:
        path: relative path to CSV file.
        max_rows: rows to preview (default 20).
    """
    try:
        rows = list(csv.reader(io.StringIO(_safe_path(path).read_text(encoding="utf-8-sig"))))
        if not rows: return "CSV is empty."
        header, data = rows[0], rows[1:]
        preview = data[:max_rows]
        widths = [max(len(str(r[i])) for r in [header]+preview if i < len(r)) for i in range(len(header))]
        sep = "+-" + "-+-".join("-"*w for w in widths) + "-+"
        fmt = "| " + " | ".join(f"{{:<{w}}}" for w in widths) + " |"
        lines = [sep, fmt.format(*header), sep]
        for row in preview:
            row += [""] * (len(header) - len(row))
            lines.append(fmt.format(*row[:len(header)]))
        lines += [sep, f"{len(preview)}/{len(data)} rows shown"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


@tool
def weather_tool(location: str, units: str = "metric") -> str:
    """Get current weather via wttr.in (no API key needed).
    Args:
        location: city name or coords, e.g. 'Nairobi', 'London'.
        units: 'metric' (°C) or 'imperial' (°F).
    """
    try:
        r = requests.get(
            f"https://wttr.in/{requests.utils.quote(location)}?format=j1",
            headers={"User-Agent": "curl/7.68.0"}, timeout=10
        )
        r.raise_for_status()
        d = r.json()["current_condition"][0]
        area = r.json()["nearest_area"][0]
        city = area["areaName"][0]["value"]
        if units == "imperial":
            return (f"{city}: {d['weatherDesc'][0]['value']}, {d['temp_F']}°F "
                    f"(feels {d['FeelsLikeF']}°F), humidity {d['humidity']}%, "
                    f"wind {d['windspeedMiles']} mph")
        return (f"{city}: {d['weatherDesc'][0]['value']}, {d['temp_C']}°C "
                f"(feels {d['FeelsLikeC']}°C), humidity {d['humidity']}%, "
                f"wind {d['windspeedKmph']} km/h")
    except Exception as e:
        return f"Error: {e}"


@tool
def summarise_text_tool(text: str, max_words: int = 100) -> str:
    """Ask the model to summarise text concisely.
    Args:
        text: text to summarise (capped at 4000 chars).
        max_words: target word count (default 100).
    """
    try:
        resp = openai_client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content":
                f"Summarise in ≤{max_words} words:\n\n{text[:4000]}"}],
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


@tool
def translate_tool(text: str, target_language: str) -> str:
    """Translate text into another language using the local model.
    Args:
        text: text to translate.
        target_language: e.g. 'French', 'Swahili', 'Japanese'.
    """
    try:
        resp = openai_client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content":
                f"Translate into {target_language}. Return only the translation:\n\n{text}"}],
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


@tool
def check_url_status_tool(url: str) -> str:
    """Check if a URL is reachable; returns HTTP status and response time.
    Args:
        url: full URL to check.
    """
    import time
    try:
        t0 = time.time()
        r  = requests.get(url, timeout=10, allow_redirects=True)
        ms = int((time.time() - t0) * 1000)
        return f"{url} → {r.status_code} {r.reason} ({ms} ms)"
    except Exception as e:
        return f"Error: {e}"


# ── Agent ─────────────────────────────────────────────────────

ALL_TOOLS = [
    web_search_tool, fetch_url_tool,
    read_file_tool,  write_file_tool, list_directory_tool,
    calculator_tool, regex_search_tool,
    shell_tool,      datetime_tool,
    json_format_tool, base64_tool, csv_reader_tool,
    summarise_text_tool, translate_tool,
    weather_tool,    check_url_status_tool,
]

agent = ToolCallingAgent(
    tools=ALL_TOOLS,
    model=model,
    max_steps=15,
    verbosity_level=2,
)

# ── Example tasks ─────────────────────────────────────────────

TASKS = [
    # 0
    "Search for the top 3 open-source LLM frameworks in 2024, summarise the "
    "most popular one in 60 words, write to 'output/llm_frameworks.txt'.",
    # 1
    "Calculate compound interest: $5000 at 7% for 10 years (A=P*(1+r)**n). "
    "Get current UTC time. Append both to 'output/results.txt'.",
    # 2
    "Read 'agent.py'. Count @tool-decorated functions with regex, list their "
    "names, write findings to 'output/tools.txt'.",
    # 3
    "Get the weather in Nairobi. Translate it into French and Swahili. "
    "Save all three versions to 'output/weather.txt'.",
    # 4
    'Format this JSON prettily: {"name":"Alice","age":30,"city":"Nairobi"} '
    "then base64-encode the minified version and print both.",
    # 5
    "Check if https://ollama.com is reachable. If yes, fetch and summarise "
    "its homepage in 50 words. Save to 'output/ollama_summary.txt'.",
]

# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=f"smolagents + Ollama ({MODEL_ID})")
    parser.add_argument("--task",       type=str, default=None)
    parser.add_argument("--task-index", type=int, default=None)
    parser.add_argument("--list-tasks", action="store_true")
    args = parser.parse_args()

    if args.list_tasks:
        for i, t in enumerate(TASKS):
            print(f"\n[Task {i}]\n{textwrap.fill(t, 80)}")
        raise SystemExit

    task = TASKS[args.task_index] if args.task_index is not None else (args.task or TASKS[0])

    print(f"\n{'='*60}")
    print(f"Platform : {platform.system()} {platform.release()}")
    print(f"Model    : {MODEL_ID}")
    print(f"Endpoint : {OLLAMA_BASE_URL}")
    print(f"Tools    : {len(ALL_TOOLS)}")
    print(f"{'='*60}")
    print(f"Task:\n{textwrap.fill(task, 78)}")
    print(f"{'='*60}\n")

    Path("output").mkdir(exist_ok=True)
    result = agent.run(task)

    print(f"\n{'='*60}")
    print("FINAL ANSWER:")
    print(result)
    print(f"{'='*60}\n")