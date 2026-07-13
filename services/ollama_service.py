from ollama import chat


MODEL = "qwen3:8b"


def ask_llm(prompt):
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content
