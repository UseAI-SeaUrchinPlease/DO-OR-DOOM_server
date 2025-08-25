from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from transJson import format_tasks_from_json, _get_content_from_response 


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
# CHAT_AI_ENDPOINT = os.getenv("CHAT_AI_ENDPOINT") # APIエンドポイント
CHAT_AI_API_KEY = os.getenv("CHAT_AI_API_KEY") # APIキー
# MODEL_NAME = os.getenv("MODEL_NAME") # モデル名

# プロンプトを設定
DIALY_SYSTEM_PROMPT_NEGATIVE = "# 命令 " \
" - あなたは物語の作家です" \
" - キチンとわかりやすい表現で、かつ、作家としてのプライドを持ち、ユーモアを込めて執筆してくささい" \
" - 文章はuserから受け取る「# タスク」を参照して、それらのタスクを達成できなかったときの様子を執筆してください" \
" - 文章の量は200文字前後にしてください" \
" - 返答はその文章のみとしてください" \
" - この文章について説明文は含まないでください" \

DIALY_SYSTEM_PROMPT_POSITIVE = "# 命令 " \
" - あなたは物語の作家です" \
" - キチンとわかりやすい表現で、かつ、作家としてのプライドを持ち、ユーモアを込めて執筆してくささい" \
" - 文章はuserから受け取る「# タスク」を参照して、それらのタスクを達成したときの様子を執筆してください" \
" - 文章の量は200文字前後にしてください" \
" - 返答はその文章のみとしてください" \
" - この文章について説明文は含まないでください" \

@app.post("/dialy")
async def chat(request: Request):
    body = await request.json()
    tasks = format_tasks_from_json(body)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.aipf.sakura.ad.jp/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {CHAT_AI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "cotomi2-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": DIALY_SYSTEM_PROMPT_POSITIVE
                    },
                    {
                        "role": "user",
                        "content": tasks
                    }
                ]
            },
            timeout=30.0 # 結構長考タイプのcotomiのためのタイムアウト設定
        )
    
    pos_data = response.json()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.aipf.sakura.ad.jp/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {CHAT_AI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "cotomi2-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": DIALY_SYSTEM_PROMPT_NEGATIVE
                    },
                    {
                        "role": "user",
                        "content": tasks
                    }
                ]
            },
            timeout=30.0 # 結構長考タイプのcotomiのためのタイムアウト設定
        )
        
    neg_data = response.json()

    # choices -> message -> content を安全に取り出して返す
    dialies = None
    pos_dialy = _get_content_from_response(pos_data)
    neg_dialy = _get_content_from_response(neg_data)
    dialies = {
        "positive": pos_dialy.get("reply"),
        "negative": neg_dialy.get("reply"),
    }

    return dialies