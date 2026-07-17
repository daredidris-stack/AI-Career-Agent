import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from services.ollama_service import AIRequestTimeoutError, reliable_chat


class OllamaServiceTests(unittest.TestCase):
    @patch("services.ollama_service.AI_MAX_RETRIES", 1)
    def test_retries_transient_provider_failure(self):
        response = SimpleNamespace(message=SimpleNamespace(content="ok"))
        provider = Mock(side_effect=[RuntimeError("busy"), response])

        result = reliable_chat("prompt", chat_callable=provider)

        self.assertEqual(result, response)
        self.assertEqual(provider.call_count, 2)

    @patch("services.ollama_service.AI_MAX_RETRIES", 0)
    @patch("services.ollama_service.AI_REQUEST_TIMEOUT_SECONDS", 0.01)
    def test_times_out_slow_provider(self):
        def slow_provider(**_kwargs):
            time.sleep(0.05)

        with self.assertRaises(AIRequestTimeoutError):
            reliable_chat("prompt", chat_callable=slow_provider)

    @patch("services.ollama_service.AI_MAX_PROMPT_CHARACTERS", 8)
    def test_caps_prompt_size(self):
        provider = Mock(
            return_value=SimpleNamespace(
                message=SimpleNamespace(content="ok")
            )
        )

        reliable_chat("1234567890", chat_callable=provider)

        prompt = provider.call_args.kwargs["messages"][0]["content"]
        self.assertEqual(prompt, "12345678")

    def test_disables_extended_model_thinking(self):
        provider = Mock(
            return_value=SimpleNamespace(
                message=SimpleNamespace(content="ok")
            )
        )

        reliable_chat("prompt", chat_callable=provider)

        self.assertIs(provider.call_args.kwargs["think"], False)


if __name__ == "__main__":
    unittest.main()
