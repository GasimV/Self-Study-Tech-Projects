"""Persist and restore an Azerbaijan travel-agent thread with Redis."""

import argparse
import asyncio
import os
import sys
import uuid

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from langgraph_short_term_memory import build_travel_assistant


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


def parse_args() -> argparse.Namespace:
    """Parse the save/restore demonstration command."""
    parser = argparse.ArgumentParser(
        description="Save or restore a LangGraph thread in Docker-hosted Redis."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    save_parser = subparsers.add_parser("save", help="Start and persist a thread.")
    save_parser.add_argument(
        "--question",
        help="Initial question; omit it to enter the question interactively.",
    )
    save_parser.add_argument(
        "--thread-id",
        default=None,
        help="Optional thread ID; a UUID is generated when omitted.",
    )

    restore_parser = subparsers.add_parser(
        "restore", help="Restore and continue a persisted thread."
    )
    restore_parser.add_argument("thread_id", help="Thread ID printed by save.")
    restore_parser.add_argument(
        "--question",
        help=(
            "Follow-up question; defaults to asking for mock weather in the "
            "same town."
        ),
    )
    return parser.parse_args()


async def save_thread(args: argparse.Namespace) -> None:
    """Run an initial turn and persist all graph checkpoints in Redis."""
    thread_id = args.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    question = args.question or input("You: ").strip()
    if not question:
        print("No question supplied; exiting.")
        return

    print(f"Thread ID: {thread_id}")
    print(f"You: {question}")
    async with AsyncRedisSaver.from_conn_string(REDIS_URL) as checkpointer:
        await checkpointer.asetup()
        graph = await build_travel_assistant(checkpointer=checkpointer)
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=question)]}, config=config
        )
        saved = await graph.aget_state(config)

    print(f"Assistant: {result['messages'][-1].content}")
    print(
        "Saved latest Redis checkpoint: "
        f"{saved.config['configurable']['checkpoint_id']}"
    )
    print(
        "Run the restore command in a new process with this thread ID to "
        "continue the conversation."
    )


async def restore_thread(args: argparse.Namespace) -> None:
    """Load an existing Redis thread and continue it from its latest state."""
    config = {"configurable": {"thread_id": args.thread_id}}
    follow_up = args.question or "What is the mock weather in the same town?"

    async with AsyncRedisSaver.from_conn_string(REDIS_URL) as checkpointer:
        await checkpointer.asetup()
        graph = await build_travel_assistant(checkpointer=checkpointer)
        restored = await graph.aget_state(config)
        if not restored.values:
            raise SystemExit(
                f"No Redis checkpoints found for thread {args.thread_id!r}."
            )

        checkpoint_id = restored.config["configurable"]["checkpoint_id"]
        messages_before = len(restored.values.get("messages", []))
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=follow_up)]}, config=config
        )
        continued = await graph.aget_state(config)

    print(f"Restored thread: {args.thread_id}")
    print(f"Latest checkpoint: {checkpoint_id}")
    print(f"Messages before continuing: {messages_before}")
    print(f"You: {follow_up}")
    print(f"Assistant: {result['messages'][-1].content}")
    print(
        "New latest Redis checkpoint: "
        f"{continued.config['configurable']['checkpoint_id']}"
    )


async def main() -> None:
    """Execute the requested Redis checkpoint operation."""
    args = parse_args()
    if args.action == "save":
        await save_thread(args)
    else:
        await restore_thread(args)


if __name__ == "__main__":
    asyncio.run(main())
