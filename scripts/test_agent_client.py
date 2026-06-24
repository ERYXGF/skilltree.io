"""Test suite for backend.agent.client module."""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import anthropic
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.agent.client import call_claude  # noqa: E402


def test_call_claude_success():
    """Test successful Claude API call without retries."""
    mock_response = MagicMock()
    mock_response.content = [{"type": "text", "text": "Hello!"}]

    with patch("backend.agent.client.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        messages = [{"role": "user", "content": "Hello"}]
        result = call_claude(messages)

        assert result == mock_response
        mock_client.messages.create.assert_called_once()


def test_call_claude_with_tools():
    """Test Claude API call with tools parameter."""
    mock_response = MagicMock()

    with patch("backend.agent.client.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        messages = [{"role": "user", "content": "Analyze this"}]
        tools = [{"name": "test_tool", "description": "A test tool"}]

        result = call_claude(messages, tools=tools)

        assert result == mock_response
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["tools"] == tools


def test_call_claude_retry_on_rate_limit():
    """Test retry mechanism fires on RateLimitError."""
    mock_response = MagicMock()

    with patch("backend.agent.client.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()

        # First call raises RateLimitError, second succeeds
        mock_client.messages.create.side_effect = [
            anthropic.RateLimitError("Rate limit exceeded", response=MagicMock(), body=None),
            mock_response,
        ]
        mock_anthropic.return_value = mock_client

        with patch("backend.agent.client.time.sleep") as mock_sleep:
            messages = [{"role": "user", "content": "Test"}]
            result = call_claude(messages, max_retries=3, initial_delay=0.5)

            assert result == mock_response
            assert mock_client.messages.create.call_count == 2
            # Verify exponential backoff was called with initial delay
            mock_sleep.assert_called_once_with(0.5)


def test_call_claude_retry_on_internal_server_error():
    """Test retry mechanism fires on InternalServerError (500)."""
    mock_response = MagicMock()

    with patch("backend.agent.client.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()

        # First two calls raise 500 error, third succeeds
        mock_client.messages.create.side_effect = [
            anthropic.InternalServerError("Server error", response=MagicMock(), body=None),
            anthropic.InternalServerError("Server error", response=MagicMock(), body=None),
            mock_response,
        ]
        mock_anthropic.return_value = mock_client

        with patch("backend.agent.client.time.sleep") as mock_sleep:
            messages = [{"role": "user", "content": "Test"}]
            result = call_claude(messages, max_retries=3, initial_delay=1.0)

            assert result == mock_response
            assert mock_client.messages.create.call_count == 3
            # Verify exponential backoff: 1.0, then 2.0
            assert mock_sleep.call_count == 2
            assert mock_sleep.call_args_list[0][0][0] == 1.0
            assert mock_sleep.call_args_list[1][0][0] == 2.0


def test_call_claude_exhausted_retries():
    """Test that exception is raised when all retries are exhausted."""
    with patch("backend.agent.client.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()

        # All calls raise RateLimitError
        mock_client.messages.create.side_effect = anthropic.RateLimitError(
            "Rate limit exceeded", response=MagicMock(), body=None
        )
        mock_anthropic.return_value = mock_client

        with patch("backend.agent.client.time.sleep"):
            messages = [{"role": "user", "content": "Test"}]

            with pytest.raises(anthropic.RateLimitError):
                call_claude(messages, max_retries=2, initial_delay=0.1)

            # Should attempt initial call + 2 retries = 3 total
            assert mock_client.messages.create.call_count == 3


def test_call_claude_no_retry_on_invalid_request():
    """Test that non-retryable errors (e.g., BadRequestError) are raised immediately."""
    with patch("backend.agent.client.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()

        # Raise a non-retryable error
        mock_client.messages.create.side_effect = anthropic.BadRequestError(
            "Invalid request", response=MagicMock(), body=None
        )
        mock_anthropic.return_value = mock_client

        messages = [{"role": "user", "content": "Test"}]

        with pytest.raises(anthropic.BadRequestError):
            call_claude(messages, max_retries=3)

        # Should only attempt once (no retries for BadRequestError)
        assert mock_client.messages.create.call_count == 1


def test_call_claude_exponential_backoff_timing():
    """Test that exponential backoff doubles the delay each time."""
    with patch("backend.agent.client.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()

        # Raise errors to trigger all retries
        mock_client.messages.create.side_effect = anthropic.RateLimitError(
            "Rate limit", response=MagicMock(), body=None
        )
        mock_anthropic.return_value = mock_client

        with patch("backend.agent.client.time.sleep") as mock_sleep:
            messages = [{"role": "user", "content": "Test"}]

            try:
                call_claude(messages, max_retries=3, initial_delay=0.5)
            except anthropic.RateLimitError:
                pass

            # Should have 3 sleep calls with exponential backoff: 0.5, 1.0, 2.0
            assert mock_sleep.call_count == 3
            assert mock_sleep.call_args_list[0][0][0] == 0.5
            assert mock_sleep.call_args_list[1][0][0] == 1.0
            assert mock_sleep.call_args_list[2][0][0] == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
