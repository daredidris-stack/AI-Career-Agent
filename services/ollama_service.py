import queue
import threading
import time
from collections.abc import Callable
from typing import Any

from ollama import chat

from backend.core.settings import (
    AI_MAX_PROMPT_CHARACTERS,
    AI_MAX_RETRIES,
    AI_MODEL,
    AI_REQUEST_TIMEOUT_SECONDS,
)


MODEL = AI_MODEL


class AIRequestTimeoutError(TimeoutError):
    pass


def reliable_chat(
    prompt: str,
    *,
    chat_callable: Callable[..., Any] = chat,
    response_format: str | dict | None = None,
):
    """Run a bounded AI call with a small retry budget."""
    prompt = prompt[:AI_MAX_PROMPT_CHARACTERS]
    last_error: Exception | None = None

    for attempt in range(AI_MAX_RETRIES + 1):
        try:
            return _call_with_timeout(
                chat_callable,
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                think=False,
                **({"format": response_format} if response_format else {}),
            )
        except Exception as error:
            last_error = error
            if attempt < AI_MAX_RETRIES:
                time.sleep(0.15 * (attempt + 1))

    raise last_error or RuntimeError("AI request failed.")


def _call_with_timeout(chat_callable: Callable[..., Any], **kwargs):
    result_queue: queue.Queue = queue.Queue(maxsize=1)

    def invoke() -> None:
        try:
            result_queue.put((True, chat_callable(**kwargs)), block=False)
        except Exception as error:
            result_queue.put((False, error), block=False)

    worker = threading.Thread(target=invoke, daemon=True)
    worker.start()
    try:
        succeeded, result = result_queue.get(
            timeout=AI_REQUEST_TIMEOUT_SECONDS
        )
    except queue.Empty as error:
        raise AIRequestTimeoutError(
            f"AI request exceeded {AI_REQUEST_TIMEOUT_SECONDS:g} seconds."
        ) from error

    if succeeded:
        return result
    raise result


def ask_llm(prompt):
    response = reliable_chat(prompt)

    return response.message.content
