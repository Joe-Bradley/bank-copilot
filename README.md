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