import sys
import os
import argparse

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from core.agent_manager import AgentManager
from core.registry import load_tools_from_directory
from core.memory import SmartContextManager
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
    prompt    = f"Previous Context Summary: {optimized[0]['content']}\n\nTask: {user_input}"

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

            run_task(manager, context_manager, chat_memory, active_chat, user_input)

        except KeyboardInterrupt:
            print(f"\n  {YEL}Interrupted — type /exit to quit.{R}")
        except Exception as e:
            print(f"\n  {'\033[1;31m'}Error:{R} {e}\n")


def _print_help():
    """Print help for built-in CLI commands."""
    cmds = [
        ("/exit   ", "Exit BRAWL"),
        ("/new    ", "Start a new chat session"),
        ("/chats  ", "List all saved chat sessions"),
        ("/switch ", "Switch to a different session  e.g. /switch abc123"),
        ("/clear  ", "Clear the screen and reprint banner"),
        ("/help   ", "Show this help"),
    ]
    print()
    print(f"  {MAG}{B}Built-in Commands{R}")
    print(f"  {GREY}{'─' * 44}{R}")
    for cmd, desc in cmds:
        print(f"  {CYAN}{cmd}{R}  {GREY}{desc}{R}")
    print()


if __name__ == "__main__":
    main()
