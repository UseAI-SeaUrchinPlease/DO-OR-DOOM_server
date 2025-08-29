from fastapi import FastAPI, Request
import asyncio
import httpx
import os
import json
import copy
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from transJson import format_tasks_from_json, _get_content_from_response, truncate_dict_values
from SDImage import get_image_by_SD
from makeSentence import make_dialy_sentence, generate_dialy_prompt, make_badge_name, make_badge_sentence, generate_badge_prompt


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


#### ヘルスチェック用エンドポイント ####
@app.get("/")
def health_check():
    """Renderのヘルスチェックに応答するためのエンドポイント"""
    return {"status": "ok"}


#### 日記生成用エンドポイント ####
@app.post("/dialy")
async def make_dialy(request: Request):
    # リクエストボディをJSONとして取得
    body = await request.json()
    # JSONからタスクを抽出し、フォーマット
    tasks = format_tasks_from_json(body)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 文章を生成（並列で実行）
        # asyncio.gatherで2つのタスクを並列実行し、両方の完了を待つ
        pos_text, neg_text = await asyncio.gather(
            make_dialy_sentence(client, tasks, True), 
            make_dialy_sentence(client, tasks, False)
        )

    pos_image_base64 = None
    neg_image_base64 = None
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 画像生成プロンプトを生成（並列で実行）
        # asyncio.gatherで2つのタスクを並列実行し、両方の完了を待つ
        pos_prompt, neg_prompt = await asyncio.gather(
            generate_dialy_prompt(client, pos_text), 
            generate_dialy_prompt(client, neg_text))

        # 生成したプロンプトを出力(ログに表示)
        print("Positive Prompt:", pos_prompt)
        print("Negative Prompt:", neg_prompt)

        pos_prompt = "positive, active, " + pos_prompt
        neg_prompt = "negative, inactive, " + neg_prompt

    # 画像を生成 (base64形式で返されるのでそのまま)
    pos_image_base64 = get_image_by_SD(pos_prompt)
    neg_image_base64 = get_image_by_SD(neg_prompt)
    # レスポンス用の辞書を作成
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

    # デバッグ用ログを見やすくするためにバリューを省略
    dialies_copy = copy.deepcopy(dialies)
    dialies_truncated = truncate_dict_values(dialies_copy, 30)
    dialies_json = json.dumps(dialies_truncated, ensure_ascii=False)
    print("Response JSON:", dialies_json)

    return dialies

### バッジ生成用エンドポイント ###
@app.post("/badge")
async def make_badge(request: Request):
    # リクエストボディをJSONとして取得
    body = await request.json()
    # JSONからタスクを抽出し、フォーマット
    tasks = format_tasks_from_json(body)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 文章と名前を生成
        name = await make_badge_name(client, tasks)
        text = await make_badge_sentence(client, tasks)

    prompt = None
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 画像生成プロンプトを生成
        prompt = await generate_badge_prompt(client, text)

        # 生成したプロンプトを出力(ログに表示)
        print("Badge Prompt:", prompt)

        prompt = "badge, icon, square" + prompt

    # 画像を生成 (base64形式で返されるのでそのまま)
    image_base64 = get_image_by_SD(prompt)

    # レスポンス用の辞書を作成
    badge = {
        "name": name,
        "text": text,
        "image": image_base64,
    }

    # デバッグ用ログを見やすくするためにバリューを省略
    badge_copy = copy.deepcopy(badge)
    badge_truncated = truncate_dict_values(badge_copy, 30)
    badge_json = json.dumps(badge_truncated, ensure_ascii=False)
    print("Response JSON:", badge_json)

    return badge