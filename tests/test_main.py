from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_chat_passes_retrieved_context_to_llm(
    monkeypatch,
):
    captured = {}

    def fake_ask_deepseek(
        message,
        history,
        context,
    ):
        captured["message"] = message
        captured["history"] = history
        captured["context"] = context
        return "测试回答"

    monkeypatch.setattr(
        main,
        "ask_deepseek",
        fake_ask_deepseek,
    )

    response = client.post(
        "/chat",
        json={
            "message": (
                "比较星河成长账户和"
                "稳享养老存款的最低起存金额"
            ),
            "user_name": "Joe",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Joe，测试回答"
    }

    assert captured["history"] == []
    assert "星河成长账户" in captured["context"]
    assert "100元" in captured["context"]
    assert "稳享养老存款" in captured["context"]
    assert "10,000元" in captured["context"]


def test_chat_stream_passes_context_to_llm(
    monkeypatch,
):
    captured = {}

    def fake_stream_deepseek(
        message,
        history,
        context,
    ):
        captured["history"] = history
        captured["context"] = context

        yield "第一段"
        yield "第二段"

    monkeypatch.setattr(
        main,
        "stream_deepseek",
        fake_stream_deepseek,
    )

    response = client.post(
        "/chat/stream",
        json={
            "message": (
                "比较星河成长账户和"
                "稳享养老存款的最低起存金额"
            ),
        },
    )

    assert response.status_code == 200
    assert response.text == "第一段第二段"
    assert response.headers[
        "content-type"
    ].startswith("text/plain")

    assert captured["history"] == []
    assert "星河成长账户" in captured["context"]
    assert "100元" in captured["context"]
    assert "稳享养老存款" in captured["context"]
    assert "10,000元" in captured["context"]


def test_chat_follow_up_passes_history_context_to_llm(
    monkeypatch,
):
    captured = {}

    def fake_ask_deepseek(
        message,
        history,
        context,
    ):
        captured["history"] = history
        captured["context"] = context
        return "可以通过手机银行或营业网点办理。"

    monkeypatch.setattr(
        main,
        "ask_deepseek",
        fake_ask_deepseek,
    )

    response = client.post(
        "/chat",
        json={
            "message": "那在哪里办理？",
            "history": [
                {
                    "role": "user",
                    "content": "星河成长账户最低起存金额是多少？",
                },
                {
                    "role": "assistant",
                    "content": "最低起存金额是100元。",
                },
            ],
        },
    )

    assert response.status_code == 200
    assert captured["context"] is not None
    assert "星河成长账户" in captured["context"]
    assert "办理渠道：手机银行、营业网点" in captured["context"]


def test_chat_stream_follow_up_uses_history_context(monkeypatch):
    captured = {}

    def fake_stream_deepseek(message, history, context):
        captured["history"] = history
        captured["context"] = context
        yield "测试回答"

    # monkeypatch是pytest提供的一个fixture，用于在测试中临时修改对象的属性或方法
    monkeypatch.setattr(main, "stream_deepseek", fake_stream_deepseek)

    response = client.post(
        "/chat/stream",
        json={
            "message": "那在哪里办理？",
            "history": [
                {
                    "role": "user",
                    "content": "星河成长账户最低起存金额是多少？",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.text == "测试回答"
    assert captured["history"][0]["role"] == "user"
    assert captured["context"] is not None
    assert "星河成长账户" in captured["context"]
