# Bank Copilot

一个使用 FastAPI、DeepSeek 和原生 JavaScript 构建的流式 AI 聊天应用。

## Features

- FastAPI 聊天接口
- DeepSeek 流式回答
- 最多 10 条多轮对话历史
- 浏览器 `localStorage` 持久化
- 清空对话
- 桌面和手机响应式布局
- 上游模型错误处理

## Run Locally

启动服务：

```bash
uv run uvicorn main:app --reload
```

打开浏览器：

```text
http://127.0.0.1:8000/
```

项目需要在 `.env` 中配置 `DEEPSEEK_API_KEY`。不要提交 `.env` 或公开密钥。

## Project Structure

```text
bank-copilot/
├── main.py              # FastAPI 路由和 HTTP 响应
├── llm.py               # DeepSeek 模型调用
├── static/
│   ├── index.html       # 页面结构
│   ├── app.js           # 聊天交互和历史记录
│   └── style.css        # 页面样式
├── pyproject.toml
└── README.md
```

## Browser Chat

浏览器使用 `POST /chat/stream` 获取流式回答。

对话历史最多保留 10 条，并存储在浏览器的 `bankCopilotHistory` 中。点击“清空对话”可以删除本地历史。

## Curl Test Cases

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
