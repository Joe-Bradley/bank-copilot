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
)


def ask_deepseek(message: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "system",
                "content": "你是一名回答简洁、准确的中文助手。",
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        stream=False,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("DeepSeek returned an empty response")

    return answer