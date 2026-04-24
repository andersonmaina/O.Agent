# OLLAMA AGENT v3
## AI Agent with Chat Memory & Token Optimization

A powerful, Windows-compatible AI agent powered by Ollama and smolagents, featuring **persistent chat memory**, **task management**, and **token optimization** for efficient long-running conversations.

---

## Features

### Chat Memory System
- **Persistent storage** - Conversations saved across sessions
- **Multiple chats** - Switch between different chat contexts
- **Resume chats** - Continue conversations where you left off
- **Search chats** - Find previous discussions by keyword
- **Export chats** - Save conversations as JSON

### Task Management
- Create tasks within chats
- Track task status (pending, completed, failed)
- View task history per chat

### Token Optimization
- **Sliding window** - Keeps newest messages in context
- **Auto-summarization** - Summarizes old messages when approaching token limit
- **Configurable limits** - Set max tokens via `.env` or CLI
- **Context compression** - Efficient memory usage

### 60+ Built-in Tools

#### Core Tools
| Tool | Description |
|------|-------------|
| `web_search_tool` | DuckDuckGo search (no API key) |
| `fetch_url_tool` | Fetch & parse web pages |
| `read_file_wrapper` | Read local files (sandboxed to cwd) |
| `write_file_wrapper` | Write/append to local files |
| `list_directory_wrapper` | List directory contents |
| `shell_tool` | Run shell commands |
| `calculator_tool` | Safe AST-based arithmetic |
| `datetime_tool` | Date/time with timezone support |
| `regex_search_tool` | Pattern matching in text |
| `json_format_tool` | Parse and format JSON |
| `csv_reader_tool` | Read and preview CSV files |
| `weather_tool` | Get weather via wttr.in |
| `summarise_text_tool` | AI text summarization |
| `translate_tool` | AI-powered translation |

#### System Tools
| Tool | Description |
|------|-------------|
| `file_exists_tool` | Check if file exists |
| `get_system_info_tool` | Get system information |
| `hash_string_tool` | Hash strings (SHA256, etc.) |
| `generate_uuid_tool` | Generate UUID v4 |
| `generate_password_tool` | Generate strong passwords |
| `is_valid_url_tool` | Validate URLs |
| `is_email_tool` | Validate email addresses |
| `git_status_tool` | Git repository status |
| `git_current_branch_tool` | Get current Git branch |

#### Super Tools (NEW in v3)
| Tool | Description |
|------|-------------|
| `analyze_code_tool` | Analyze code structure & metrics |
| `find_symbol_tool` | Find functions/classes in codebase |
| `explore_project_tool` | Project structure overview |
| `search_codebase_tool` | Semantic code search |
| `sentiment_analysis_tool` | Text sentiment analysis |
| `extract_entities_tool` | Extract emails, URLs, phones, dates |
| `grep_search_tool` | Regex file search |
| `create_database_tool` | Create SQLite databases |
| `execute_sql_tool` | Run SQL queries |
| `get_file_outline_tool` | Code file structure outline |

#### Chat Memory Tools (NEW in v3)
| Tool | Description |
|------|-------------|
| `chat_list_tool` | List all chat sessions |
| `chat_create_tool` | Create new chat |
| `chat_switch_tool` | Switch between chats |
| `chat_resume_tool` | Resume chat with history |
| `chat_delete_tool` | Delete a chat |
| `chat_history_tool` | View message history |
| `task_list_tool` | List tasks in chat |
| `task_create_tool` | Create new task |
| `task_complete_tool` | Mark task complete |
| `chat_stats_tool` | Chat storage statistics |
| `chat_search_tool` | Search across all chats |
| `chat_export_tool` | Export chat to JSON |

---

## Installation

### Requirements
- Python 3.10+
- Ollama running locally or accessible via network

### Install Dependencies
```bash
pip install smolagents openai httpx duckduckgo-search beautifulsoup4 requests python-dotenv
```

### Environment Variables
Create a `.env` file:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:397b-cloud
MAX_CONTEXT_TOKENS=4096
TOKEN_ESTIMATE_PER_CHAR=4
SLIDING_WINDOW_SIZE=50
```

Or set via PowerShell:
```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_MODEL = "qwen3.5:397b-cloud"
$env:MAX_CONTEXT_TOKENS = "4096"
```

---

## Usage

### Interactive Mode
```bash
py agentv3.py
```

### Single Task
```bash
py agentv3.py --task "analyze the codebase and find all Python files"
```

### With Specific Chat
```bash
py agentv3.py --chat "my-project" --task "fix the bug in main.py"
```

### Custom Token Limit
```bash
py agentv3.py --max-tokens 8192
```

### Non-Interactive (stdin)
```bash
echo "What is the capital of France?" | py agentv3.py --no-interactive
```

---

## Interactive Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help menu |
| `/tools` | List available tools |
| `/chats` | List all chat sessions |
| `/chat new [title]` | Create new chat |
| `/chat switch <id>` | Switch to another chat |
| `/chat resume <id>` | Resume chat with history |
| `/chat delete <id>` | Delete a chat |
| `/history` | View message history |
| `/tasks` | List tasks in current chat |
| `/task new <title>` | Create new task |
| `/task complete <id> <output>` | Mark task complete |
| `/stats` | Show chat statistics |
| `/search <query>` | Search across all chats |
| `/export <path>` | Export current chat to JSON |
| `/clear` | Clear agent memory |
| `/reset` | Create fresh agent instance |
| `/exit` | Exit the program |

---

## Project Structure

```
OLLAMA-AGENT/
├── agentv3.py           # Main agent with chat memory
├── agentv2.py           # Previous version (no chat memory)
├── tools/
│   ├── chat_memory.py   # Chat persistence system
│   ├── code_tools.py    # Code analysis tools
│   ├── ai_tools.py      # AI-powered text tools
│   ├── database_tools.py # SQLite operations
│   ├── search_tools.py  # Advanced file search
│   ├── explorer_tools.py # Codebase exploration
│   ├── file_tools.py    # File operations
│   ├── text_tools.py    # Text manipulation
│   ├── web_tools.py     # Web utilities
│   ├── system_tools.py  # System info & commands
│   ├── git_tools.py     # Git operations
│   └── ...              # More tool modules
├── chat_storage/        # Persistent chat data
├── output/              # Generated outputs
└── .env                 # Environment config
```

---

## Token Optimization Details

The agent uses several strategies to manage context tokens efficiently:

1. **Sliding Window** - Keeps the most recent N messages (configurable via `SLIDING_WINDOW_SIZE`)

2. **Auto-Summarization** - When context approaches `MAX_CONTEXT_TOKENS * SUMMARY_TRIGGER_RATIO`, older messages are summarized

3. **Truncation** - If context still exceeds limits after summarization, oldest messages are dropped

4. **Content Compression** - Long messages have whitespace normalized and content truncated

---

## API Reference

### ChatMemoryManager

```python
from tools.chat_memory import ChatMemoryManager

chat_memory = ChatMemoryManager(storage_dir="./chat_storage")

# Create a chat
chat = chat_memory.create_chat("My Project")

# Switch to a chat
chat_memory.set_active_chat(chat.id)

# Add messages
chat_memory.add_message(chat.id, "user", "Hello!")
chat_memory.add_message(chat.id, "assistant", "Hi there!")

# Create a task
task = chat_memory.create_task(chat.id, "Fix bug", "Investigate the issue")

# Complete a task
chat_memory.update_task(chat.id, task.id, output="Fixed!", status="completed")

# Get history
messages = chat_memory.get_messages(chat.id, limit=50)

# Search chats
results = chat_memory.search_chats("bug fix")

# Export chat
chat_memory.export_chat(chat.id, "output/chat_backup.json")
```

---

## Version History

### v3 (Current)
- Added persistent chat memory system
- Task management within chats
- Token optimization strategies
- 20+ new super tools
- Chat resume/delete/switch commands
- Search across all chats
- Export chats to JSON

### v2
- Integrated tools from `./tools` folder
- Interactive mode with multiple tools
- No context carry-over between tasks

### v1
- Basic smolagents + Ollama integration
- Single task execution

---

## License

MIT License

---

## Contributing

Contributions welcome! Please ensure new tools follow the existing patterns and include proper docstrings.
