import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("DEEPSEEK_API_KEY is not configured")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=15.0,
    max_retries=1,
)


def ask_deepseek(
    message: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    messages = [
        {
            "role": "system",
            "content": "你是一名面向初学者的中文AI老师。回答时先给结论，再用一个生活化例子解释，控制在100字以内。",
        },
    ]

    if history:
        messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        stream=False,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("DeepSeek returned an empty response")

    return answer


def stream_deepseek(
    message: str,
    history: list[dict[str, str]] | None = None,
):
    messages = [
        {
            "role": "system",
            "content": "你是一名面向初学者的中文AI老师。回答时先给结论，再用一个生活化例子解释，控制在100字以内。",
        },
    ]

    if history:
        messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        stream=True,
    )

    for chunk in response:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content
        if content:
            yield content
