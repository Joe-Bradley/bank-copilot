from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import APIError
from pydantic import BaseModel, Field

from llm import ask_deepseek, stream_deepseek
from retrieval import retrieve_product_context

#在找到 main.py 所在的文件夹，并把它保存为 BASE_DIR
BASE_DIR = Path(__file__).resolve().parent

#创建一个 FastAPI 应用，并把它保存到变量 app 中
app = FastAPI()


#这段代码是把项目里的 static 文件夹开放给浏览器访问
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


#主页
@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


#获取favicon.ico 图标
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")

#定义ChatResponse返回answer的类
class ChatResponse(BaseModel):
    answer: str

#定义ChatMessage，有role和content两个属性，role只能是"user"或者"assistant"，content是字符串，长度在1到500之间
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=500)

#定义ChatRequest类，有message、user_name和history三个属性，message是字符串，长度在1到500之间，user_name是字符串，默认值为"用户"，长度在1到50之间，history是一个ChatMessage对象的列表，最大长度为10
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    user_name: str = Field(default="用户", min_length=1, max_length=50)
    history: list[ChatMessage] = Field(default_factory=list, max_length=10)


#定义一个POST请求的路由/chat，返回类型为ChatResponse
#传入message、user_name和history三个参数，返回answer
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    #取出请求中的message，并去掉首尾空格
    message = request.message.strip()

    #如果message为空，抛出HTTPException异常，状态码为400，提示"message cannot be blank"
    if not message:
        raise HTTPException(
            status_code=400,
            detail="message cannot be blank",
        )

    #取出请求中的history和context
    #item.model_dump()就是把item对象转换为字典
    #history的类型是list[dict[str, str]]是因为item.model_dump()就是把item对象转换为字典
    #每个字典有两个键，role和content，分别对应ChatMessage对象的role和content属性
    history = [item.model_dump() for item in request.history]


    #调用retrieve_product_context函数，传入message和history，获取context
    #message是用户输入的问题，history是用户和助手的历史对话，context是匹配的产品知识内容，如果没有匹配的内容，返回None
    context = retrieve_product_context(
        message,
        history=history,
    )

    #调用ask_deepseek函数，传入message、history和context，获取answer
    try:
        answer = ask_deepseek(
            message,
            history,
            context,
        )

    #如果调用ask_deepseek函数时发生APIError异常，抛出HTTPException异常，状态码为502，提示"大模型服务暂时不可用"
    except APIError as exc:
        raise HTTPException(
            status_code=502,
            detail="大模型服务暂时不可用",
        ) from exc

    #返回ChatResponse对象，answer属性为"{request.user_name}，{answer}"，即在answer前加上用户的名字
    return ChatResponse(answer=f"{request.user_name}，{answer}")



@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="message cannot be blank",
        )

    history = [item.model_dump() for item in request.history]
    context = retrieve_product_context(message, history=history)

    def response_stream():
        try:
            #生成流式响应，yield from stream_deepseek(message, history, context)就是把stream_deepseek函数的返回值逐个yield出来
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
