import requests
import json
import os
import aiohttp

# BASE_URL = "https://9a755e97b8550f9e67.gradio.live"
# TXT2IMG_URL = f"{BASE_URL}/sdapi/v1/txt2img"
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") # APIキー


async def send_generation_request_async(session, host, params):
    """
    aiohttpを使用して非同期でAPIにリクエストを送信するヘルパー関数。
    """
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }

    # multipart/form-data形式でデータを送信するためにFormDataオブジェクトを使用
    form_data = aiohttp.FormData()
    for key, value in params.items():
        form_data.add_field(key, str(value))

    print(f"Sending async REST request to {host}...")
    
    # aiohttp.ClientSession.postを使用して非同期にPOSTリクエストを送信
    response = await session.post(
        host,
        headers=headers,
        data=form_data
    )
    
    # 応答ヘッダーとステータスコードをすぐに確認
    print("--- APIからの応答ヘッダー ---")
    print(f"Status: {response.status}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print("---------------------------")

    if not response.ok:
        # エラーレスポンスも非同期で読み取る
        error_text = await response.text()
        raise Exception(f"HTTP {response.status}: {error_text}")
    
    return response


async def get_image_by_SD_async(prompt):
    """
    Stability AI APIを非同期で呼び出し、画像データを取得するメイン関数。
    """
    txt2img_url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    params = {
        "prompt": prompt,
        "negative_prompt": "",
        "aspect_ratio": "3:2",
        "output_format": "png"
    }

    # aiohttp.ClientSessionを非同期コンテキストマネージャとして使用
    async with aiohttp.ClientSession() as session:
        try:
            print("画像生成リクエストを送信します...")
            # ヘルパー関数をawaitで呼び出す
            response = await send_generation_request_async(
                session,
                txt2img_url,
                params
            )

            # レスポンスを非同期で処理
            # ヘッダーを見てJSONかバイナリかを判断するのがより堅牢
            if response.headers.get('content-type') == 'application/json':
                # JSONとして非同期に解析
                json_data = await response.json()
                print("レスポンスはJSON形式です:")
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
                return json_data # エラーメッセージなどが含まれる場合
            else:
                # バイナリデータ（画像）として非同期に読み込む
                content = await response.read()
                print("レスポンスはバイナリデータです:")
                print(f"データ長: {len(content)} bytes")
                print(f"データ型: {type(content)}")
                
                # 先頭数バイトを16進数で表示
                print("データの先頭20バイト:")
                print(content[:20].hex())
                
                return content
                
        except aiohttp.ClientError as e:
            print(f"APIへのリクエスト中にエラーが発生しました: {e}")
            return None
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            return None
    


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
    params = {
        "prompt" : prompt,
        "negative_prompt" : "",
        "aspect_ratio" : "21:9",
        "output_format": "png"
    }
    
    # Send request
    print(f"Sending REST request to {txt2img_url}...")
    response = await client.post(
        txt2img_url,
        headers=headers,
        files=params
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