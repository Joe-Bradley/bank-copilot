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


def build_messages(
    message: str,
    history: list[dict[str, str]] | None = None,
    context: str | None = None,
) -> list[dict[str, str]]:
    system_content = (
        "你是一名面向初学者的中文AI老师。"
        "回答时先给结论，再用一个生活化例子解释，"
        "控制在100字以内。"
    )

    if context:
        system_content += (
            "\n请仅根据以下产品资料回答产品事实。"
            "资料未提及的信息必须明确说不知道，不要猜测。"
            f"\n\n{context}"
        )
    else:
        system_content += (
            "\n当前没有检索到匹配的产品资料。"
            "如果用户询问具体产品事实，请明确说明"
            "知识库中没有相关信息，不要猜测。"
        )

    messages = [
        {
            "role": "system",
            "content": system_content,
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

    return messages


def ask_deepseek(
    message: str,
    history: list[dict[str, str]] | None = None,
    context: str | None = None,
) -> str:
    messages = build_messages(
        message,
        history,
        context,
    )

    response = client.chat.completions.create(
        model="deepseek-flash",
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
    context: str | None = None,
):

    # message包含用户当前输入的问题，history包含用户和助手的历史对话，context包含匹配的产品知识内容。
    messages = build_messages(
        message,
        history,
        context,
    )

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        # 和ask_deepseek函数不同，stream_deepseek函数的stream参数为True，表示返回流式响应，用yield逐个返回响应内容，而不是一次性返回完整的响应内容。
        stream=True,
    )

    for chunk in response:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content
        if content:
            yield content
