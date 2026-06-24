"""
Test suite for the orchestrator loop.

This test verifies that the orchestrator correctly:
1. Handles tool_use responses from Claude
2. Executes tools via dispatch
3. Loops through multiple tool calls
4. Returns final text when Claude stops calling tools
5. Enforces circuit breaker to prevent infinite loops
"""

import sys
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agent.orchestrator import run_orchestrator
from backend.agent.tools import TOOL_SCHEMAS


def test_orchestrator_tool_loop():
    """
    Test that orchestrator correctly loops through tool calls and returns final text.

    Scenario:
    - Call 1: Claude returns tool_use for detect_stack
    - Call 2: Claude returns tool_use for map_to_jobs
    - Call 3: Claude returns final text response
    """
    print("\n=== Testing Orchestrator Tool Loop ===")

    # Mock repository summary
    repo_summary = {
        "dependencies": {
            "python": ["fastapi", "pytest"],
            "javascript": ["react", "vite"]
        },
        "languages": {
            "Python": 65.5,
            "JavaScript": 34.5
        }
    }

    # Create mock responses for each call
    mock_response_1 = MagicMock()
    mock_response_1.content = [
        MagicMock(
            type="tool_use",
            id="tool_1",
            name="detect_stack",
            input={"repo_summary": repo_summary}
        )
    ]

    mock_response_2 = MagicMock()
    mock_response_2.content = [
        MagicMock(
            type="tool_use",
            id="tool_2",
            name="map_to_jobs",
            input={"technologies": ["fastapi", "pytest", "react", "vite"]}
        )
    ]

    mock_response_3 = MagicMock()
    mock_response_3.content = [
        MagicMock(
            type="text",
            text="• Architected REST API using FastAPI and React, serving 100K+ requests/day\n• Implemented comprehensive test suite with Pytest, achieving 95% code coverage"
        )
    ]

    # Patch call_claude to return our mock responses in sequence
    with patch("backend.agent.orchestrator.call_claude") as mock_call_claude:
        mock_call_claude.side_effect = [mock_response_1, mock_response_2, mock_response_3]

        # Run orchestrator
        result = run_orchestrator(repo_summary)

        # Verify call_claude was called 3 times
        assert mock_call_claude.call_count == 3, f"Expected 3 calls to Claude, got {mock_call_claude.call_count}"
        print(f"✓ Claude called {mock_call_claude.call_count} times (expected 3)")

        # Verify final result is text
        assert isinstance(result, str), f"Expected string result, got {type(result)}"
        assert "FastAPI" in result, "Expected FastAPI in final result"
        assert "Pytest" in result, "Expected Pytest in final result"
        print(f"✓ Final result is text: {result[:80]}...")

        # Note: The messages list is mutated in place, so all calls see the same list reference
        # We need to verify the behavior by checking that messages accumulate correctly

        # Verify tools were passed to all calls
        for i, call_args in enumerate(mock_call_claude.call_args_list):
            call_kwargs = call_args[1]
            assert "tools" in call_kwargs, f"Call {i+1} should have tools parameter"
            assert call_kwargs["tools"] == TOOL_SCHEMAS, f"Call {i+1} should pass TOOL_SCHEMAS"
        print("✓ Tools passed to all Claude calls")

        # Verify the final message list has accumulated properly
        # Should have: initial user message + (assistant + tool_result) * 2 + final assistant
        final_call_kwargs = mock_call_claude.call_args_list[-1][1]
        final_messages = final_call_kwargs["messages"]

        # Count message types
        user_messages = sum(1 for m in final_messages if m["role"] == "user")
        assistant_messages = sum(1 for m in final_messages if m["role"] == "assistant")

        # Should have: 1 initial user + 2 tool_result users = 3 user messages
        # Should have: 2 tool-use assistants + 1 final assistant = 3 assistant messages
        assert user_messages == 3, f"Expected 3 user messages, got {user_messages}"
        assert assistant_messages == 3, f"Expected 3 assistant messages, got {assistant_messages}"
        print(f"✓ Message history accumulated correctly ({len(final_messages)} total messages)")

        # Verify tools were passed
        first_call_tools = mock_call_claude.call_args_list[0][1]["tools"]
        assert first_call_tools is not None, "Tools should be passed to Claude"
        assert len(first_call_tools) == 3, f"Expected 3 tools, got {len(first_call_tools)}"
        print(f"✓ Tools passed to Claude: {len(first_call_tools)} schemas")

    print("✓ Orchestrator tool loop test PASSED\n")


def test_orchestrator_circuit_breaker():
    """
    Test that orchestrator enforces circuit breaker to prevent infinite loops.

    Scenario:
    - Claude keeps returning tool_use indefinitely
    - Orchestrator should raise RuntimeError after MAX_TOOL_LOOPS
    """
    print("\n=== Testing Orchestrator Circuit Breaker ===")

    repo_summary = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 100}
    }

    # Create mock response that always returns tool_use
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            type="tool_use",
            id="tool_infinite",
            name="detect_stack",
            input={"repo_summary": repo_summary}
        )
    ]

    with patch("backend.agent.orchestrator.call_claude") as mock_call_claude:
        mock_call_claude.return_value = mock_response

        # Run orchestrator and expect RuntimeError
        try:
            run_orchestrator(repo_summary)
            assert False, "Expected RuntimeError for infinite loop"
        except RuntimeError as e:
            assert "Maximum tool loop iterations" in str(e), f"Unexpected error message: {e}"
            print(f"✓ Circuit breaker triggered: {e}")

        # Verify Claude was called MAX_TOOL_LOOPS times (5)
        # Note: call_count will be 5 because we break after 5 tool uses
        assert mock_call_claude.call_count == 5, f"Expected 5 calls before circuit breaker, got {mock_call_claude.call_count}"
        print(f"✓ Circuit breaker activated after {mock_call_claude.call_count} tool loops")

    print("✓ Circuit breaker test PASSED\n")


def test_orchestrator_no_tool_use():
    """
    Test that orchestrator handles immediate text response (no tool use).

    Scenario:
    - Call 1: Claude returns text immediately without calling tools
    """
    print("\n=== Testing Orchestrator No Tool Use ===")

    repo_summary = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 100}
    }

    # Mock response with immediate text
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            type="text",
            text="• Built FastAPI application with 99.9% uptime"
        )
    ]

    with patch("backend.agent.orchestrator.call_claude") as mock_call_claude:
        mock_call_claude.return_value = mock_response

        result = run_orchestrator(repo_summary)

        # Verify only called once
        assert mock_call_claude.call_count == 1, f"Expected 1 call, got {mock_call_claude.call_count}"
        print(f"✓ Claude called once (no tool use)")

        # Verify result
        assert "FastAPI" in result, "Expected FastAPI in result"
        print(f"✓ Immediate text response: {result}")

    print("✓ No tool use test PASSED\n")


def test_orchestrator_tool_error_handling():
    """
    Test that orchestrator handles tool execution errors gracefully.

    Scenario:
    - Call 1: Claude calls a tool that raises an exception
    - Call 2: Claude receives error and returns final text
    """
    print("\n=== Testing Orchestrator Tool Error Handling ===")

    repo_summary = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 100}
    }

    # Mock response 1: tool_use
    mock_response_1 = MagicMock()
    mock_response_1.content = [
        MagicMock(
            type="tool_use",
            id="tool_error",
            name="invalid_tool",  # This will cause dispatch to raise ValueError
            input={}
        )
    ]

    # Mock response 2: text after error
    mock_response_2 = MagicMock()
    mock_response_2.content = [
        MagicMock(
            type="text",
            text="Unable to process due to tool error"
        )
    ]

    with patch("backend.agent.orchestrator.call_claude") as mock_call_claude:
        mock_call_claude.side_effect = [mock_response_1, mock_response_2]

        result = run_orchestrator(repo_summary)

        # Verify orchestrator continued after error
        assert mock_call_claude.call_count == 2, f"Expected 2 calls, got {mock_call_claude.call_count}"
        print("✓ Orchestrator continued after tool error")

        # Verify final result
        assert isinstance(result, str), "Expected string result"
        print(f"✓ Returned text after error: {result}")

    print("✓ Tool error handling test PASSED\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ORCHESTRATOR TEST SUITE")
    print("="*60)

    try:
        test_orchestrator_tool_loop()
        test_orchestrator_circuit_breaker()
        test_orchestrator_no_tool_use()
        test_orchestrator_tool_error_handling()

        print("="*60)
        print("ALL ORCHESTRATOR TESTS PASSED ✓")
        print("="*60 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
