"""Restore an Azerbaijan travel-agent thread from an in-memory checkpoint."""

import asyncio
import uuid

from langchain_core.messages import HumanMessage

from langgraph_short_term_memory import build_travel_assistant


async def checkpoint_restore_demo() -> None:
    """Run one turn, inspect its checkpoints, and continue from the latest one."""
    travel_assistant = await build_travel_assistant()
    thread_id = str(uuid.uuid4())
    thread_config = {"configurable": {"thread_id": thread_id}}

    print(f"Thread ID: {thread_id}")
    print("Ask first about an Azerbaijani destination or accommodation.")
    user_input = input("You: ").strip()
    if not user_input:
        print("No question supplied; exiting.")
        return

    first_result = await travel_assistant.ainvoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=thread_config,
    )
    print(f"Assistant: {first_result['messages'][-1].content}\n")

    # A checkpointer stores a state snapshot at each graph super-step, so one
    # user turn normally produces several checkpoints.
    history = list(travel_assistant.get_state_history(thread_config))
    if not history:
        raise RuntimeError("No checkpoints were saved for the thread.")

    print(f"Saved checkpoints: {len(history)}")
    for index, snapshot in enumerate(history, start=1):
        checkpoint_id = snapshot.config["configurable"]["checkpoint_id"]
        print(
            f"  {index}. checkpoint_id={checkpoint_id}; "
            f"next={snapshot.next}"
        )

    # History is newest first. Supplying this checkpoint_id explicitly restores
    # that snapshot; the next invocation continues as a branch from it.
    latest_snapshot = history[0]
    restore_config = latest_snapshot.config
    restored_snapshot = travel_assistant.get_state(restore_config)
    restored_checkpoint_id = restore_config["configurable"]["checkpoint_id"]

    print(f"\nRestored checkpoint: {restored_checkpoint_id}")
    print(f"Messages in restored state: {len(restored_snapshot.values['messages'])}")
    print(f"Next nodes from restored state: {restored_snapshot.next}\n")

    follow_up = "What is the mock weather in the same town?"
    print(f"You: {follow_up}")
    continued_result = await travel_assistant.ainvoke(
        {"messages": [HumanMessage(content=follow_up)]},
        config=restore_config,
    )
    print(f"Assistant: {continued_result['messages'][-1].content}\n")

    updated_history = list(travel_assistant.get_state_history(thread_config))
    print(f"Checkpoints after continuing: {len(updated_history)}")
    print(
        "The follow-up could resolve 'the same town' because it continued from "
        "the restored thread state."
    )


if __name__ == "__main__":
    asyncio.run(checkpoint_restore_demo())
