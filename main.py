import sys
import os
import argparse

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from core.agent_manager import AgentManager
from core.registry import load_tools_from_directory
from core.memory import SmartContextManager
from core.output_filter import filtered_output
from core.brand import (
    print_banner, print_session_info, print_goodbye,
    GRN, YEL, MAG, CYAN, GREY, WHT, R, B, DIM
)
from tools.chat_memory import get_chat_memory


def _step(n: int, total: int, msg: str, done: bool = False, detail: str = ""):
    if done:
        check = f"{GRN}✔{R}"
        label = f"{GRN}{msg}{R}"
        suffix = f"  {GREY}{detail}{R}" if detail else ""
        print(f"  {check}  {B}[{n}/{total}]{R}  {label}{suffix}          ")
    else:
        spin = f"{GREY}…{R}"
        print(f"  {spin}  {B}[{n}/{total}]{R}  {DIM}{msg}…{R}           ", end="\r", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="BRAWL Agent — Autonomous Intelligence CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--task",     type=str, help="Run a single task non-interactively")
    parser.add_argument("--provider", type=str, choices=["ollama", "huggingface", "nvidia"],
                        help="Override the LLM provider")
    parser.add_argument("--model",    type=str, help="Override the model ID")
    args = parser.parse_args()

    # Apply CLI overrides
    if args.provider:
        settings.PROVIDER = args.provider
    if args.model:
        settings.OLLAMA_MODEL = args.model

    # ── Brand Banner ──────────────────────────────────────────────────────
    print_banner()

    # ── Boot sequence ─────────────────────────────────────────────────────
    _step(1, 3, "Loading tools")
    all_tools = load_tools_from_directory("tools")
    _step(1, 3, "Tools loaded", done=True, detail=f"{len(all_tools)} tools active")

    _step(2, 3, "Initializing agent")
    manager = AgentManager(all_tools)
    _step(2, 3, "Agent ready", done=True, detail=f"{settings.PROVIDER.upper()} / {settings.OLLAMA_MODEL}")

    _step(3, 3, "Restoring memory")
    chat_memory     = get_chat_memory()
    context_manager = SmartContextManager()
    active_chat     = chat_memory.get_or_create_active_chat()
    _step(3, 3, "Memory restored", done=True, detail=f"session {active_chat.id}")

    print()

    # ── Session info panel ────────────────────────────────────────────────
    print_session_info(
        provider      = settings.PROVIDER,
        model         = settings.OLLAMA_MODEL,
        context_tokens= settings.MAX_CONTEXT_TOKENS,
    )

    # ── Run ───────────────────────────────────────────────────────────────
    if args.task:
        run_task(manager, context_manager, chat_memory, active_chat, args.task)
    else:
        interactive_loop(manager, context_manager, chat_memory)


def run_task(manager, context_manager, chat_memory, active_chat, user_input: str):
    """Execute a single task and persist the exchange to memory."""
    messages  = chat_memory.get_messages(active_chat.id, limit=settings.SLIDING_WINDOW_SIZE)
    formatted = [{"role": m.role, "content": m.content} for m in messages]

    optimized = context_manager.optimize(formatted)

    # Build prompt — skip context preamble if this is a fresh chat with no history
    if optimized:
        prompt = f"Previous Context Summary: {optimized[0]['content']}\n\nTask: {user_input}"
    else:
        prompt = user_input

    with filtered_output():
        result = manager.run(prompt)

    chat_memory.add_message(active_chat.id, "user",      user_input)
    chat_memory.add_message(active_chat.id, "assistant", str(result))

    print(f"\n  {MAG}{B}◈ RESULT{R}\n")
    print(f"  {result}\n")


def interactive_loop(manager, context_manager, chat_memory):
    """Main interactive REPL loop."""
    print(f"  {GREY}Type your task and press Enter.  /exit to quit.{R}\n")

    while True:
        try:
            active_chat = chat_memory.get_active_chat()
            chat_id     = active_chat.id if active_chat else "—"

            prompt_str = f"  {CYAN}{B}[{chat_id}]{R} {MAG}{B}BRAWL ▸{R} "
            user_input = input(prompt_str).strip()

            if not user_input:
                continue
            if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
                print_goodbye()
                break

            # ── built-in slash commands ────────────────────────────────
            if user_input.lower() == "/chats":
                chats = chat_memory.list_chats()
                print()
                for c in chats:
                    marker = f"{GRN}●{R}" if c["id"] == chat_id else f"{GREY}○{R}"
                    print(f"    {marker}  {c['id']}  {GREY}{c['title']}{R}")
                print()
                continue

            if user_input.lower().startswith("/switch "):
                cid = user_input.split(" ", 1)[1].strip()
                chat_memory.set_active_chat(cid)
                print(f"  {GRN}✔  Switched to {cid}{R}\n")
                continue

            if user_input.lower() == "/new":
                active_chat = chat_memory.create_chat()
                print(f"  {GRN}✔  New session: {active_chat.id}{R}\n")
                continue

            if user_input.lower() == "/clear":
                import os as _os
                _os.system("cls" if _os.name == "nt" else "clear")
                print_banner()
                continue

            if user_input.lower() == "/help":
                _print_help()
                continue

            if user_input.lower().startswith("/delete"):
                parts = user_input.split(None, 1)
                # /delete          → delete active chat
                # /delete <id>     → delete specific chat
                target_id = parts[1].strip() if len(parts) > 1 else chat_id
                if target_id == "—" or not target_id:
                    print(f"  {YEL}No active chat to delete.{R}\n")
                else:
                    confirm = input(f"  {YEL}Delete chat {target_id}? (y/N):{R} ").strip().lower()
                    if confirm == "y":
                        was_active = (target_id == chat_id)
                        chat_memory.delete_chat(target_id)
                        if was_active:
                            next_chat = chat_memory.get_active_chat()
                            if not next_chat:
                                next_chat = chat_memory.create_chat()
                            print(f"  {GRN}✔  Deleted. Now on session {next_chat.id}{R}\n")
                        else:
                            print(f"  {GRN}✔  Deleted chat {target_id}{R}\n")
                    else:
                        print(f"  {GREY}Cancelled.{R}\n")
                continue

            # ── /model commands ───────────────────────────────────────
            if user_input.lower() == "/model list":
                _cmd_model_list(manager)
                continue

            if user_input.lower().startswith("/model use "):
                parts = user_input.split(None, 3)  # /model use <id> [provider]
                model_id = parts[2] if len(parts) > 2 else ""
                provider = parts[3] if len(parts) > 3 else None
                if not model_id:
                    print(f"  {YEL}Usage: /model use <model_id> [provider]{R}\n")
                else:
                    result = manager.switch_model(model_id, provider)
                    icon = GRN if "→" in result else YEL
                    print(f"  {icon}✔  {result}{R}\n")
                continue

            if user_input.lower().startswith("/model delete "):
                model_id = user_input.split(None, 2)[-1].strip()
                if not model_id:
                    print(f"  {YEL}Usage: /model delete <model_id>{R}\n")
                else:
                    confirm = input(f"  {YEL}Delete {model_id}? (y/N):{R} ").strip().lower()
                    if confirm == "y":
                        result = manager.delete_ollama_model(model_id)
                        print(f"  {GRN}✔  {result}{R}\n")
                    else:
                        print(f"  {GREY}Cancelled.{R}\n")
                continue

            if user_input.lower() == "/model":
                print(f"\n  {CYAN}Active:{R} {manager.current_model_info()}")
                print(f"  {GREY}Use /model list · /model use <id> · /model delete <id>{R}\n")
                continue

            run_task(manager, context_manager, chat_memory, active_chat, user_input)

        except KeyboardInterrupt:
            print(f"\n  {YEL}Interrupted — type /exit to quit.{R}")
        except Exception as e:
            print(f"\n  {'\033[1;31m'}Error:{R} {e}\n")


def _cmd_model_list(manager):
    """Print available Ollama models in a neat table."""
    print(f"\n  {MAG}{B}Available Models  ({settings.OLLAMA_BASE_URL}){R}")
    print(f"  {GREY}{'─' * 52}{R}")
    models = manager.list_ollama_models()
    if not models or "error" in models[0]:
        err = models[0].get("error", "unknown error") if models else "no response"
        print(f"  {YEL}Could not reach Ollama: {err}{R}")
    else:
        active = settings.OLLAMA_MODEL
        for m in models:
            name  = m.get("name", "?")
            size  = m.get("size", 0)
            gb    = f"{size / 1e9:.1f} GB" if size else ""
            marker = f"{GRN}●{R}" if name == active else f"{GREY}○{R}"
            print(f"  {marker}  {CYAN}{name:<40}{R}  {GREY}{gb}{R}")
    print()


def _print_help():
    """Print help for built-in CLI commands."""
    cmds = [
        ("/exit              ", "Exit BRAWL"),
        ("/new               ", "Start a new chat session"),
        ("/chats             ", "List all saved chat sessions"),
        ("/switch <id>       ", "Switch to a different session"),
        ("/delete            ", "Delete the active chat (with confirmation)"),
        ("/delete <id>       ", "Delete a specific chat by ID"),
        ("/clear             ", "Clear the screen and reprint banner"),
        ("/model             ", "Show active model"),
        ("/model list        ", "List all Ollama models available locally"),
        ("/model use <m>     ", "Switch to model <m>  e.g. /model use llama3"),
        ("/model use <m> <p> ", "Switch model + provider  e.g. /model use llama3 nvidia"),
        ("/model delete <m>  ", "Delete a model from Ollama storage"),
        ("/help              ", "Show this help"),
    ]
    print()
    print(f"  {MAG}{B}Built-in Commands{R}")
    print(f"  {GREY}{'─' * 52}{R}")
    for cmd, desc in cmds:
        print(f"  {CYAN}{cmd}{R}  {GREY}{desc}{R}")
    print()


if __name__ == "__main__":
    main()
