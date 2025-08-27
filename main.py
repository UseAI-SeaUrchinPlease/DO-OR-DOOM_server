from fastapi import FastAPI, Request
import httpx
import os
import io
import base64
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from transJson import format_tasks_from_json, _get_content_from_response 
from SDImage import get_image_by_SD


load_dotenv()

app = FastAPI()

@app.get("/")
def health_check():
    """Renderのヘルスチェックに応答するためのエンドポイント"""
    return {"status": "ok"}

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

# グローバル変数としてbase_urlを定義
base_url = None

@app.post("/set-sdserver")
async def set_sd_server(request: Request):
    global base_url
    body = await request.json()
    new_url = body.get("url")
    
    if not new_url:
        return {"status": "error", "message": "URLが指定されていません"}
    
    base_url = new_url
    return {"status": "success", "message": f"Stable Diffusion サーバーのURLを {base_url} に設定しました"}


#### 日記生成API ####

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
    pos_text = _get_content_from_response(pos_data).get("reply")
    neg_text = _get_content_from_response(neg_data).get("reply")

    ### 画像生成API呼び出し ###
    pos_image = None
    neg_image = None

    
    # プロンプトを設定
    DIALY_SYSTEM_PROMPT_IMAGE = "# 命令 " \
    " - あなたはプロンプトチューニングの専門家です" \
    " - stable diffusion が目的に沿った画像を生成できる様に、シンプルであるほど良いとされています" \
    " - 生成するプロンプトはuser から送られる「# 原文」の内容に合わせて次の「# コアプロンプト」「# スタイル」の２つをそれぞれ次にあげる内容に従って考えてください" \
    "# コアプロンプト" \
    " - コアプロンプトとは、主に画像の中心に位置する被写体や中心的なテーマ、主題を指します。タスクにあるものを上げるといいでしょう" \
    "# スタイル" \
    " - 画風を決めます。文章に表された質感を表せるように、かつシンプルな単語にしてください" \
    "作成するプロンプトは、絶対に英語にしてください" \

    
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
                        "content": DIALY_SYSTEM_PROMPT_IMAGE
                    },
                    {
                        "role": "user",
                        "content": ("「# 原文」" + pos_text)
                    }
                ]
            },
            timeout=30.0 # 結構長考タイプのcotomiのためのタイムアウト設定
        )
        
    pos_prompt = _get_content_from_response(response.json()).get("reply")
    print("Positive Prompt:", pos_prompt)

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
                        "content": DIALY_SYSTEM_PROMPT_IMAGE
                    },
                    {
                        "role": "user",
                        "content": ("「# 原文」" + neg_text)
                    }
                ]
            },
            timeout=30.0 # 結構長考タイプのcotomiのためのタイムアウト設定
        )
        
    neg_prompt = _get_content_from_response(response.json())#.get("reply")
    print("Negative Prompt:", neg_prompt)
    # 画像を生成
    pos_image_base64 = get_image_by_SD(pos_prompt)
    neg_image_base64 = get_image_by_SD(neg_prompt)

    # PIL ImageをBase64に変換
    # pos_image_buffer = io.BytesIO()
    # neg_image_buffer = io.BytesIO()
    # pos_image.save(pos_image_buffer, format='PNG')
    # neg_image.save(neg_image_buffer, format='PNG')
    # pos_image_base64 = base64.b64encode(pos_image_buffer.getvalue()).decode('utf-8')
    # neg_image_base64 = base64.b64encode(neg_image_buffer.getvalue()).decode('utf-8')

    dialies = {
        "positive": {
            "text": pos_text,
            "image": pos_image_base64,
        },
        "negative": {
            "text": neg_text,
            "image": neg_image_base64,
        }
    }



    return dialies