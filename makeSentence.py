import httpx
import os
import io
import base64
import re
from dotenv import load_dotenv

from transJson import _get_content_from_response 

CHAT_AI_API_KEY = os.getenv("CHAT_AI_API_KEY") # APIキー

# プロンプトを設定
DIALY_SYSTEM_PROMPT_NEGATIVE = "# 命令 " \
" - あなたは物語の作家です" \
" - キチンとわかりやすい表現で、かつ、作家としてのプライドを持ち、ユーモアを込めて執筆してくささい" \
" - 文章はuserから受け取る「# タスク」を参照して、それらのタスクを達成できなかったときの様子を執筆してください" \
" - 文章は、やろうとしたが失敗したものではなく、" \
" - やる気がなく、できなかったときの様子を描いてください" \
" - 思い返せば、あの時、小さな一歩を踏み出していれば、、、といった後悔を感じさせるものにしてください" \
" - 文章の量は200文字前後にしてください" \
" - 返答はその文章のみとしてください" \
" - この文章について説明文は含まないでください" \

DIALY_SYSTEM_PROMPT_POSITIVE = "# 命令 " \
" - あなたは物語の作家です" \
" - キチンとわかりやすい表現で、かつ、作家としてのプライドを持ち、ユーモアを込めて執筆してくささい" \
" - 文章はuserから受け取る「# タスク」を参照して、それらのタスクを達成したときの様子を執筆してください" \
" - やっぱりあの時、小さな一歩を踏む出していてよかったというような様子を描いてください" \
" - この文章を見た人が、タスクを達成したくなるようなモチベーションの上がる文章にしてください" \
" - 文章の量は200文字前後にしてください" \
" - 返答はその文章のみとしてください" \
" - この文章について説明文は含まないでください" \

DIALY_SYSTEM_PROMPT_IMAGE = "# 命令 " \
" - あなたはプロンプトチューニングの専門家です" \
" - stable diffusion が目的に沿った画像を生成できる様に、シンプルであるほど良いとされています" \
" - 生成するプロンプトはuser から送られる「# 原文」の内容に合わせて次の「# コアプロンプト」「# スタイル」の２つをそれぞれ次にあげる内容に従って考えてください" \
"# コアプロンプト" \
" - コアプロンプトとは、主に画像の中心に位置する被写体や中心的なテーマ、主題を指します。タスクにあるものを上げるといいでしょう" \
"# スタイル" \
" - 画風を決めます。文章に表された質感を表せるように、かつシンプルな単語にしてください" \
"生成するプロンプトは、具体的な「行動」を含めるようにしてください" \
"最終的に作成するプロンプトは「#コアプロンプト」や「#スタイル」などに分けず、ひとまとめにした、英語の１文章にしてください" \
"作成するプロンプトは英語の単語の羅列のみにしてください" \
"作成するプロンプトに改行や「:」「;」などの特殊文字も含まないでください" \
"返答する文章は、絶対に英語のみにし、その他の言語は絶対に含まないでください" \
"プロンプトに関しての説明は含まないでください" \

# 日記文章生成関数
async def make_dialy_sentence(client, tasks: str, positive: bool) -> str:
	"""日記文章を生成する関数

	Args:
		client: httpxの非同期クライアント
		tasks (str): タスクのリストをフォーマットした文字列
		positive (bool): ポジティブな日記を生成するかどうか. Defaults to False.

	Returns:
		str: 生成された日記文章
	"""
	load_dotenv()

	if positive:
		system_prompt = DIALY_SYSTEM_PROMPT_POSITIVE
	else:
		system_prompt = DIALY_SYSTEM_PROMPT_NEGATIVE
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
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": tasks
                    }
                ]
            },
            timeout=30.0 # 結構長考タイプのcotomiのためのタイムアウト設定
        )
	data = response.json()
	return _get_content_from_response(data).get("reply")


# 画像生成プロンプト生成関数
async def generate_prompt(client, text: str, max_retries=3):
    """画像生成用のプロンプトを生成する関数
      Args:
		client: httpxの非同期クライアント
		text (str): 日記文章
		max_retries (int): 非英語文字が含まれていた場合のリトライ回数
        
    Returns:
      	str: 生成された画像プロンプト
	"""
    for attempt in range(max_retries):
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
                        "content": ("「# 原文」" + text)
                    }
                ]
            },
            timeout=30.0
        )
        
        prompt = _get_content_from_response(response.json()).get("reply")
        if is_english_only(prompt):
            return prompt
        print(f"prompt:{prompt}")
        print(f"非英語文字を検出。リトライ {attempt + 1}/{max_retries}")
        
    
    # 全てのリトライが失敗した場合、デフォルトの英語プロンプトを返す
    return "person standing nature simple photo"

# 英語チェック関数
def is_english_only(text):
    # 英数字、スペース、カンマ、ピリオド、ハイフンのみを許可
    return bool(re.match('^[a-zA-Z0-9\s,\.\-]+$', text))
