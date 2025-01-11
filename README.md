"# flask_app_trip" 
旅行計画・管理アプリ

概要

このアプリは、旅行の計画や管理を効率的に行うために開発したWebアプリケーションです。月に1回旅行をする中で、LINEなどで旅行の予定を決めると情報が分散してしまい、管理が複雑になる課題を感じました。そのため、旅行に関する全ての情報を一元管理できるアプリを作成しました。

主な機能

・旅行計画作成

・目的地、出発日、旅のルートを入力して計画を作成。

・ホテル情報管理

・泊まるホテルのURLや予約情報を登録可能。

・予約確認書の管理

・PDFファイルをアップロードして予約情報を保存。

・旅行データの保存・管理

・SQLAlchemyを利用し、各旅行のデータを効率的に保存・管理。

使用技術

バックエンド: Flask

データベース: SQLAlchemy

フロントエンド: HTML, CSS


実行方法

このリポジトリをクローンします。

git clone https://github.com/Onzoro-rento/flask_app.git

ディレクトリに移動
cd flask_app

必要なパッケージをインストールします。

pip install -r requirements.txt

実行方法の例

```python app.py --option value```

Webブラウザで以下のURLにアクセスします。

http://127.0.0.1:5000

今後の課題・改善点

ユーザー認証機能の追加。

モバイル対応のUI改善。

外部APIを使用したホテル検索機能の実装。



