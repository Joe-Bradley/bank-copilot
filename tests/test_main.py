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
