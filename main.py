from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class ChatResponse(BaseModel):
    answer: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    user_name: str = Field(default="用户", min_length=1, max_length=50)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=400,
            detail="message cannot be blank",
        )
    return ChatResponse(
        answer=f"{request.user_name}，收到你的消息：{message}"
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "bank-copilot"}


@app.get("/greet/{name}")
def greet(name: str, language: str = "zh"):
    if language == "en":
        return {"message": f"Hello, {name}"}
    return {"message": f"你好，{name}"}
