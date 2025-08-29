import requests
import json
import base64
from PIL import Image
import io
import os
import time

# BASE_URL = "https://9a755e97b8550f9e67.gradio.live"
# TXT2IMG_URL = f"{BASE_URL}/sdapi/v1/txt2img"
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") # APIキー

    


async def get_image_by_SD(client, prompt: str):
    """Stable Diffusionを使って画像を生成し、base64エンコードされた画像データを返す関数
    Args:
        client: httpxの非同期クライアント
        prompt (str): 画像生成のためのプロンプト
    Returns:
        bytes: base64エンコードされた画像データ
    """

    txt2img_url = f"https://api.stability.ai/v2beta/stable-image/generate/ultra"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }
    files = {}
    params = {
        "prompt" : prompt,
        "negative_prompt" : "",
        "aspect_ratio" : "5:2",
        "output_format": "png"
    }
    
    # Send request
    print(f"Sending REST request to {txt2img_url}...")
    response = await client.post(
        txt2img_url,
        headers=headers,
        data=params
    )
    response_dict = json.loads(response.text)

    # --- デバッグのためのコードを追加 ---
    print("--- APIからの完全な応答 ---")
    print(json.dumps(response_dict, indent=2, ensure_ascii=False))
    print("---------------------------")
    # --------------------------------
    # if not response.ok:
        # raise Exception(f"HTTP {response.status_code}: {response.text}")

    # 3. APIにPOSTリクエストを送信
    # try:
        # print("画像生成リクエストを送信します...")
        # response = send_async_generation_request(
            # client,
            # txt2img_url,
            # params
        # )
        
        # レスポンスの検証
        # print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
        # print(f"Response status code: {response.status_code}")
        # 
    return response.json().get("image", [None]) 
            
    # except requests.exceptions.RequestException as e:
        # print(f"APIへのリクエスト中にエラーが発生しました: {e}")
        # return None
    

async def send_async_generation_request(client, host, params, files = None):

    # リクエストのヘッダ設定
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }

    if files is None:
        files = {}

    # Encode parameters
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != '':
        files["image"] = open(image, 'rb')
    if mask is not None and mask != '':
        files["mask"] = open(mask, 'rb')
    if len(files)==0:
        files["none"] = ''

    # Send request
    print(f"Sending REST request to {host}...")
    response = await client.post(
        host,
        headers=headers,
        files=files,
        data=params
    )
    response_dict = json.loads(response.text)

    # --- デバッグのためのコードを追加 ---
    print("--- APIからの完全な応答 ---")
    print(json.dumps(response_dict, indent=2, ensure_ascii=False))
    print("---------------------------")
    # --------------------------------
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    return response