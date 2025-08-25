## backend の 準備

 - docker desktopをインストールしておく

 - backends/.env.sample を「.env」へ名前を変更
 - 中身の「CHAT_AI_API_KEY」に自身のAPIキーを設定する

## docker image のビルド
 - まず、docker desktop が起動していることを確認する
    - 起動していなければ起動する
    - 動作確認として、「docker --version」でバージョンが出るか確認
 - /backends へ移動
 - 「docker build -t ai-backend」を実行
 - これで、docker desktop の images に「ai-backend」があればOK

## docker container の作成＆初回起動・終了
 - まず、docker desktop が起動していることを確認する
    - 起動していなければ起動する
    - 動作確認として、「docker --version」でバージョンが出るか確認
 - 「docker run -d --name ai-container --env-file .env -p 8000:8000 ai-backend」
 - これで、「localhost:8000」が開く
 - 終了したいときは「docker stop ai-container」

## docker container の2回目以降の起動・終了
 - まず、docker desktop が起動していることを確認する
    - 起動していなければ起動する
    - 動作確認として、「docker --version」でバージョンが出るか確認
 - ２回目以降の起動の際は、変更がなければ「docker start ai-container」
    - 変更があれば、一度「docker rm -f ai-container」で一度コンテナを消す
    - その後、初回起動時と同じようにもう一度ビルドからやり直す
 - 終了は、「docker stop ai-container」
