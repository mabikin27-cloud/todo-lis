# -*- coding: utf-8 -*-
"""
Todoリスト Webアプリのメイン入口です。

【初心者向け解説】
Flask は「URL と 関数」を対応させることで Web ページを表示します。
例: / にアクセス → index() が実行 → index.html が表示される
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash

# .env ファイルがあれば環境変数として読み込む（GOOGLE_SPREADSHEET_KEY 等）
from dotenv import load_dotenv
load_dotenv()

# 自分で作ったスプレッドシート連携モジュールを読み込む
import sheets_helper

app = Flask(__name__)
# メッセージを表示するために秘密鍵が必要（本番では環境変数から取得するのが望ましい）
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")


@app.route("/")
def index():
    """
    ［解説］トップページです。
    一覧ページにリダイレクトするだけなので、実質的には「一覧がトップ」になります。
    """
    return redirect(url_for("list_tasks"))


@app.route("/list")
def list_tasks():
    """
    ［解説］登録した「やること」を一覧表示するページです。
    sheets_helper.get_all_tasks() でスプレッドシートから全件取得し、
    list.html に渡して表示します。
    """
    try:
        tasks = sheets_helper.get_all_tasks()
    except Exception as e:
        flash(f"データの取得に失敗しました: {e}", "error")
        tasks = []
    return render_template("list.html", tasks=tasks)


@app.route("/add", methods=["GET", "POST"])
def add_task():
    """
    ［解説］新しい「やること」を登録するページです。
    GET  → 入力フォームを表示
    POST → フォームの内容をスプレッドシートに追加し、一覧へリダイレクト
    """
    if request.method == "GET":
        return render_template("form.html", task=None, title="やることを登録")

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    due_date = request.form.get("due_date", "").strip()

    if not title:
        flash("タイトルを入力してください。", "error")
        return render_template(
            "form.html",
            task={"title": title, "content": content, "due_date": due_date},
            title="やることを登録",
        )

    try:
        sheets_helper.add_task(title, content, due_date)
        flash("登録しました。", "success")
    except Exception as e:
        flash(f"登録に失敗しました: {e}", "error")
        return render_template(
            "form.html",
            task={"title": title, "content": content, "due_date": due_date},
            title="やることを登録",
        )
    return redirect(url_for("list_tasks"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    """
    ［解説］既存の「やること」を編集するページです。
    GET  → 現在の内容をフォームに表示
    POST → フォームの内容でスプレッドシートを更新し、一覧へリダイレクト
    """
    if request.method == "GET":
        try:
            task = sheets_helper.get_task(task_id)
        except Exception as e:
            flash(f"データの取得に失敗しました: {e}", "error")
            return redirect(url_for("list_tasks"))
        if task is None:
            flash("指定されたやることは見つかりません。", "error")
            return redirect(url_for("list_tasks"))
        return render_template("form.html", task=task, title="やることを編集")

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    due_date = request.form.get("due_date", "").strip()

    if not title:
        flash("タイトルを入力してください。", "error")
        return render_template(
            "form.html",
            task={"id": task_id, "title": title, "content": content, "due_date": due_date},
            title="やることを編集",
        )

    try:
        sheets_helper.update_task(task_id, title, content, due_date)
        flash("更新しました。", "success")
    except Exception as e:
        flash(f"更新に失敗しました: {e}", "error")
        return render_template(
            "form.html",
            task={"id": task_id, "title": title, "content": content, "due_date": due_date},
            title="やることを編集",
        )
    return redirect(url_for("list_tasks"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    """
    ［解説］「やること」を削除します。
    一覧ページの削除ボタンから POST で呼ばれ、処理後は一覧に戻ります。
    """
    try:
        sheets_helper.delete_task(task_id)
        flash("削除しました。", "success")
    except Exception as e:
        flash(f"削除に失敗しました: {e}", "error")
    return redirect(url_for("list_tasks"))


if __name__ == "__main__":
    # 開発時: ブラウザで http://127.0.0.1:5000 にアクセスすると表示されます
    # 本番サーバーでは gunicorn 等で app を起動してください
    app.run(host="0.0.0.0", port=5000, debug=True)
