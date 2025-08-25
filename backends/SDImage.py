import requests
import json
import base64
from PIL import Image
import io

# BASE_URL = "https://9a755e97b8550f9e67.gradio.live"
# TXT2IMG_URL = f"{BASE_URL}/sdapi/v1/txt2img"


def get_image_by_SD(prompt, base_url):
    
    txt2img_url = f"{base_url}/sdapi/v1/txt2img"

    payload = {
        "prompt": prompt,
        "negative_prompt": "",
        "steps": 25,
        "width": 512,
        "height": 768,
        "cfg_scale": 7,
        "seed": -1  # -1にするとランダムになります
    }
    # 3. APIにPOSTリクエストを送信
    try:
        print("画像生成リクエストを送信します...")
        response = requests.post(url=txt2img_url, json=payload)
        response.raise_for_status() 
        r = response.json()
        # 4. レスポンスから画像データを取得して保存
        if 'images' in r and len(r['images']) > 0:
            image_data = r['images'][0]
            image_bytes = base64.b64decode(image_data.split(",",1)[0] if "," in image_data else image_data)
            image = Image.open(io.BytesIO(image_bytes))
            print("画像生成が完了しました。")
            return image
        else:
            print("エラー: レスポンスに画像データが含まれていませんでした。")
    except requests.exceptions.RequestException as e:
        print(f"APIへのリクエスト中にエラーが発生しました: {e}")