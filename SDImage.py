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


def get_image_by_SD(prompt):
    
    txt2img_url = f"https://api.stability.ai/v2beta/stable-image/generate/ultra"
    params = {
        "prompt" : prompt,
        "negative_prompt" : "",
        "output_format": "png"
    }

    # 3. APIにPOSTリクエストを送信
    try:
        print("画像生成リクエストを送信します...")
        response = send_async_generation_request(
            txt2img_url,
            params
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
    

def send_async_generation_request(
    host,
    params,
    files = None
):
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
    response = requests.post(
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

    # Process async response
    generation_id = response_dict.get("id", None)
    assert generation_id is not None, "Expected id in response"

    # Loop until result or timeout
    timeout = int(os.getenv("WORKER_TIMEOUT", 500))
    start = time.time()
    status_code = 202
    while status_code == 202:
        print(f"Polling results at https://api.stability.ai/v2beta/results/{generation_id}")
        response = requests.get(
            f"https://api.stability.ai/v2beta/results/{generation_id}",
            headers={
                **headers,
                "Accept": "*/*"
            },
        )

        if not response.ok:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        status_code = response.status_code
        time.sleep(10)
        if time.time() - start > timeout:
            raise Exception(f"Timeout after {timeout} seconds")

    return response