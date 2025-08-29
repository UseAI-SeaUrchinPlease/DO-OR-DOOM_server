import httpx
import os
import re
from dotenv import load_dotenv

from transJson import _get_content_from_response 

CHAT_AI_API_KEY = os.getenv("CHAT_AI_API_KEY") # APIキー

# プロンプトを設定
## 日記生成用プロンプト
DIALY_SYSTEM_PROMPT_NEGATIVE = "# 命令 " \
" - あなたは物語の作家です" \
" - キチンとわかりやすい表現で、かつ、作家としてのプライドを持ち、ユーモアを込めて執筆してくささい" \
" - 文章はuserから受け取る「# タスク」を参照して、それらのタスクを達成できなかったときの様子を執筆してください" \
" - 文章は、やろうとしたが失敗したものではなく、" \
" - やる気がなく、そもそもやろうとすらしなかった、怠惰な様子を描いてください" \
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

## 画像生成プロンプト生成用プロンプト
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

## バッジ名前生成用プロンプト
BADGE_SYSTEM_PROMPT_NAME = "# 命令 " \
" - 貴方の作るバッジでタスクを達成した人をねぎらいましょう" \
" - 次にuserから与えられる「# タスク」をもとに、特別なバッジを作りたいです" \
" - 与えるバッジにユニークで唯一無二で、ユーモアあふれる名前を作ってください" \
" - 考えるバッジの名前は8文字以内にしてください" \
" - 名前は、日本語で、ことがあそびを混ぜるとなおよいでしょう" \
" - 名前についての説明は含まないでください" \
" - 返答は名前のみにしてください" \
" - 返答は、１つの名前に絞ってください" \

## バッジ文章生成用プロンプト
BADGE_SYSTEM_PROMPT_TEXT = "# 命令 " \
" - 貴方は人をほめたたえるプロです" \
" - 貴方の書く文章でタスクを達成した人をねぎらいましょう" \
" - 次にuserから与えられる「# タスク」をもとに、特別なバッジを作りたいです" \
" - バッジに対しての、ユーモアあふれる、読んだ人がまたタスクを達成したくなるような文章を作成してください" \
" - 日本語特有の言葉遊びなどを含めるとよりよいです" \
" - 文章は100文字程度にしてください" \
" - 生成した文章に関しての説明は含まないでください" \

## バッジ画像生成用プロンプト
BADGE_SYSTEM_PROMPT_IMAGE = "# 命令 " \
" - あなたは、画像生成プロンプトを作成するプロです" \
" - 次にuserから与えられる「# 原文」をもとに、特別なバッジを作りたいです" \
" - Stable Diffusionで画像を生成するために、完全に英語のみの生成プロンプトを作成してください" \
" - 抽象的な画像にして、独特な雰囲気を持たせてください" \
" - でも、確実に、原文の内容をイメージできるものにしてください" \
" - 作成するプロンプトは英語の単語の羅列のみにしてください" \
" - 作成するプロンプトに改行や「:」「;」などの特殊文字も含まないでください" \
" - 返答する文章は、絶対に英語のみにし、その他の言語は絶対に含まないでください" \
" - プロンプトに関しての説明は含まないでください" \

# 日記文章生成関数
async def make_dialy_sentence(client, tasks: str, positive: bool) -> str:
	"""日記文章を生成する関数

	Args:
		client: httpxの非同期クライアント
		tasks (str): タスクのリストをフォーマットした文字列
		positive (bool): ポジティブな日記を生成するかどうか

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


# 日記用画像生成プロンプト生成関数
async def generate_dialy_prompt(client, text: str, max_retries=3):
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

        return format_to_allowed_chars(prompt)
        # if is_english_only(prompt):
            # return prompt
        # print(f"prompt:{prompt}")
        # poprint(f"非英語文字を検出。リトライ {attempt + 1}/{max_retries}")
        
    
    # 全てのリトライが失敗した場合、デフォルトの英語プロンプトを返す
    return "person standing nature simple photo"

# 英語のみの文字列にフォーマットする関数
def format_to_allowed_chars(text: str) -> str:
    """テキストを許可された文字のみに再構成する関数

    Args:
        text (str): 入力テキスト

    Returns:
        str: 許可された文字のみで構成されたテキスト
    """
    # 許可する文字のパターン
    allowed_pattern = re.compile(r'[^a-zA-Z0-9\s,\.\-]')
    # 許可されない文字を空文字に置換
    formatted_text = allowed_pattern.sub('', text)
    # 連続する空白を1つに置換
    formatted_text = ' '.join(formatted_text.split())
    return formatted_text

# 英語チェック関数
def is_english_only(text):
    # 英数字、スペース、カンマ、ピリオド、ハイフンのみを許可
    return bool(re.match('^[a-zA-Z0-9\s,\.\-]+$', text))

async def make_badge_name(client, tasks: str) -> str:
    """バッジの名前を生成する関数

    Args:
        name (str): バッジの名前

    Returns:
        str: 生成されたバッジの名前
    """
    load_dotenv()

    system_prompt = BADGE_SYSTEM_PROMPT_NAME

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

async def make_badge_sentence(client, tasks: str) -> str:
    """バッジの説明文を生成する関数

    Args:
        name (str): バッジの名前

    Returns:
        str: 生成されたバッジ文章
    """
    
    load_dotenv()

    system_prompt = BADGE_SYSTEM_PROMPT_TEXT

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


# バッジ用画像生成プロンプト生成関数
async def generate_badge_prompt(client, text: str, max_retries=3):
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
                        "content": BADGE_SYSTEM_PROMPT_IMAGE
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