from types import SimpleNamespace

import llm


def test_ask_deepseek_uses_non_streaming_request(monkeypatch):
    captured = {}

    def fake_create(*, model, messages, stream):
        captured["model"] = model
        captured["messages"] = messages
        captured["stream"] = stream
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="模拟回答")
                )
            ]
        )

    monkeypatch.setattr(
        llm.client.chat.completions,
        "create",
        fake_create,
    )

    answer = llm.ask_deepseek("你好")

    assert answer == "模拟回答"
    assert captured["model"] == "deepseek-flash"
    assert captured["stream"] is False
    assert captured["messages"][-1] == {
        "role": "user",
        "content": "你好",
    }


def test_stream_deepseek_yields_nonempty_chunks(monkeypatch):
    captured = {}

    def fake_create(*, model, messages, stream):
        captured["stream"] = stream
        return [
            SimpleNamespace(
                choices=[
                    SimpleNamespace(delta=SimpleNamespace(content="第一段"))
                ]
            ),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(delta=SimpleNamespace(content=""))
                ]
            ),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(delta=SimpleNamespace(content="第二段"))
                ]
            ),
        ]

    monkeypatch.setattr(
        llm.client.chat.completions,
        "create",
        fake_create,
    )

    chunks = list(llm.stream_deepseek("你好"))

    assert captured["stream"] is True
    assert chunks == ["第一段", "第二段"]