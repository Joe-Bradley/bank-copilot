# Curl Test Cases

运行测试前，先启动服务：

```bash
uv run uvicorn main:app --reload
```

## Health Check

```bash
curl -i http://127.0.0.1:8000/health
```

## Chat

使用默认用户名：

```bash
curl -i -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好"}'
```

指定用户名：

```bash
curl -i -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","user_name":"XL"}'
```

测试缺少 `message`，预期返回 `422`：

```bash
curl -i -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{}'
```

测试空白消息，预期返回 `400`：

```bash
curl -i -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"   "}'
```

## Greeting

默认中文：

```bash
curl -i http://127.0.0.1:8000/greet/XL
```

指定英文：

```bash
curl -i "http://127.0.0.1:8000/greet/XL?language=en"
```

## Multi-turn Chat

`history` 用于把之前的对话一起发送给模型，最多包含 10 条消息。每条消息的 `role` 只能是 `user` 或 `assistant`。

```bash
curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"我最喜欢的数字是什么？","user_name":"Joe","history":[{"role":"user","content":"我最喜欢的数字是17"},{"role":"assistant","content":"好的，我记住了"}]}'
```

## Streaming Chat

`POST /chat/stream` 会在 DeepSeek 生成内容时逐段返回纯文本。`curl -N` 会关闭客户端缓冲，让每个片段到达后立即显示。

```bash
curl -N -i -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"用一句话解释生成器","user_name":"Joe"}'
```

流式接口同样支持最多 10 条历史消息：

```bash
curl -N -i -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"我最喜欢的数字是什么？","user_name":"Joe","history":[{"role":"user","content":"我最喜欢的数字是17"},{"role":"assistant","content":"好的，我记住了"}]}'
```

空白消息会在流开始前返回 `400`。如果模型服务在流开始后失败，HTTP 状态码已经发送，接口会在正文末尾返回 `[大模型服务暂时不可用]`。
