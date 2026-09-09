import json
from typing import Any

from openai import OpenAI

from backend.core.config import settings


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
    timeout=120.0,
    max_retries=2,
)


def ask_llm(prompt: str) -> str:
    """
    Send a normal text prompt to OpenRouter.
    """

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_completion_tokens=4096,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("OpenRouter returned an empty response")

    return content


def ask_json(
    prompt: str,
    *,
    name: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    """
    Send a structured JSON request to OpenRouter.
    """

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_completion_tokens=2048,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": name,
                "strict": True,
                "schema": schema,
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("OpenRouter returned an empty response")

    return json.loads(content)