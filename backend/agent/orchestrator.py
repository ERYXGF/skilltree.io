"""
Orchestrator loop for AI agent tool-calling workflow.

This module implements the main control loop that manages the conversation
between Claude and the tool system, handling tool calls and responses until
Claude provides a final text answer.
"""

import json
from typing import Any

from .client import call_claude
from .prompts import BULLET_INSTRUCTIONS, SYSTEM_PROMPT
from .tools import TOOL_SCHEMAS, dispatch


def run_orchestrator(repo_summary: dict[str, Any]) -> str:
    """
    Execute the orchestrator loop for resume bullet generation.

    This function manages the tool-calling conversation with Claude:
    1. Initializes conversation with system prompt and bullet instructions
    2. Passes repository summary to Claude
    3. Loops through tool calls, executing them via dispatch()
    4. Returns final text response when Claude stops calling tools

    Args:
        repo_summary: Repository analysis data containing dependencies, languages, etc.

    Returns:
        Final text response from Claude containing resume bullets

    Raises:
        RuntimeError: If maximum tool loop iterations exceeded (circuit breaker)
        ValueError: If Claude returns unexpected response format

    Example:
        >>> summary = {"dependencies": {"python": ["fastapi"]}, "languages": {"Python": 100}}
        >>> bullets = run_orchestrator(summary)
        >>> print(bullets)
        "Architected REST API using FastAPI..."
    """
    # Safety circuit breaker to prevent infinite API spend
    MAX_TOOL_LOOPS = 5
    tool_loop_count = 0

    # Initialize conversation history with system prompt
    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": f"{SYSTEM_PROMPT}\n\n{BULLET_INSTRUCTIONS}\n\nRepository Summary:\n{json.dumps(repo_summary, indent=2)}"
        }
    ]

    while tool_loop_count < MAX_TOOL_LOOPS:
        # Call Claude with current message history and available tools
        response = call_claude(messages=messages, tools=TOOL_SCHEMAS)

        # Build assistant message from response
        assistant_message: dict[str, Any] = {
            "role": "assistant",
            "content": []
        }

        # Process response content blocks
        has_tool_use = False
        final_text = ""

        for block in response.content:
            if block.type == "text":
                # Text block - could be final answer or intermediate reasoning
                assistant_message["content"].append({
                    "type": "text",
                    "text": block.text
                })
                final_text = block.text

            elif block.type == "tool_use":
                # Tool use block - Claude wants to call a tool
                has_tool_use = True
                tool_loop_count += 1

                # Add tool use to assistant message
                assistant_message["content"].append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })

                # Execute the tool via dispatch
                try:
                    tool_result = dispatch(
                        name=block.name,
                        arguments=block.input,
                        repo_summary=repo_summary
                    )

                    # Convert result to JSON string for Claude
                    result_content = json.dumps(tool_result, indent=2)
                    is_error = False

                except Exception as e:
                    # Tool execution failed - return error to Claude
                    result_content = f"Error executing tool: {str(e)}"
                    is_error = True

                # Append assistant message with tool use
                messages.append(assistant_message)

                # Create tool result message
                tool_result_message: dict[str, Any] = {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_content,
                            "is_error": is_error
                        }
                    ]
                }

                # Append tool result and continue loop
                messages.append(tool_result_message)

                # Break inner loop to re-call Claude with tool result
                break

        # If no tool use detected, Claude has provided final answer
        if not has_tool_use:
            # Append final assistant message
            messages.append(assistant_message)

            # Return the final text response
            if final_text:
                return final_text
            else:
                raise ValueError("Claude returned empty response without tool use")

    # Circuit breaker triggered
    raise RuntimeError(
        f"Maximum tool loop iterations ({MAX_TOOL_LOOPS}) exceeded. "
        "Possible infinite loop detected."
    )
