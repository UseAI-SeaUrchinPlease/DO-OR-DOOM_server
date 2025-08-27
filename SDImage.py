import requests
import json
import base64
from PIL import Image
import io
import os

# BASE_URL = "https://9a755e97b8550f9e67.gradio.live"
# TXT2IMG_URL = f"{BASE_URL}/sdapi/v1/txt2img"
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") # APIキー


def get_image_by_SD(prompt):
    
    txt2img_url = f"https://api.stability.ai/v2alpha/generation/stable-image/upscale"

    # 3. APIにPOSTリクエストを送信
    try:
        print("画像生成リクエストを送信します...")
        response = requests.post(
            txt2img_url,
            headers={
                "Authorization": f"Bearer {STABILITY_API_KEY}",
                "accept": "application/json"
            },
            files = { "none" :  '' },
            data = {
                "prompt": prompt,
            },
            timeout=30.0 
        )
        
        # レスポンスの検証
        print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
        print(f"Response status code: {response.status_code}")
        
        try:
            # JSONとして解析を試みる
            json_data = response.json()
            print("レスポンスはJSON形式です:")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
            return json_data
        except json.JSONDecodeError:
            # バイナリデータとして処理
            content = response.content
            print(f"レスポンスはバイナリデータです:")
            print(f"データ長: {len(content)} bytes")
            print(f"データ型: {type(content)}")
            
            # 先頭数バイトを16進数で表示
            print("データの先頭20バイト:")
            print(content[:20].hex())
            
            return content
            
    except requests.exceptions.RequestException as e:
        print(f"APIへのリクエスト中にエラーが発生しました: {e}")
        return None