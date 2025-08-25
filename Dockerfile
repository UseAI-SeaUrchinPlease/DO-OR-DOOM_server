# Pythonベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    # Pillowの依存関係
    libpq-dev \
    python3-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをコピー
COPY . .

# EXPOSE命令を追加 (推奨)
# このコンテナが10000番ポートを使うことを明示的に宣言します
EXPOSE 10000

# FastAPI サーバー起動コマンドを修正
# Renderが提供する$PORT環境変数を読み込んで起動します
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
