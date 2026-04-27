# BRAWL Agent v3.1
## Autonomous Intelligence. Relentlessly Capable.

BRAWL is a high-performance, autonomous AI agent CLI powered by **Ollama**, **smolagents**, and **RTK (Recursive Token context)**. Built for power users who need persistent memory, advanced toolsets, and multi-provider flexibility.

---

##  Quick Start

### 1. Clone & install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Create a `.env` file (see `.env.example` for details):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3-coder-next:cloud
PROVIDER=ollama
MAX_CONTEXT_TOKENS=4096
```

### 3. Launch BRAWL
```bash
python main.py
```

---

##  Features

- **Multi-provider support**: Seamlessly switch between **Ollama**, **HuggingFace**, and **NVIDIA** models.
- **Smart context (RTK)**: Intelligent token management with recursive summarization to maintain long-term context without hitting limits.
- **Persistent memory**: Chat sessions are automatically saved and can be resumed at any time.
- **120+ tool suites**:
    - `file_tools`, `search_tools`, `code_tools` for system automation.
    - `web_tools`, `network_tools`, `ai_tools` for connectivity and analysis.
    - `database_tools`, `data_tools`, `math_tools` for structured data handling.
- **Interactive REPL**: A polished command-line interface with built-in session management.

---

##  CLI commands

| Command | Action |
|:---|:---|
| `/new` | Start a fresh chat session |
| `/chats` | List all saved sessions |
| `/switch <id>` | Switch to a specific session |
| `/delete` | Delete the active (or specified) chat |
| `/model` | Manage providers and models (`list`, `use`, `delete`) |
| `/clear` | Refresh the terminal view |
| `/help` | Display the command manual |
| `/exit` | Terminate the BRAWL session |

---

## Project structure

- `main.py`: Entry point for the BRAWL CLI.
- `core/`: Core logic (Agent management, RTK memory, configuration).
- `tools/`: Modular tool implementations (filesystem, web, database, etc.).
- `chat_storage/`: Persistent SQLite storage for sessions.
- `output/`: Default directory for generated files and exports.

---

## Credits

Built with ❤️ using [smolagents](https://github.com/huggingface/smolagents) and [Ollama](https://ollama.ai).
