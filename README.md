# Todoリスト Webアプリ（Python + Flask + Googleスプレッドシート）

やることを登録・編集でき、一覧で確認できるWebアプリです。  
データの保存には **Googleスプレッドシート** を使います。

---

## 機能

- **やることの登録** … タイトル・内容・期日を入力して保存
- **やることの編集** … 既存の項目を変更
- **一覧表示** … 登録したやることリストを一覧で確認
- **削除** … 不要な項目を削除

---

## 必要なもの

- **Python 3.8 以上**（`python3 --version` で確認）
- **Googleアカウント**（スプレッドシートとGoogle Cloud の設定用）

---

## 1. プロジェクトの準備

### 1-1. フォルダに移動

```bash
cd "/Users/masumi/Desktop/to doリスト"
```

### 1-2. 仮想環境の作成（推奨）

初めての方向けの解説：  
仮想環境を使うと、このプロジェクト専用のパッケージだけを入れられ、他のPythonプロジェクトに影響しません。

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
# Windows の場合は: venv\Scripts\activate
```

### 1-3. パッケージのインストール

```bash
pip install -r requirements.txt
```

---

## 2. Googleスプレッドシートの設定（重要）

データを保存するスプレッドシートと、プログラムからアクセスするための「認証」を用意します。

### 2-1. Google Cloud でプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセスし、Googleアカウントでログインします。
2. 画面上部の「プロジェクトを選択」→「新しいプロジェクト」をクリックし、名前（例：`todo-app`）を入力して作成します。

### 2-2. API を有効にする

1. 左メニュー「APIとサービス」→「ライブラリ」を開きます。
2. 「**Google Sheets API**」を検索して開き、「有効にする」をクリックします。
3. 同様に「**Google Drive API**」を検索して「有効にする」をクリックします。

### 2-3. サービスアカウント（認証用）の作成

1. 左メニュー「APIとサービス」→「認証情報」を開きます。
2. 「認証情報を作成」→「サービスアカウント」を選択します。
3. サービスアカウント名（例：`todo-app-sa`）を入力し、「作成して続行」→「完了」でOKです。
4. 作成したサービスアカウントの行をクリックし、「キー」タブ→「鍵を追加」→「新しい鍵を作成」→形式は「**JSON**」を選び「作成」します。JSONファイルがダウンロードされます。

### 2-4. 認証ファイルをプロジェクトに配置

1. ダウンロードしたJSONファイルの名前を **`credentials.json`** に変更します。
2. このプロジェクトのフォルダ（`to doリスト` の中）に **`credentials.json`** をコピーします。  
   → プロジェクト直下に `credentials.json` が存在する状態にしてください。

### 2-5. スプレッドシートを作成し、共有する

1. [Googleスプレッドシート](https://sheets.google.com/) で新しいスプレッドシートを作成します（名前は何でもOKです。例：「Todoリストデータ」）。
2. スプレッドシートのURLを開いた状態で、アドレスバーのURLを確認します。  
   例：`https://docs.google.com/spreadsheets/d/【ここがスプレッドシートのID】/edit`
3. **「ここがスプレッドシートのID」の部分**（長い英数字の文字列）をコピーします。後で環境変数に使います。
4. スプレッドシートの「共有」をクリックし、**共有相手**に `credentials.json` を開いて出てくる **`client_email`** の値（例：`xxx@xxx.iam.gserviceaccount.com`）を入力し、「編集者」で追加します。  
   → これでプログラムからスプレッドシートの読み書きができるようになります。

---

## 3. 環境変数の設定

プログラムが「どのスプレッドシートを使うか」を識別するために、**スプレッドシートのID** を設定します。

プロジェクトフォルダに **`.env`** ファイルが用意されています。  
その中の `GOOGLE_SPREADSHEET_KEY=` の右側に、コピーしたスプレッドシートのIDを貼り付けて保存してください。

```bash
# .env の例（「ここに…」の部分を実際のIDに書き換え）
GOOGLE_SPREADSHEET_KEY=1ABC123xyz...
SECRET_KEY=dev-secret-key-change-in-production
```

アプリ起動時に `.env` が自動で読み込まれるため、ターミナルで `export` する必要はありません。  
※ `.env` には秘密情報を書くため、Git にコミットしないでください（`.gitignore` に含まれています）。

---

## 4. アプリの起動

```bash
python3 app.py
```

ブラウザで次のURLを開きます。

- **http://127.0.0.1:5000** または **http://localhost:5000**

トップは「一覧」にリダイレクトされます。「新規登録」からやることを追加し、一覧・編集・削除を試してみてください。

---

## 5. サーバーで公開するには

「サーバーで公開する」とは、**いつでもインターネットからアクセスできるURL**（例：`https://my-todo-app.up.railway.app`）でアプリを動かすことです。  
ここでは**本番用の準備**と、**公開の代表的な3つの方法**を説明します。

---

### 5-1. 本番用の準備（共通）

サーバー上では、開発時と次の点を変えると安全で安定します。

| 項目 | 開発時 | 本番 |
|------|--------|------|
| 起動方法 | `python3 app.py` | **Gunicorn** で起動 |
| デバッグ | `debug=True` | オフ |
| 秘密鍵 | `.env` の適当な値 | **ランダムな長い文字列**（環境変数 `SECRET_KEY`） |
| 認証 | `credentials.json` ファイル | ファイル **または** 環境変数 `GOOGLE_CREDENTIALS_JSON` |

**Gunicorn** は、Flask アプリを本番向けに動かすためのサーバーです。  
`requirements.txt` に含まれているので、次のように起動できます。

```bash
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

- `-w 4` … ワーカー数
- `-b 0.0.0.0:5000` … 5000番ポートで受け付け
- `app:app` … `app.py` の Flask アプリを指定

---

### 5-2. 公開の方法を選ぶ

| 方法 | 難易度 | 特徴 | 無料枠 |
|------|--------|------|--------|
| **A. Railway** | ★☆☆ | Git push でデプロイ。設定が少ない | あり（クレジット制） |
| **B. Render** | ★★☆ | Railway と似た運用。無料だとスリープする | あり |
| **C. VPS** | ★★★ | 自分でサーバーを用意。自由度が高い | 各社による |

---

### 5-3. 方法A：Railway で公開（おすすめ）

[Railway](https://railway.app/) は、GitHub と連携して「push すると自動でデプロイ」できるサービスです。

1. **GitHub にプロジェクトを push**  
   新しいリポジトリを作成し、このプロジェクトを push。`credentials.json` と `.env` は push しない（`.gitignore` 済み）。

2. **Railway に登録**  
   https://railway.app/ で GitHub ログイン。

3. **New Project → Deploy from GitHub repo**  
   対象リポジトリを選択。

4. **環境変数を設定**  
   デプロイしたサービス → 「Variables」で次を追加。

   | 変数名 | 値 |
   |--------|-----|
   | `GOOGLE_SPREADSHEET_KEY` | スプレッドシートのID |
   | `SECRET_KEY` | 本番用ランダム文字列（例：`openssl rand -hex 32` で生成） |
   | `GOOGLE_CREDENTIALS_JSON` | `credentials.json` の**中身全体**をコピーして貼り付け |

5. **起動コマンド**  
   「Settings」→ Start Command に次を指定。  
   `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

6. **ドメイン発行**  
   「Settings」の「Networking」で「Generate Domain」を押すとURLが発行されます。

---

### 5-4. 方法B：Render で公開

[Render](https://render.com/) も Git 連携でデプロイできます。

1. GitHub に push（方法Aと同じ）。
2. Render で「New → Web Service」、リポジトリを選択。
3. **Build Command:** `pip install -r requirements.txt`  
   **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
4. 環境変数で `GOOGLE_SPREADSHEET_KEY`・`SECRET_KEY`・`GOOGLE_CREDENTIALS_JSON` を追加。
5. デプロイ後、`https://xxxx.onrender.com` のようなURLでアクセスできます。無料プランはスリープすることがあります。

---

### 5-5. 方法C：VPS で公開

さくら・ConoHa・AWS などのサーバーに、手動でアプリを置く方法です。

1. サーバーを用意し、SSH でログイン。
2. プロジェクトを clone またはアップロード。`credentials.json` を置くか、`GOOGLE_CREDENTIALS_JSON` を環境変数で設定。
3. `python3 -m venv venv && source venv/bin/activate` → `pip install -r requirements.txt`
4. 環境変数 `GOOGLE_SPREADSHEET_KEY`・`SECRET_KEY` を設定。
5. `gunicorn -w 4 -b 0.0.0.0:5000 app:app` で起動。常時動かす場合は systemd でサービス登録します。

---

### 5-6. まとめ

- 本番は **Gunicorn** で起動し、`GOOGLE_SPREADSHEET_KEY` と `SECRET_KEY` を必ず設定する。
- 認証は **`credentials.json`** をサーバーに置くか、環境変数 **`GOOGLE_CREDENTIALS_JSON`** に JSON 全体を入れる（Railway / Render では環境変数が便利）。
- まずは **Railway か Render** で「Git push → 環境変数設定 → URL で開く」まで試すのがおすすめです。

---

## 6. Render にデプロイする（手順）

このプロジェクトには **Render 用の設定**（`render.yaml`・`runtime.txt`）が入っています。

### ステップ1：GitHub に push

1. GitHub で新規リポジトリを作成（例：`todo-list`）。
2. プロジェクトフォルダで次を実行（`YOUR_USERNAME` / `YOUR_REPO` は自分のものに置き換え）。

```bash
cd "/Users/masumi/Desktop/to doリスト"
git init
git add .
git commit -m "Initial commit: Todo list app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

`.env` と `credentials.json` は `.gitignore` で push されません。

### ステップ2：Render で Web Service 作成

1. [Render](https://render.com/) で「Get Started」→ GitHub ログイン。
2. **New + → Web Service** をクリック。
3. 対象のリポジトリを選んで **Connect**。

### ステップ3：設定の確認

`render.yaml` があるため、多くの場合は自動で次のように入ります。

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

入っていなければ手動で上記を設定してください。

### ステップ4：環境変数を追加

**Environment** で「Add Environment Variable」を押し、次の3つを追加します。

| Key | Value |
|-----|--------|
| `GOOGLE_SPREADSHEET_KEY` | スプレッドシートのID |
| `SECRET_KEY` | 本番用のランダム文字列（`openssl rand -hex 32` で生成可） |
| `GOOGLE_CREDENTIALS_JSON` | `credentials.json` の**中身全体**をコピーして貼り付け |

### ステップ5：デプロイ

**「Create Web Service」** をクリック。ビルドが終わると「Your service is live at …」のURLでアプリにアクセスできます。

- 無料プランは一定時間使わないとスリープします。再度アクセスで起動しますが、数十秒かかることがあります。
- コードを変更したら `git push` すると自動で再デプロイされます。

---

## フォルダ構成（参考）

```
to doリスト/
├── app.py              # Webアプリの入口（Flask）
├── sheets_helper.py    # Googleスプレッドシート連携
├── requirements.txt    # パッケージ一覧
├── render.yaml         # Render 用設定（ビルド・起動コマンド）
├── runtime.txt         # Render 用 Python バージョン
├── credentials.json    # 自分で配置（Gitにコミットしないこと）
├── README.md           # このファイル
└── templates/
    ├── base.html       # 共通レイアウト
    ├── list.html       # 一覧ページ
    └── form.html       # 登録・編集フォーム
```

---

## トラブルシューティング

- **「認証ファイルが見つかりません」**  
  → `credentials.json` がプロジェクトフォルダの直下にあるか確認してください。

- **「GOOGLE_SPREADSHEET_KEY が設定されていません」**  
  → ターミナルで `export GOOGLE_SPREADSHEET_KEY="スプレッドシートのID"` を実行してから、再度 `python3 app.py` を実行してください。

- **スプレッドシートにアクセスできない / 404 のようなエラー**  
  → スプレッドシートの「共有」に、`credentials.json` の `client_email` を「編集者」で追加しているか確認してください。

- **ポート 5000 が使えない**  
  → `app.py` の最後の行を `app.run(host="0.0.0.0", port=5001, debug=True)` のように `port=5001` に変更すると、5001番で起動できます。

---

以上で、TodoリストWebアプリのセットアップは完了です。不明な点があれば、エラーメッセージとあわせて質問してください。
# todo-list
