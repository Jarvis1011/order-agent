"""訂單管家 API — 自訂的 FastAPI + ADK 服務層。

取代 `adk api_server`:內建端點的事件格式太原始(欄位多、前端要自己猜語意),
這裡把 Runner 的事件流翻譯成專為前端設計的精簡協定:

    {"type": "delta",       "text": "..."}                  # 逐字片段(追加)
    {"type": "text",        "text": "..."}                  # 段落完整文字(覆蓋)
    {"type": "tool_call",   "tool": "...", "args": {...}}   # Agent 呼叫工具
    {"type": "tool_result", "tool": "...", "response": ...} # 工具執行結果
    {"type": "done"}                                        # 本輪結束
    {"type": "error",       "message": "..."}               # 發生錯誤

啟動:uvicorn server.main:app --port 8000
"""

import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("my_agent/.env")  # uvicorn 不會像 adk CLI 那樣自動載入 .env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import BaseModel

from my_agent.agent import root_agent

APP_NAME = "order_agent"
USER_ID = "u1"  # 單人 demo;多使用者時改由登入身分帶入

app = FastAPI(title="訂單管家 API")

# 開發時前端走 Vite proxy(同源),這層 CORS 是為了直連與部署後的跨網域情境
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)


class ChatRequest(BaseModel):
    session_id: str
    message: str


def sse(payload: dict) -> str:
    """打包成 SSE 格式;ensure_ascii=False 讓中文以原文傳輸(省流量、好除錯)"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.post("/api/chat")
async def chat(req: ChatRequest):
    # session 不存在就建,前端從此不用管 session 生命週期
    session = await runner.session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=req.session_id
    )
    if session is None:
        await runner.session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=req.session_id
        )

    new_message = types.Content(role="user", parts=[types.Part(text=req.message)])

    async def event_stream():
        try:
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=req.session_id,
                new_message=new_message,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            ):
                parts = event.content.parts if event.content and event.content.parts else []
                for part in parts:
                    # 同一個 function_call 會在 partial 與彙總事件各出現一次,
                    # 只取彙總(非 partial),否則前端側欄會畫出重複步驟
                    if part.function_call:
                        if not event.partial:
                            yield sse({
                                "type": "tool_call",
                                "tool": part.function_call.name,
                                "args": part.function_call.args,
                            })
                    elif part.function_response:
                        if not event.partial:
                            yield sse({
                                "type": "tool_result",
                                "tool": part.function_response.name,
                                "response": part.function_response.response,
                            })
                    elif part.text:
                        yield sse({
                            "type": "delta" if event.partial else "text",
                            "text": part.text,
                        })
            yield sse({"type": "done"})
        except Exception as exc:  # 錯誤也走事件流告知前端,而不是讓連線無聲斷掉
            yield sse({"type": "error", "message": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# 生產環境(Docker):FastAPI 直接 serve 打包好的前端;開發時 dist 不存在,自動跳過
_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=_dist, html=True), name="frontend")
