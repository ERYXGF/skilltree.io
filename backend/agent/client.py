"""Anthropic Claude API client with retry logic."""

import time
from typing import Any, Optional

import anthropic
from anthropic.types import Message

from ..config import get_settings


def call_claude(
    messages: list[dict[str, Any]],
    tools: Optional[list[dict[str, Any]]] = None,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> Message:
    """
    Call Claude API with exponential backoff retry mechanism.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        tools: Optional list of tool schemas for function calling
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)

    Returns:
        Message: Anthropic Message object containing the response

    Raises:
        anthropic.APIError: If all retries are exhausted
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            # Build request parameters
            params: dict[str, Any] = {
                "model": settings.model_name,
                "max_tokens": 4096,
                "messages": messages,
            }

            # Add tools if provided
            if tools:
                params["tools"] = tools

            # Make the API call
            response = client.messages.create(**params)
            return response

        except (
            anthropic.RateLimitError,
            anthropic.InternalServerError,
            anthropic.APIConnectionError,
        ) as e:
            last_exception = e

            # Don't retry on the last attempt
            if attempt == max_retries:
                break

            # Exponential backoff: delay *= 2 for each retry
            time.sleep(delay)
            delay *= 2

        except anthropic.APIError as e:
            # For other API errors (e.g., invalid request), don't retry
            raise e

    # If we've exhausted all retries, raise the last exception
    raise last_exception  # type: ignore
