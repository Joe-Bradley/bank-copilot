from typing import Literal

from fastapi import FastAPI, HTTPException
from openai import APIError
from pydantic import BaseModel, Field

from llm import ask_deepseek

app = FastAPI()


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
    
    history = [item.model_dump() for item in request.history]

    try:
        answer = ask_deepseek(message, history)
    except APIError as exc:
        raise HTTPException(
            status_code=502,
            detail="大模型服务暂时不可用",
        ) from exc

    return ChatResponse(
        answer=f"{request.user_name}，{answer}"
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "bank-copilot"}


@app.get("/greet/{name}")
def greet(name: str, language: str = "zh"):
    if language == "en":
        return {"message": f"Hello, {name}"}
    return {"message": f"你好，{name}"}
