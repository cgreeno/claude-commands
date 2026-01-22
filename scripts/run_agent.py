#!/usr/bin/env python3
"""
Run a Claude agent with a prompt file against a batch file.

Usage: python run_agent.py <prompt_file> <batch_file>

Example:
    python run_agent.py ~/.claude/prompts/codeowners-test-verifier.md .github/unowned-batches/batch_01.json
"""
import asyncio
import json
import sys
from pathlib import Path

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)


async def run(prompt_file: str, batch_file: str) -> None:
    """Run agent with prompt against batch of files."""
    # Load system prompt
    prompt_path = Path(prompt_file).expanduser()
    system_prompt = prompt_path.read_text()

    # Load batch
    batch_path = Path(batch_file)
    batch = json.loads(batch_path.read_text())
    files = batch["files"]
    batch_num = batch["batch"]

    # Build task prompt with file list
    files_list = "\n".join(f"- {f}" for f in files)
    task = f"Process batch {batch_num} with {len(files)} files:\n\n{files_list}"

    # Output directory
    output_dir = Path(".github/new_owner")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"batch_result_{batch_num:02d}.json"

    print(f"Processing batch {batch_num} ({len(files)} files)...")

    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=["Read", "Grep", "Glob", "Write"],
        permission_mode="acceptEdits",
        cwd=str(Path.cwd()),
    )

    collected_text = []

    async for message in query(prompt=task, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    collected_text.append(block.text)
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"[{block.name}] {block.input}")

        elif isinstance(message, ResultMessage):
            print(f"\nBatch {batch_num} complete in {message.duration_ms}ms")
            if message.total_cost_usd:
                print(f"Cost: ${message.total_cost_usd:.4f}")

    # Write results
    result = {
        "batch": batch_num,
        "files_processed": len(files),
        "files": files,
        "output": "\n".join(collected_text),
    }
    output_file.write_text(json.dumps(result, indent=2))
    print(f"Results written to {output_file}")


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python run_agent.py <prompt_file> <batch_file>")
        print("\nExample:")
        print("  python run_agent.py ~/.claude/prompts/test-verifier.md .github/unowned-batches/batch_01.json")
        sys.exit(1)

    prompt_file = sys.argv[1]
    batch_file = sys.argv[2]

    # Validate files exist
    if not Path(prompt_file).expanduser().exists():
        print(f"Error: Prompt file not found: {prompt_file}")
        sys.exit(1)

    if not Path(batch_file).exists():
        print(f"Error: Batch file not found: {batch_file}")
        sys.exit(1)

    asyncio.run(run(prompt_file, batch_file))


if __name__ == "__main__":
    main()
