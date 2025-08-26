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
        response.raise_for_status() 
        r = response.json()
        # 4. レスポンスから画像データを取得して保存
        if 'images' in r and len(r['images']) > 0:
            image_data = r['images'][0]
            # Base64デコード前にデータの形式を確認
            if isinstance(image_data, str):
                # Base64文字列から余分なヘッダー部分を除去
                if ',' in image_data:
                    base64_data = image_data.split(',')[1]
                else:
                    base64_data = image_data
                
                try:
                    # Base64デコード
                    image_bytes = base64.b64decode(base64_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    print("画像生成が完了しました。")
                    return image
                except base64.binascii.Error as e:
                    print(f"Base64デコードエラー: {e}")
                    return None
            else:
                print(f"予期しない画像データ形式: {type(image_data)}")
                return None
        else:
            print("エラー: レスポンスに画像データが含まれていませんでした。")
    except requests.exceptions.RequestException as e:
        print(f"APIへのリクエスト中にエラーが発生しました: {e}")