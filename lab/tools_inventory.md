# Tools Inventory - Ollama Agent

## Overview
This document explores all available tools in the agent system.

## Tool Categories

### 1. Web & Network Tools
- **web_search_tool**: Search the web with DuckDuckGo. Returns titles, URLs, snippets.
- **fetch_url_tool**: Fetch visible text from a web page (strips HTML).
- **check_url_status_tool**: Check if a URL is reachable; returns HTTP status and response time.
- **is_valid_url_tool**: Check if a URL is valid.
- **extract_domain_tool**: Extract domain from URL.
- **weather_tool**: Get current weather via wttr.in (no API key needed).

### 2. File System Tools
- **read_file_wrapper**: Read a local file inside cwd and return its text.
- **write_file_wrapper**: Write or append text to a local file inside cwd.
- **list_directory_wrapper**: List files and folders in a directory inside cwd.
- **file_exists_tool**: Check if a file exists.

### 3. Text Processing Tools
- **summarise_text_tool**: Ask the model to summarise text concisely.
- **translate_tool**: Translate text into another language using the local model.
- **count_words_tool**: Count words in text.
- **remove_html_tags_tool**: Remove HTML tags from text.
- **slugify_tool**: Convert text to URL-friendly slug.

### 4. Data & Calculation Tools
- **calculator_tool**: Safely evaluate arithmetic. Supports + - * / ** // % abs round sqrt.
- **calculate_average_tool**: Calculate average of comma-separated numbers.
- **is_prime_tool**: Check if a number is prime.
- **csv_reader_tool**: Read a local CSV and return a text table preview.

### 5. JSON & Data Format Tools
- **json_format_tool**: Parse and reformat JSON. mode='pretty' (indented) or 'minify'.
- **parse_json_tool**: Parse JSON string and return formatted output.
- **flatten_dict_tool**: Flatten a nested JSON dictionary.
- **base64_wrapper**: Encode text to base64 or decode base64 back to text.

### 6. Security & Generation Tools
- **hash_string_tool**: Hash a string using specified algorithm.
- **generate_uuid_tool**: Generate a UUID v4.
- **generate_password_tool**: Generate a strong random password.

### 7. Validation Tools
- **is_email_tool**: Check if a string is a valid email.
- **is_valid_url_tool**: Check if a URL is valid.

### 8. System & Time Tools
- **get_system_info_tool**: Get system information.
- **get_current_datetime_tool**: Get current date and time.
- **datetime_tool**: Return current date and time in the given IANA timezone.

### 9. Git Tools
- **git_status_tool**: Get git status of current repository.
- **git_current_branch_tool**: Get current git branch.

### 10. Memory Tools
- **agent_set_memory_tool**: Store a value in agent memory (session-only).
- **agent_get_memory_tool**: Retrieve a value from agent memory.
- **agent_clear_memory_tool**: Clear all agent memory.
- **agent_list_memory_tool**: List all keys in agent memory.

### 11. Shell & Advanced Tools
- **shell_tool**: Run a shell command, return stdout+stderr.
- **regex_search_tool**: Find all regex matches in text, with surrounding context.

### 12. Final Answer Tool
- **final_answer**: Provides a final answer to the given problem.

## Total Tools Count: 36 tools

## Notes
- All file operations are sandboxed to the current working directory (cwd)
- Shell commands run via cmd.exe on Windows
- Memory tools are session-only (cleared when agent restarts)
