from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()

# CORS設定（開発中のみ全て許可、本番では適切に設定すること）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発中は全て許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 環境変数から各変数を取得
CHAT_AI_ENDPOINT = os.getenv("CHAT_AI_ENDPOINT") # APIエンドポイント
# CHAT_AI_API_KEY = os.getenv("CHAT_AI_API_KEY") # APIキー
# MODEL_NAME = os.getenv("MODEL_NAME") # モデル名

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.aipf.sakura.ad.jp/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {CHAT_AI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "cotomi2-pro",
                "messages": messages
            },
        )
    
    data = response.json()

    # choices -> message -> content を安全に取り出して返す
    assistant = None
    choices = data.get("choices")
    if isinstance(choices, list) and len(choices) > 0:
        first = choices[0]
        if isinstance(first, dict):
            msg = first.get("message")
            if isinstance(msg, dict):
                assistant = msg.get("content")

    if assistant is None:
        # 取り出せなければ元のdataをそのまま返す（デバッグ用）
        assistant = data

    return {"reply": assistant}