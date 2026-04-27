# BRAWL Agent v3.1
## Autonomous Intelligence. Relentlessly Capable.

BRAWL is a high-performance, autonomous AI agent CLI powered by **Ollama**, **smolagents**, and **RTK (Recursive Token context)**. Built for power users who need persistent memory, advanced toolsets, and multi-provider flexibility.

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file (see `.env.example` for details):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
PROVIDER=ollama
MAX_CONTEXT_TOKENS=8192
```

### 3. Launch BRAWL
```bash
python main.py
```

---

## 🛠 Features

- **Multi-Provider Support**: Seamlessly switch between **Ollama**, **HuggingFace**, and **NVIDIA** models.
- **Smart Context (RTK)**: Intelligent token management with recursive summarization to maintain long-term context without hitting limits.
- **Persistent Memory**: Chat sessions are automatically saved and can be resumed at any time.
- **20+ Tool Suites**:
    - `file_tools`, `search_tools`, `code_tools` for system automation.
    - `web_tools`, `network_tools`, `ai_tools` for connectivity and analysis.
    - `database_tools`, `data_tools`, `math_tools` for structured data handling.
- **Interactive REPL**: A polished command-line interface with built-in session management.

---

## ⌨️ CLI Commands

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

## 📂 Project Structure

- `main.py`: Entry point for the BRAWL CLI.
- `core/`: Core logic (Agent management, RTK memory, configuration).
- `tools/`: Modular tool implementations (filesystem, web, database, etc.).
- `chat_storage/`: Persistent JSON storage for sessions.
- `output/`: Default directory for generated files and exports.

---

## 🏆 Credits

Built with ❤️ using [smolagents](https://github.com/huggingface/smolagents) and [Ollama](https://ollama.ai).
