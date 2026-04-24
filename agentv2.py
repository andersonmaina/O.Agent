"""
smolagents + Ollama — Interactive Agent v2
Config via .env  →  OLLAMA_BASE_URL and OLLAMA_MODEL
Integrates tools from ./tools folder
Interactive mode: multiple tasks per session, no context carry-over
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
import sys
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

# Import tools from ./tools folder
from tools.file_tools import (
    read_file, write_file, append_file, copy_file, move_file,
    delete_file, file_exists, get_file_size, get_file_extension,
    list_files, list_directories, create_directory, delete_directory,
    get_directory_size, find_files, backup_file, get_file_hash, get_file_info
)
from tools.text_tools import (
    count_words, count_lines, count_characters, extract_emails,
    extract_urls, extract_phone_numbers, remove_duplicates,
    shuffle_text, reverse_text, capitalize_words, lowercase_words,
    truncate_text, wrap_text, indent_text, remove_empty_lines,
    normalize_whitespace, extract_hashtags, extract_mentions,
    word_frequency, sentence_count, average_word_length,
    remove_html_tags, strip_html
)
from tools.data_tools import (
    parse_csv, write_csv, parse_json, write_json, parse_xml,
    flatten_dict, merge_dicts, filter_dict, sort_dict,
    group_by, chunk_list, rotate_list, unique_list,
    intersection, union, difference, zip_dicts, invert_dict,
    deep_copy, dict_to_list, list_to_dict, safe_get, set_nested
)
from tools.web_tools import (
    is_valid_url, extract_domain, extract_path, parse_query_params,
    build_url, is_url_safe, normalize_url, extract_urls_from_text,
    url_encode, url_decode, get_url_components, is_same_domain,
    make_absolute_url, sanitize_url
)
from tools.system_tools import (
    get_system_info, get_disk_usage, get_memory_usage,
    get_cpu_count, get_platform_info, get_environment_variables,
    get_environment_variable, run_command, is_admin,
    get_current_directory, change_directory, get_home_directory,
    get_temp_directory, list_processes, get_username
)
from tools.crypto_tools import (
    hash_string, verify_hash, generate_random_string,
    generate_uuid, generate_token, base64_encode, base64_decode,
    base64_url_encode, base64_url_decode, hmac_hash,
    generate_password, mask_string, constant_time_compare, generate_api_key
)
from tools.date_tools import (
    get_current_date, get_current_time, get_current_datetime,
    get_timestamp, format_date, parse_date, date_difference,
    is_leap_year, get_days_in_month, add_days, subtract_days,
    add_hours, add_minutes, get_weekday, get_weekday_number,
    get_week_number, get_month_name, get_month_abbr,
    start_of_day, end_of_day, start_of_month, end_of_month,
    is_today, is_yesterday, is_tomorrow, days_until,
    business_days_between, age_from_birthdate
)
from tools.math_tools import (
    calculate_percentage, calculate_average, calculate_median,
    calculate_mode, calculate_std_dev, calculate_variance,
    is_prime, get_factors, gcd, lcm, fibonacci, factorial,
    permutations, combinations, power, sqrt, cbrt,
    log, log10, log2, sin, cos, tan,
    degrees_to_radians, radians_to_degrees, round_to,
    floor, ceil, clamp, lerp, distance_2d, distance_3d
)
from tools.network_tools import (
    is_valid_ip, is_valid_ipv4, is_valid_ipv6, get_local_ip,
    is_port_open, parse_mac_address, is_valid_mac_address,
    get_hostname, get_host_by_name, get_ip_by_name,
    ip_to_int, int_to_ip, get_subnet_mask, is_private_ip,
    is_loopback_ip, get_network_address, get_broadcast_address,
    count_ips_in_subnet, is_valid_port, get_common_ports
)
from tools.string_tools import (
    slugify, camel_case, pascal_case, snake_case, kebab_case,
    truncate, remove_special_chars,
    levenshtein_distance, is_palindrome, character_frequency,
    remove_whitespace, pad_left, pad_right, pad_center,
    remove_accents, is_uppercase, is_lowercase, is_title_case,
    swap_case, repeat_string, insert_string, replace_all,
    extract_between, count_substring, starts_with_any, ends_with_any
)
from tools.validation_tools import (
    is_email, is_phone, is_credit_card, is_strong_password,
    is_valid_date, is_numeric, is_integer, is_alphanumeric,
    is_empty, is_not_empty, is_url, is_ipv4, is_ipv6,
    is_uuid, is_hex, is_base64, is_slug, is_username,
    is_file_extension, is_in_range, is_positive, is_negative, is_zero
)
from tools.git_tools import (
    run_git_command, git_init, git_clone, git_add, git_add_all,
    git_commit, git_push, git_pull, git_fetch, git_merge,
    git_checkout, git_checkout_new_branch, git_create_branch,
    git_delete_branch, git_list_branches, git_current_branch,
    git_status, git_log, git_diff, git_show, git_stash,
    git_stash_pop, git_stash_list, git_remote_list, git_remote_add,
    git_remote_remove, git_tag_create, git_tag_list, git_tag_delete,
    git_reset, git_revert, git_cherry_pick, git_blame,
    git_config_get, git_config_set, git_is_repository, git_root,
    git_ignore_add, git_clean
)
from tools.agent_tools import (
    agent_set_memory, agent_get_memory, agent_list_memory,
    agent_clear_memory, agent_memory_history, agent_think,
    agent_plan, agent_get_plan, agent_goal, agent_get_goal,
    agent_context, agent_get_context, agent_clear_context,
    agent_state, agent_get_state, agent_metadata, agent_get_metadata,
    agent_task_start, agent_task_complete, agent_error,
    agent_get_errors, agent_stats, agent_reset
)

# ── Config ────────────────────────────────────────────────────
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_ID = os.getenv("OLLAMA_MODEL", "gemma3:e2b")

_http = httpx.Client(
    headers={"ngrok-skip-browser-warning": "1"},
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

# ── Tool Wrappers for smolagents ─────────────────────────────

@tool
def web_search_tool(query: str, max_results: int = 5) -> str:
    """Search the web with DuckDuckGo. Returns titles, URLs, snippets.

    Args:
        query: The search query string to search for.
        max_results: Maximum number of search results to return (default: 5, max: 10).
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
        url: The full URL to fetch (must start with http:// or https://).
        max_chars: Maximum number of characters to return (default: 3000).
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
def read_file_wrapper(path: str) -> str:
    """Read a local file inside cwd and return its text.

    Args:
        path: Relative file path to read.
    """
    try:
        return read_file(str(_safe_path(path)))
    except ValueError:
        return "Error: path outside working directory."
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error: {e}"


@tool
def write_file_wrapper(path: str, content: str, mode: str = "write") -> str:
    """Write or append text to a local file inside cwd.

    Args:
        path: Relative file path to write to.
        content: Text content to write.
        mode: 'write' to overwrite or 'append' to add to existing file.
    """
    try:
        p = _safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if mode == "append":
            append_file(str(p), content)
        else:
            write_file(str(p), content)
        return f"OK: wrote content to {path}"
    except Exception as e:
        return f"Error: {e}"


@tool
def list_directory_wrapper(path: str = ".") -> str:
    """List files and folders in a directory inside cwd.

    Args:
        path: Relative directory path (default: current directory).
    """
    try:
        p = _safe_path(path)
        entries = sorted(p.iterdir(), key=lambda e: (e.is_file(), e.name))
        lines = [f"Directory: {p}"]
        for e in entries:
            if e.name.startswith("."):
                continue
            if e.is_dir():
                lines.append(f"  [DIR] {e.name}/")
            else:
                kb = e.stat().st_size / 1024
                lines.append(f"  [FILE] {e.name}  ({kb:.1f} KB)")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


@tool
def shell_tool(command: str, timeout: int = 30) -> str:
    """Run a shell command, return stdout+stderr.

    Args:
        command: Shell command string to execute.
        timeout: Kill command after N seconds (default: 30).
    """
    blocked = ["rm -rf /", "mkfs", "format c:", "shutdown", "reboot"]
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
        expression: Arithmetic expression string, e.g. '5000 * (1 + 0.07) ** 10'.
    """
    import math
    NAMES = {"abs": abs, "round": round, "min": min, "max": max,
             "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
             "floor": math.floor, "ceil": math.ceil}
    OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
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
        timezone: IANA timezone name, e.g. 'UTC', 'Africa/Nairobi', 'US/Eastern' (default: UTC).
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
        text: Text to search in.
        pattern: Regular expression pattern to match.
        flags: Regex flags - 'i' for ignore-case, 'm' for multiline, 's' for dotall.
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
            out.append(f"  [{i}] pos={m.start()}")
        return "\n".join(out)
    except re.error as e:
        return f"Invalid regex: {e}"


@tool
def json_format_tool(json_string: str, mode: str = "pretty") -> str:
    """Parse and reformat JSON. mode='pretty' (indented) or 'minify'.

    Args:
        json_string: Raw JSON text to parse.
        mode: 'pretty' for indented output or 'minify' for compact output.
    """
    try:
        obj = json.loads(json_string)
        if mode == "minify":
            return json.dumps(obj, separators=(",", ":"))
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"


@tool
def base64_wrapper(text: str, mode: str = "encode") -> str:
    """Encode text to base64 or decode base64 back to text.

    Args:
        text: Input string to encode or decode.
        mode: 'encode' to encode to base64 or 'decode' to decode from base64.
    """
    try:
        if mode == "encode":
            return base64_encode(text)
        return base64_decode(text)
    except Exception as e:
        return f"Error: {e}"


@tool
def csv_reader_tool(path: str, max_rows: int = 20) -> str:
    """Read a local CSV and return a text table preview.

    Args:
        path: Relative path to CSV file.
        max_rows: Number of rows to preview (default: 20).
    """
    try:
        content = read_file(str(_safe_path(path)))
        rows = list(csv.reader(io.StringIO(content)))
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
        location: City name or coordinates, e.g. 'Nairobi', 'London'.
        units: 'metric' for Celsius or 'imperial' for Fahrenheit.
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
            return f"{city}: {d['weatherDesc'][0]['value']}, {d['temp_F']}F"
        return f"{city}: {d['weatherDesc'][0]['value']}, {d['temp_C']}C"
    except Exception as e:
        return f"Error: {e}"


@tool
def summarise_text_tool(text: str, max_words: int = 100) -> str:
    """Ask the model to summarise text concisely.

    Args:
        text: Text to summarise (capped at 4000 characters).
        max_words: Target word count for summary (default: 100).
    """
    try:
        resp = openai_client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": f"Summarise in {max_words} words:\n\n{text[:4000]}"}],
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


@tool
def translate_tool(text: str, target_language: str) -> str:
    """Translate text into another language using the local model.

    Args:
        text: Text to translate.
        target_language: Target language name, e.g. 'French', 'Swahili', 'Japanese'.
    """
    try:
        resp = openai_client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": f"Translate into {target_language}:\n\n{text}"}],
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


@tool
def check_url_status_tool(url: str) -> str:
    """Check if a URL is reachable; returns HTTP status and response time.

    Args:
        url: Full URL to check.
    """
    import time
    try:
        t0 = time.time()
        r = requests.get(url, timeout=10, allow_redirects=True)
        ms = int((time.time() - t0) * 1000)
        return f"{url} -> {r.status_code} ({ms} ms)"
    except Exception as e:
        return f"Error: {e}"


# ── Tools from ./tools folder (wrapped) ───────────────────────

@tool
def file_exists_tool(path: str) -> str:
    """Check if a file exists.

    Args:
        path: Relative file path to check.
    """
    try:
        exists = file_exists(str(_safe_path(path)))
        return f"File exists: {exists}"
    except Exception as e:
        return f"Error: {e}"


@tool
def get_system_info_tool() -> str:
    """Get system information."""
    try:
        info = get_system_info()
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def get_current_datetime_tool() -> str:
    """Get current date and time."""
    try:
        return get_current_datetime()
    except Exception as e:
        return f"Error: {e}"


@tool
def hash_string_tool(text: str, algorithm: str = "sha256") -> str:
    """Hash a string using specified algorithm.

    Args:
        text: String to hash.
        algorithm: Hash algorithm to use (default: sha256).
    """
    try:
        return hash_string(text, algorithm)
    except Exception as e:
        return f"Error: {e}"


@tool
def generate_uuid_tool() -> str:
    """Generate a UUID v4."""
    try:
        return generate_uuid()
    except Exception as e:
        return f"Error: {e}"


@tool
def generate_password_tool(length: int = 16, use_special: bool = True) -> str:
    """Generate a strong random password.

    Args:
        length: Password length (default: 16).
        use_special: Whether to include special characters (default: True).
    """
    try:
        return generate_password(length, use_special)
    except Exception as e:
        return f"Error: {e}"


@tool
def calculate_average_tool(numbers: str) -> str:
    """Calculate average of comma-separated numbers.

    Args:
        numbers: Comma-separated string of numbers.
    """
    try:
        nums = [float(x.strip()) for x in numbers.split(",")]
        return str(calculate_average(nums))
    except Exception as e:
        return f"Error: {e}"


@tool
def is_prime_tool(n: int) -> str:
    """Check if a number is prime.

    Args:
        n: Number to check.
    """
    try:
        result = is_prime(n)
        return f"{n} is {'prime' if result else 'not prime'}"
    except Exception as e:
        return f"Error: {e}"


@tool
def is_valid_url_tool(url: str) -> str:
    """Check if a URL is valid.

    Args:
        url: URL to validate.
    """
    try:
        result = is_valid_url(url)
        return f"URL is {'valid' if result else 'invalid'}"
    except Exception as e:
        return f"Error: {e}"


@tool
def is_email_tool(email: str) -> str:
    """Check if a string is a valid email.

    Args:
        email: Email address to validate.
    """
    try:
        result = is_email(email)
        return f"Email is {'valid' if result else 'invalid'}"
    except Exception as e:
        return f"Error: {e}"


@tool
def slugify_tool(text: str) -> str:
    """Convert text to URL-friendly slug.

    Args:
        text: Text to convert to slug.
    """
    try:
        return slugify(text)
    except Exception as e:
        return f"Error: {e}"


@tool
def extract_domain_tool(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: URL to extract domain from.
    """
    try:
        return extract_domain(url)
    except Exception as e:
        return f"Error: {e}"


@tool
def count_words_tool(text: str) -> str:
    """Count words in text.

    Args:
        text: Text to count words in.
    """
    try:
        return f"Word count: {count_words(text)}"
    except Exception as e:
        return f"Error: {e}"


@tool
def remove_html_tags_tool(html: str) -> str:
    """Remove HTML tags from text.

    Args:
        html: HTML text to strip tags from.
    """
    try:
        return remove_html_tags(html)
    except Exception as e:
        return f"Error: {e}"


@tool
def parse_json_tool(json_string: str) -> str:
    """Parse JSON string and return formatted output.

    Args:
        json_string: JSON string to parse.
    """
    try:
        obj = parse_json(json_string)
        return json.dumps(obj, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def flatten_dict_tool(json_string: str) -> str:
    """Flatten a nested JSON dictionary.

    Args:
        json_string: JSON string to flatten.
    """
    try:
        obj = parse_json(json_string)
        flattened = flatten_dict(obj)
        return json.dumps(flattened, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def git_status_tool() -> str:
    """Get git status of current repository."""
    try:
        return git_status()
    except Exception as e:
        return f"Error: {e}"


@tool
def git_current_branch_tool() -> str:
    """Get current git branch."""
    try:
        return git_current_branch()
    except Exception as e:
        return f"Error: {e}"


@tool
def agent_set_memory_tool(key: str, value: str) -> str:
    """Store a value in agent memory (session-only).

    Args:
        key: Memory key name.
        value: Value to store.
    """
    try:
        return agent_set_memory(key, value)
    except Exception as e:
        return f"Error: {e}"


@tool
def agent_get_memory_tool(key: str) -> str:
    """Retrieve a value from agent memory.

    Args:
        key: Memory key name to retrieve.
    """
    try:
        return agent_get_memory(key)
    except Exception as e:
        return f"Error: {e}"


@tool
def agent_clear_memory_tool() -> str:
    """Clear all agent memory."""
    try:
        return agent_clear_memory()
    except Exception as e:
        return f"Error: {e}"


@tool
def agent_list_memory_tool() -> str:
    """List all keys in agent memory."""
    try:
        return agent_list_memory()
    except Exception as e:
        return f"Error: {e}"


# ── Agent Setup ───────────────────────────────────────────────

ALL_TOOLS = [
    web_search_tool, fetch_url_tool,
    read_file_wrapper, write_file_wrapper, list_directory_wrapper,
    calculator_tool, regex_search_tool,
    shell_tool, datetime_tool,
    json_format_tool, base64_wrapper, csv_reader_tool,
    summarise_text_tool, translate_tool,
    weather_tool, check_url_status_tool,
    file_exists_tool, get_system_info_tool, get_current_datetime_tool,
    hash_string_tool, generate_uuid_tool, generate_password_tool,
    calculate_average_tool, is_prime_tool,
    is_valid_url_tool, is_email_tool,
    slugify_tool, extract_domain_tool,
    count_words_tool, remove_html_tags_tool,
    parse_json_tool, flatten_dict_tool,
    git_status_tool, git_current_branch_tool,
    agent_set_memory_tool, agent_get_memory_tool,
    agent_clear_memory_tool, agent_list_memory_tool,
]


def create_agent():
    """Create a new agent instance (fresh, no context carry-over)."""
    return ToolCallingAgent(
        tools=ALL_TOOLS,
        model=model,
        max_steps=100,
        verbosity_level=2,
    )


# ── Interactive Loop ──────────────────────────────────────────

def print_banner():
    print("\n" + "="*60)
    print("  OLLAMA AGENT v2 - Interactive Mode")
    print("="*60)
    print(f"Platform : {platform.system()} {platform.release()}")
    print(f"Model    : {MODEL_ID}")
    print(f"Endpoint : {OLLAMA_BASE_URL}")
    print(f"Tools    : {len(ALL_TOOLS)}")
    print("="*60)
    print("\nCommands:")
    print("  /help     - Show this help")
    print("  /tools    - List available tools")
    print("  /clear    - Clear agent memory")
    print("  /reset    - Create fresh agent (no context)")
    print("  /exit     - Exit the program")
    print("="*60)


def print_tools():
    print("\nAvailable Tools:")
    print("-" * 40)
    tool_names = [t.name for t in ALL_TOOLS]
    for i, name in enumerate(sorted(tool_names), 1):
        print(f"  {i:2}. {name}")
    print("-" * 40)


def interactive_loop():
    """Main interactive loop - each task is independent."""
    print_banner()
    
    agent = create_agent()
    task_count = 0
    
    Path("output").mkdir(exist_ok=True)
    
    while True:
        try:
            user_input = input("\nTask > ").strip()
            
            if not user_input:
                continue
            
            if user_input.startswith("/"):
                cmd = user_input.lower()
                
                if cmd in ("/exit", "/quit"):
                    print("\nGoodbye!\n")
                    break
                
                elif cmd == "/help":
                    print_banner()
                    continue
                
                elif cmd == "/tools":
                    print_tools()
                    continue
                
                elif cmd == "/clear":
                    agent_clear_memory()
                    print("Agent memory cleared")
                    continue
                
                elif cmd == "/reset":
                    agent = create_agent()
                    agent_clear_memory()
                    print("Agent reset (fresh instance, no context)")
                    continue
                
                else:
                    print(f"Unknown command: {user_input}")
                    print("Type /help for available commands")
                    continue
            
            task_count += 1
            print(f"\n{'='*60}")
            print(f"Task #{task_count}")
            print(f"{'='*60}")
            print(f"Input: {textwrap.fill(user_input, 78)}")
            print(f"{'='*60}\n")
            
            result = agent.run(user_input)
            
            print(f"\n{'='*60}")
            print("RESULT:")
            print(f"{'='*60}")
            print(result)
            print(f"{'='*60}\n")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type /exit to quit.")
            continue
        except Exception as e:
            print(f"\nError: {e}\n")
            continue


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=f"smolagents + Ollama Interactive ({MODEL_ID})")
    parser.add_argument("--task", type=str, default=None, help="Run a single task and exit")
    parser.add_argument("--no-interactive", action="store_true", help="Disable interactive mode")
    args = parser.parse_args()
    
    Path("output").mkdir(exist_ok=True)
    
    if args.task:
        agent = create_agent()
        print(f"\nRunning single task: {args.task}\n")
        result = agent.run(args.task)
        print(f"\nResult:\n{result}\n")
    elif args.no_interactive:
        agent = create_agent()
        for line in sys.stdin:
            task = line.strip()
            if task:
                print(f"\nTask: {task}")
                result = agent.run(task)
                print(f"Result: {result}\n")
                agent = create_agent()
    else:
        interactive_loop()
