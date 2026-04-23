Smolagents + Ollama via ngrok — Windows-compatible
===================================================
Tools:
  web_search_tool     — DuckDuckGo search (no API key)
  fetch_url_tool      — fetch & parse a web page
  read_file_tool      — read a local file (sandboxed to cwd)
  write_file_tool     — write / append to a local file
  shell_tool          — run a shell command (cmd.exe on Windows)
  calculator_tool     — safe AST-based arithmetic evaluator
  summarise_text_tool — ask the model to summarise a block of text

Setup
-----
pip install smolagents openai httpx duckduckgo-search beautifulsoup4 requests

PowerShell env vars:
  $env:NGROK_URL    = "https://improved-zebra-jj5pqwjxqpj7f5x77-11434.app.github.dev"
  $env:OLLAMA_MODEL = "gemma4:e2b"

Run:
  python agent.py
  python agent.py --task "your task here"
  python agent.py --list-tasks