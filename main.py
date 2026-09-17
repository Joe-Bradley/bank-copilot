from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import APIError
from pydantic import BaseModel, Field

from llm import ask_deepseek, stream_deepseek
from retrieval import retrieve_product_context

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(
        BASE_DIR / "static" / "index.html"
    )


class ChatResponse(BaseModel):
    answer: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=500)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    user_name: str = Field(default="用户", min_length=1, max_length=50)
    history: list[ChatMessage] = Field(default_factory=list, max_length=10)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="message cannot be blank",
        )

    context = retrieve_product_context(message)
    history = [item.model_dump() for item in request.history]

    try:
        answer = ask_deepseek(
            message,
            history,
            context,
        )
    except APIError as exc:
        raise HTTPException(
            status_code=502,
            detail="大模型服务暂时不可用",
        ) from exc

    return ChatResponse(
        answer=f"{request.user_name}，{answer}"
    )


@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="message cannot be blank",
        )

    context = retrieve_product_context(message)
    history = [item.model_dump() for item in request.history]

    def response_stream():
        try:
            yield from stream_deepseek(
                message,
                history,
                context,
            )
        except APIError as exc:
            print(f"stream error = {exc!r}", flush=True)
            yield "\n[大模型服务暂时不可用]"

    return StreamingResponse(
        response_stream(),
        media_type="text/plain",
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "bank-copilot"}


@app.get("/greet/{name}")
def greet(name: str, language: str = "zh"):
    if language == "en":
        return {"message": f"Hello, {name}"}
    return {"message": f"你好，{name}"}
