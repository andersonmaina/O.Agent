"""
OLLAMA AGENT v3 - Enhanced with Chat Memory & Token Optimization
================================================================
Features:
- Persistent chat memory with resume/delete capabilities
- Tasks within chats with full history
- Token optimization strategies (truncation, summarization, sliding window)
- Enhanced tools from ./tools folder
- Multi-session context retention

Config via .env → OLLAMA_BASE_URL and OLLAMA_MODEL
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
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

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

# Import NEW super tools
from tools.code_tools import (
    analyze_code, find_code_patterns, refactor_variable, extract_function,
    generate_function_stub, validate_syntax, count_code_metrics,
    format_code, find_unused_imports, extract_classes,
    get_function_signature, generate_docstring_template, compare_code_similarity
)
from tools.ai_tools import (
    classify_text, extract_key_phrases, summarize_key_points,
    detect_language, sentiment_analysis, generate_tags,
    readability_score, extract_entities, text_to_outline
)
from tools.database_tools import (
    create_database, create_table, insert_record, insert_many,
    select_records, update_records, delete_records, get_table_schema,
    list_tables, drop_table, execute_query, export_to_csv,
    import_from_csv, backup_database, get_database_stats,
    add_column, create_index
)
from tools.chat_memory import (
    ChatMemoryManager, get_chat_memory, Message, Task, Chat
)
from tools.search_tools import (
    semantic_search, grep_search, search_by_type, find_duplicates,
    search_recent, find_empty_files, find_large_files,
    search_filenames, get_file_statistics
)
from tools.explorer_tools import (
    explore_project, find_symbol, get_file_outline, find_references,
    get_call_hierarchy, find_implementation, get_dependency_graph,
    analyze_codebase, search_codebase
)


# ── Config ────────────────────────────────────────────────────
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_ID = os.getenv("OLLAMA_MODEL", "gemma3:e2b")

# Token optimization config
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "4096"))
TOKEN_ESTIMATE_PER_CHAR = int(os.getenv("TOKEN_ESTIMATE_PER_CHAR", "4"))
SLIDING_WINDOW_SIZE = int(os.getenv("SLIDING_WINDOW_SIZE", "50"))
SUMMARY_TRIGGER_RATIO = float(os.getenv("SUMMARY_TRIGGER_RATIO", "0.8"))

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

# Initialize chat memory manager
chat_memory = ChatMemoryManager()


# ── Safety ────────────────────────────────────────────────────
def _safe_path(path: str) -> Path:
    p = Path(path).resolve()
    p.relative_to(Path.cwd().resolve())
    return p


# ── Token Optimization Utilities ─────────────────────────────
def estimate_tokens(text: str) -> int:
    """Estimate token count from text length."""
    return len(text) // TOKEN_ESTIMATE_PER_CHAR


def truncate_messages(messages: List[Dict], max_tokens: int = MAX_CONTEXT_TOKENS) -> List[Dict]:
    """
    Truncate message history to fit within token limit.
    Uses sliding window approach - keeps newest messages.
    """
    if not messages:
        return []

    # Start with system message if present
    result = []
    if messages and messages[0].get('role') == 'system':
        result.append(messages[0])
        messages = messages[1:]

    # Add messages from newest to oldest until we hit limit
    current_tokens = sum(estimate_tokens(m.get('content', '')) for m in result)

    for msg in reversed(messages):
        msg_tokens = estimate_tokens(msg.get('content', ''))
        if current_tokens + msg_tokens > max_tokens:
            break
        result.insert(0 if not result or result[0].get('role') != 'system' else 1, msg)
        current_tokens += msg_tokens

    # If we couldn't fit any messages, truncate the newest one
    if len(result) <= 1 and messages:
        newest = messages[-1]
        max_content_length = max_tokens * TOKEN_ESTIMATE_PER_CHAR
        truncated_content = newest.get('content', '')[-max_content_length:]
        result.append({'role': newest.get('role', 'user'), 'content': truncated_content})

    return result


def summarize_old_messages(messages: List[Dict], summary_ratio: float = 0.5) -> Tuple[str, List[Dict]]:
    """
    Summarize older messages and keep recent ones intact.
    Returns (summary, recent_messages).
    """
    if len(messages) < 3:
        return "", messages

    split_point = int(len(messages) * (1 - summary_ratio))
    old_messages = messages[:split_point]
    recent_messages = messages[split_point:]

    # Create summary text
    summary_parts = []
    for msg in old_messages[-10:]:  # Summarize last 10 of old messages
        content = msg.get('content', '')[:200]
        summary_parts.append(f"{msg.get('role', 'user')}: {content}")

    summary = "Previous conversation summary:\n" + "\n".join(summary_parts)[-1500:]

    return summary, recent_messages


def optimize_context(messages: List[Dict], max_tokens: int = MAX_CONTEXT_TOKENS) -> List[Dict]:
    """
    Apply token optimization strategies to message history.
    1. Truncate if over limit
    2. Summarize old messages if approaching limit
    3. Use sliding window for very long histories
    """
    current_tokens = sum(estimate_tokens(m.get('content', '')) for m in messages)

    if current_tokens <= max_tokens * SUMMARY_TRIGGER_RATIO:
        return messages  # No optimization needed

    # Try summarization first
    summary, recent = summarize_old_messages(messages, summary_ratio=0.5)

    if summary:
        optimized = [{'role': 'system', 'content': summary}] + recent
    else:
        optimized = messages

    # Final truncation if still too long
    return truncate_messages(optimized, max_tokens)


def compress_message_content(content: str, max_length: int = 2000) -> str:
    """Compress message content by removing whitespace and truncating."""
    if len(content) <= max_length:
        return content

    # Remove excessive whitespace
    compressed = re.sub(r'\s+', ' ', content)

    if len(compressed) > max_length:
        compressed = compressed[:max_length] + "\n[... content truncated ...]"

    return compressed


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


# ── Super Tools (Enhanced) ───────────────────────────────────

@tool
def analyze_code_tool(code: str, language: str = "python") -> str:
    """Analyze code structure and return metrics.

    Args:
        code: Code to analyze.
        language: Programming language (default: python).
    """
    try:
        result = analyze_code(code, language)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def find_symbol_tool(symbol_name: str, symbol_type: str = "all") -> str:
    """Find a symbol (function, class, variable) across the codebase.

    Args:
        symbol_name: Name of the symbol to find.
        symbol_type: Type of symbol - 'all', 'class', 'function', or 'variable'.
    """
    try:
        results = find_symbol(symbol_name, symbol_type=symbol_type)
        if not results:
            return f"Symbol '{symbol_name}' not found."
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def explore_project_tool(max_depth: int = 5) -> str:
    """Explore project structure and return comprehensive overview.

    Args:
        max_depth: Maximum directory depth to explore (default: 5).
    """
    try:
        result = explore_project('.', max_depth)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def search_codebase_tool(query: str, max_results: int = 10) -> str:
    """Search codebase for relevant code based on query.

    Args:
        query: Search query (keywords or natural language).
        max_results: Maximum results to return (default: 10).
    """
    try:
        results = search_codebase(query, max_results=max_results)
        if not results:
            return "No results found."
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def sentiment_analysis_tool(text: str) -> str:
    """Analyze sentiment of text.

    Args:
        text: Text to analyze.
    """
    try:
        result = sentiment_analysis(text)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def extract_entities_tool(text: str) -> str:
    """Extract named entities (emails, URLs, phones, dates, etc.) from text.

    Args:
        text: Text to extract entities from.
    """
    try:
        result = extract_entities(text)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def grep_search_tool(pattern: str, directory: str = ".", file_pattern: str = "*") -> str:
    """Search files using regex pattern matching.

    Args:
        pattern: Regex pattern to search for.
        directory: Directory to search in (default: current).
        file_pattern: File glob pattern (default: all files).
    """
    try:
        results = grep_search(pattern, directory, file_pattern)
        if not results:
            return "No matches found."
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def create_database_tool(db_path: str) -> str:
    """Create a new SQLite database.

    Args:
        db_path: Path for the new database file.
    """
    try:
        return create_database(db_path)
    except Exception as e:
        return f"Error: {e}"


@tool
def execute_sql_tool(db_path: str, query: str) -> str:
    """Execute a SQL query against SQLite database.

    Args:
        db_path: Path to database file.
        query: SQL query to execute.
    """
    try:
        result = execute_query(db_path, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def get_file_outline_tool(file_path: str) -> str:
    """Get outline/structure of a code file.

    Args:
        file_path: Path to the code file.
    """
    try:
        outline = get_file_outline(file_path)
        if not outline:
            return "Could not parse file or file is empty."
        return json.dumps(outline, indent=2)
    except Exception as e:
        return f"Error: {e}"


# ── Chat Memory Tools ────────────────────────────────────────

@tool
def chat_list_tool() -> str:
    """List all chat sessions."""
    try:
        chats = chat_memory.list_chats()
        if not chats:
            return "No chat sessions found."
        output = ["Chat Sessions:", "-" * 40]
        for chat in chats:
            active = " (active)" if chat['id'] == chat_memory._index.get('active_chat') else ""
            output.append(f"  [{chat['id']}] {chat['title']}{active}")
            output.append(f"      Created: {chat['created_at'][:19]} | Tasks: {chat['task_count']} | Messages: {chat['message_count']}")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_create_tool(title: str = None) -> str:
    """Create a new chat session.

    Args:
        title: Optional title for the chat (auto-generated if not provided).
    """
    try:
        chat = chat_memory.create_chat(title)
        return f"Created new chat: [{chat.id}] {chat.title}"
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_switch_tool(chat_id: str) -> str:
    """Switch to a different chat session.

    Args:
        chat_id: ID of the chat to switch to.
    """
    try:
        if chat_memory.set_active_chat(chat_id):
            return f"Switched to chat: [{chat_id}]"
        return f"Chat '{chat_id}' not found."
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_delete_tool(chat_id: str) -> str:
    """Delete a chat session.

    Args:
        chat_id: ID of the chat to delete.
    """
    try:
        if chat_memory.delete_chat(chat_id):
            return f"Deleted chat: [{chat_id}]"
        return f"Chat '{chat_id}' not found."
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_resume_tool(chat_id: str) -> str:
    """Resume a chat session and show recent history.

    Args:
        chat_id: ID of the chat to resume.
    """
    try:
        chat = chat_memory.get_chat(chat_id)
        if not chat:
            return f"Chat '{chat_id}' not found."

        chat_memory.set_active_chat(chat_id)

        output = [f"Resumed chat: [{chat.id}] {chat.title}"]
        output.append(f"Created: {chat.created_at[:19]} | Messages: {len(chat.messages)} | Tasks: {len(chat.tasks)}")
        output.append("-" * 40)
        output.append("Recent messages:")

        for msg in chat.messages[-5:]:
            output.append(f"  [{msg.role}] {msg.content[:80]}...")

        if chat.tasks:
            output.append("\nTasks:")
            for task in chat.tasks[-3:]:
                output.append(f"  [{task.id}] {task.title} - {task.status}")

        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_history_tool(chat_id: str = None, limit: int = 20) -> str:
    """Get chat history/messages.

    Args:
        chat_id: Chat ID (uses active chat if not specified).
        limit: Maximum messages to return (default: 20).
    """
    try:
        if not chat_id:
            chat = chat_memory.get_active_chat()
            chat_id = chat.id if chat else None

        if not chat_id:
            return "No active chat and no chat_id specified."

        messages = chat_memory.get_messages(chat_id, limit)
        if not messages:
            return "No messages in this chat."

        output = [f"Chat History (last {len(messages)} messages):", "-" * 40]
        for msg in messages:
            output.append(f"[{msg.role}] {msg.content[:150]}...")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"


@tool
def task_list_tool(chat_id: str = None, status: str = None) -> str:
    """List tasks in a chat.

    Args:
        chat_id: Chat ID (uses active chat if not specified).
        status: Filter by status - 'pending', 'completed', 'failed'.
    """
    try:
        if not chat_id:
            chat = chat_memory.get_active_chat()
            chat_id = chat.id if chat else None

        if not chat_id:
            return "No active chat and no chat_id specified."

        tasks = chat_memory.get_tasks(chat_id, status)
        if not tasks:
            return "No tasks found."

        output = ["Tasks:", "-" * 40]
        for task in tasks:
            output.append(f"[{task.id}] {task.title}")
            output.append(f"    Status: {task.status} | Created: {task.created_at[:19]}")
            if task.output:
                output.append(f"    Output: {task.output[:100]}...")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"


@tool
def task_create_tool(chat_id: str, title: str, input_text: str) -> str:
    """Create a new task within a chat.

    Args:
        chat_id: Chat ID to create task in.
        title: Title for the task.
        input_text: Task input/description.
    """
    try:
        task = chat_memory.create_task(chat_id, title, input_text)
        return f"Created task [{task.id}] '{title}' in chat [{chat_id}]"
    except Exception as e:
        return f"Error: {e}"


@tool
def task_complete_tool(chat_id: str, task_id: str, output: str) -> str:
    """Mark a task as completed with output.

    Args:
        chat_id: Chat ID containing the task.
        task_id: ID of the task to complete.
        output: Task output/result.
    """
    try:
        task = chat_memory.update_task(chat_id, task_id, output=output, status="completed")
        if task:
            return f"Task [{task_id}] marked as completed."
        return f"Task '{task_id}' not found in chat '{chat_id}'."
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_stats_tool() -> str:
    """Get chat storage statistics."""
    try:
        stats = chat_memory.get_stats()
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_search_tool(query: str) -> str:
    """Search across all chats for a query string.

    Args:
        query: Search query string.
    """
    try:
        results = chat_memory.search_chats(query)
        if not results:
            return f"No matches for '{query}'."
        output = [f"Search results for '{query}':", "-" * 40]
        for result in results:
            output.append(f"Chat: [{result['chat_id']}] {result['chat_title']}")
            for match in result['matches'][:3]:
                if match['type'] == 'message':
                    output.append(f"  Message: {match['content'][:80]}...")
                else:
                    output.append(f"  Task: {match['title']}")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_export_tool(chat_id: str, output_path: str) -> str:
    """Export a chat to a JSON file.

    Args:
        chat_id: Chat ID to export.
        output_path: Path for the export file.
    """
    try:
        path = chat_memory.export_chat(chat_id, output_path)
        return f"Chat exported to: {path}"
    except Exception as e:
        return f"Error: {e}"


# ── System Tool Wrappers ────────────────────────────────────

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


# ── Tools List ───────────────────────────────────────────────

ALL_TOOLS = [
    # Core tools
    web_search_tool, fetch_url_tool,
    read_file_wrapper, write_file_wrapper, list_directory_wrapper,
    calculator_tool, regex_search_tool,
    shell_tool, datetime_tool,
    json_format_tool, base64_wrapper, csv_reader_tool,
    summarise_text_tool, translate_tool,
    weather_tool, check_url_status_tool,

    # System tools
    file_exists_tool, get_system_info_tool, get_current_datetime_tool,
    hash_string_tool, generate_uuid_tool, generate_password_tool,
    calculate_average_tool, is_prime_tool,
    is_valid_url_tool, is_email_tool,
    slugify_tool, extract_domain_tool,
    count_words_tool, remove_html_tags_tool,
    parse_json_tool, flatten_dict_tool,
    git_status_tool, git_current_branch_tool,

    # Agent memory tools
    agent_set_memory_tool, agent_get_memory_tool,
    agent_clear_memory_tool, agent_list_memory_tool,

    # Super tools (NEW)
    analyze_code_tool, find_symbol_tool, explore_project_tool,
    search_codebase_tool, sentiment_analysis_tool,
    extract_entities_tool, grep_search_tool,
    create_database_tool, execute_sql_tool,
    get_file_outline_tool,

    # Chat memory tools (NEW)
    chat_list_tool, chat_create_tool, chat_switch_tool,
    chat_delete_tool, chat_resume_tool, chat_history_tool,
    task_list_tool, task_create_tool, task_complete_tool,
    chat_stats_tool, chat_search_tool, chat_export_tool,
]


# ── Agent Setup with Token Optimization ───────────────────────

def create_agent() -> ToolCallingAgent:
    """Create a new agent instance."""
    return ToolCallingAgent(
        tools=ALL_TOOLS,
        model=model,
        max_steps=100,
        verbosity_level=2,
    )


def get_context_messages(chat_id: str) -> List[Dict]:
    """Get optimized context messages for a chat."""
    messages = chat_memory.get_messages(chat_id, limit=SLIDING_WINDOW_SIZE)

    # Convert to format expected by token optimization
    formatted = [{'role': m.role, 'content': m.content} for m in messages]

    # Apply token optimization
    optimized = optimize_context(formatted, MAX_CONTEXT_TOKENS)

    return optimized


# ── Interactive Loop with Chat Memory ─────────────────────────

def print_banner():
    print("\n" + "=" * 60)
    print("  OLLAMA AGENT v3 - Chat Memory & Token Optimization")
    print("=" * 60)
    print(f"Platform : {platform.system()} {platform.release()}")
    print(f"Model    : {MODEL_ID}")
    print(f"Endpoint : {OLLAMA_BASE_URL}")
    print(f"Tools    : {len(ALL_TOOLS)}")
    print(f"Max Tokens: {MAX_CONTEXT_TOKENS}")
    print("=" * 60)

    # Show current chat info
    active_chat = chat_memory.get_active_chat()
    if active_chat:
        print(f"\nActive Chat: [{active_chat.id}] {active_chat.title}")
        print(f"  Messages: {len(active_chat.messages)} | Tasks: {len(active_chat.tasks)}")

    print("\n" + "=" * 60)
    print("\nCommands:")
    print("  /help              - Show this help")
    print("  /tools             - List available tools")
    print("  /chats             - List all chats")
    print("  /chat new [title]  - Create new chat")
    print("  /chat switch <id>  - Switch to chat")
    print("  /chat resume <id>  - Resume chat")
    print("  /chat delete <id>  - Delete chat")
    print("  /history           - Show chat history")
    print("  /tasks             - List tasks")
    print("  /task new <title>  - Create new task")
    print("  /stats             - Show chat statistics")
    print("  /search <query>    - Search chats")
    print("  /clear             - Clear agent memory")
    print("  /reset             - Create fresh agent")
    print("  /export <path>     - Export current chat")
    print("  /exit              - Exit the program")
    print("=" * 60)


def print_tools():
    print("\nAvailable Tools:")
    print("-" * 40)
    tool_names = [t.name for t in ALL_TOOLS]
    for i, name in enumerate(sorted(tool_names), 1):
        print(f"  {i:2}. {name}")
    print("-" * 40)


def handle_chat_command(args: List[str]) -> str:
    """Handle chat-related commands."""
    if not args:
        return "Usage: /chat [new|switch|resume|delete|export] [args...]"

    cmd = args[0].lower()

    if cmd == "new":
        title = " ".join(args[1:]) if len(args) > 1 else None
        chat = chat_memory.create_chat(title)
        return f"Created new chat: [{chat.id}] {chat.title}"

    elif cmd in ("switch", "resume"):
        if len(args) < 2:
            return f"Usage: /chat {cmd} <chat_id>"
        chat_id = args[1]
        if cmd == "resume":
            return chat_resume_tool(chat_id)
        else:
            return chat_switch_tool(chat_id)

    elif cmd == "delete":
        if len(args) < 2:
            return "Usage: /chat delete <chat_id>"
        return chat_delete_tool(args[1])

    elif cmd == "export":
        if len(args) < 2:
            return "Usage: /chat export <output_path>"
        active = chat_memory.get_active_chat()
        if not active:
            return "No active chat. Switch to a chat first."
        return chat_export_tool(active.id, args[1])

    else:
        return f"Unknown chat command: {cmd}"


def handle_task_command(args: List[str]) -> str:
    """Handle task-related commands."""
    if not args:
        return "Usage: /task [new|complete|list] [args...]"

    cmd = args[0].lower()

    if cmd == "new":
        active = chat_memory.get_active_chat()
        if not active:
            return "No active chat. Create or switch to a chat first."
        title = " ".join(args[1:]) if len(args) > 1 else "Untitled Task"
        task = chat_memory.create_task(active.id, title, title)
        return f"Created task [{task.id}] '{title}'"

    elif cmd == "complete":
        active = chat_memory.get_active_chat()
        if not active:
            return "No active chat."
        if len(args) < 3:
            return "Usage: /task complete <task_id> <output>"
        task_id = args[1]
        output = " ".join(args[2:])
        return task_complete_tool(active.id, task_id, output)

    elif cmd == "list":
        active = chat_memory.get_active_chat()
        status = args[1] if len(args) > 1 else None
        return task_list_tool(active.id if active else None, status)

    else:
        return f"Unknown task command: {cmd}"


def interactive_loop():
    """Main interactive loop with chat memory support."""
    print_banner()

    # Ensure we have an active chat
    chat_memory.get_or_create_active_chat()

    agent = create_agent()
    task_count = 0

    Path("output").mkdir(exist_ok=True)
    Path("chat_storage").mkdir(exist_ok=True)

    while True:
        try:
            # Show current chat in prompt
            active_chat = chat_memory.get_active_chat()
            chat_prefix = f"[{active_chat.id}] " if active_chat else ""

            user_input = input(f"\n{chat_prefix}Task > ").strip()

            if not user_input:
                continue

            if user_input.startswith("/"):
                parts = user_input.split()
                cmd = parts[0].lower()

                if cmd in ("/exit", "/quit"):
                    print("\nGoodbye!\n")
                    break

                elif cmd == "/help":
                    print_banner()
                    continue

                elif cmd == "/tools":
                    print_tools()
                    continue

                elif cmd == "/chats":
                    print(chat_list_tool())
                    continue

                elif cmd == "/chat":
                    result = handle_chat_command(parts[1:])
                    print(result)
                    # Update banner after chat operations
                    active_chat = chat_memory.get_active_chat()
                    if active_chat:
                        print(f"\nNow in chat: [{active_chat.id}] {active_chat.title}")
                    continue

                elif cmd == "/history":
                    chat_id = parts[1] if len(parts) > 1 else None
                    print(chat_history_tool(chat_id))
                    continue

                elif cmd == "/tasks":
                    active = chat_memory.get_active_chat()
                    status = parts[1] if len(parts) > 1 else None
                    print(task_list_tool(active.id if active else None, status))
                    continue

                elif cmd == "/task":
                    result = handle_task_command(parts[1:])
                    print(result)
                    continue

                elif cmd == "/stats":
                    print(chat_stats_tool())
                    continue

                elif cmd == "/search":
                    if len(parts) < 2:
                        print("Usage: /search <query>")
                        continue
                    print(chat_search_tool(" ".join(parts[1:])))
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

                elif cmd == "/export":
                    active = chat_memory.get_active_chat()
                    if not active:
                        print("No active chat")
                        continue
                    path = parts[1] if len(parts) > 1 else f"output/chat_export_{active.id}.json"
                    print(chat_export_tool(active.id, path))
                    continue

                else:
                    print(f"Unknown command: {user_input}")
                    print("Type /help for available commands")
                    continue

            # Ensure we have an active chat for regular tasks
            active_chat = chat_memory.get_active_chat()
            if not active_chat:
                active_chat = chat_memory.get_or_create_active_chat()
                print(f"\nCreated new chat: [{active_chat.id}]")

            task_count += 1

            # Create a task for this input
            task = chat_memory.create_task(
                active_chat.id,
                f"Task #{task_count}",
                user_input
            )

            print(f"\n{'='*60}")
            print(f"Chat: [{active_chat.id}] {active_chat.title}")
            print(f"Task #{task_count} (ID: {task.id})")
            print(f"{'='*60}")
            print(f"Input: {textwrap.fill(user_input, 78)}")
            print(f"{'='*60}\n")

            # Get optimized context for the agent
            context_messages = get_context_messages(active_chat.id)

            # Add system message with context info
            system_msg = {
                'role': 'system',
                'content': f"You are in chat: {active_chat.title}. "
                          f"Previous context available: {len(context_messages)} messages. "
                          f"Current task ID: {task.id}"
            }

            # Run agent with optimized context
            result = agent.run(user_input)

            print(f"\n{'='*60}")
            print("RESULT:")
            print(f"{'='*60}")
            print(result)
            print(f"{'='*60}\n")

            # Save to chat memory
            chat_memory.add_message(active_chat.id, "user", user_input)
            chat_memory.add_message(active_chat.id, "assistant", str(result))
            chat_memory.update_task(active_chat.id, task.id, output=str(result), status="completed")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type /exit to quit.")
            continue
        except Exception as e:
            print(f"\nError: {e}\n")
            # Record error in current task
            active_chat = chat_memory.get_active_chat()
            if active_chat:
                for task in reversed(active_chat.tasks):
                    if task.status == "pending":
                        chat_memory.update_task(active_chat.id, task.id, output=f"Error: {e}", status="failed")
                        break


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=f"OLLAMA Agent v3 with Chat Memory ({MODEL_ID})")
    parser.add_argument("--task", type=str, default=None, help="Run a single task and exit")
    parser.add_argument("--chat", type=str, default=None, help="Chat ID to use (creates if not exists)")
    parser.add_argument("--no-interactive", action="store_true", help="Disable interactive mode")
    parser.add_argument("--max-tokens", type=int, default=MAX_CONTEXT_TOKENS, help="Max context tokens")
    args = parser.parse_args()

    # Override token config if specified
    if args.max_tokens:
        MAX_CONTEXT_TOKENS = args.max_tokens

    Path("output").mkdir(exist_ok=True)
    Path("chat_storage").mkdir(exist_ok=True)

    if args.task:
        # Single task mode
        if args.chat:
            chat = chat_memory.get_chat(args.chat)
            if not chat:
                chat = chat_memory.create_chat(f"Task: {args.task[:30]}")
                chat_memory.set_active_chat(args.chat)
            else:
                chat_memory.set_active_chat(args.chat)
        else:
            chat = chat_memory.get_or_create_active_chat()

        agent = create_agent()
        print(f"\nRunning task in chat [{chat.id}]: {args.task}\n")

        task = chat_memory.create_task(chat.id, "Single Task", args.task)
        result = agent.run(args.task)

        chat_memory.add_message(chat.id, "user", args.task)
        chat_memory.add_message(chat.id, "assistant", str(result))
        chat_memory.update_task(chat.id, task.id, output=str(result), status="completed")

        print(f"\nResult:\n{result}\n")
        print(f"Saved to chat: [{chat.id}]")

    elif args.no_interactive:
        agent = create_agent()
        chat = chat_memory.get_or_create_active_chat()

        for line in sys.stdin:
            task_input = line.strip()
            if task_input:
                task = chat_memory.create_task(chat.id, "stdin task", task_input)
                print(f"\nTask: {task_input}")
                result = agent.run(task_input)
                print(f"Result: {result}\n")

                chat_memory.add_message(chat.id, "user", task_input)
                chat_memory.add_message(chat.id, "assistant", str(result))
                chat_memory.update_task(chat.id, task.id, output=str(result), status="completed")
    else:
        interactive_loop()
