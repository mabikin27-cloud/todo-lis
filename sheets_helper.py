# -*- coding: utf-8 -*-
"""
Googleスプレッドシートとの連携を担当するモジュールです。

【初心者向け解説】
このファイルは「データの出し入れ」を専門に担当します。
- やることの一覧をスプレッドシートから取得
- 新規登録・編集・削除をスプレッドシートに反映
"""

import os
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None

# スプレッドシートで使うAPIの範囲（スプレッドシートとGoogleドライブの両方に必要）
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# 1行目はヘッダー（タイトル・内容・期日）
HEADER_ROW = ["タイトル", "内容", "期日", "作成日時"]


def _get_client():
    """
    ［解説］認証情報を使ってGoogleスプレッドシートに接続し、クライアントを返します。
    認証は (1) 環境変数 GOOGLE_CREDENTIALS_JSON のJSON文字列、または
    (2) プロジェクト内の credentials.json ファイルの順で参照します。
    """
    if gspread is None:
        raise RuntimeError(
            "gspread がインストールされていません。"
            " pip install -r requirements.txt を実行してください。"
        )

    import json

    # 本番サーバー向け: 環境変数にJSON文字列が入っていればそれを使う
    cred_json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON", "").strip()
    if cred_json_str:
        try:
            info = json.loads(cred_json_str)
            creds = Credentials.from_service_account_info(info, scopes=SCOPES)
            return gspread.authorize(creds)
        except (json.JSONDecodeError, Exception) as e:
            raise RuntimeError(f"GOOGLE_CREDENTIALS_JSON の内容が正しくありません: {e}")

    # ローカル・VPS向け: ファイルから読み込む
    cred_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "credentials.json"
    )
    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"認証ファイルが見つかりません: {cred_path}\n"
            "Google Cloud でサービスアカウントを作成し、"
            "ダウンロードしたJSONを credentials.json として保存するか、"
            "環境変数 GOOGLE_CREDENTIALS_JSON にJSON文字列を設定してください。"
        )

    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return gspread.authorize(creds)


def _get_sheet():
    """
    ［解説］環境変数 GOOGLE_SPREADSHEET_KEY に設定したスプレッドシートの
    最初のシートを取得します。未設定の場合はエラーにします。
    """
    key = os.environ.get("GOOGLE_SPREADSHEET_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "環境変数 GOOGLE_SPREADSHEET_KEY が設定されていません。\n"
            "スプレッドシートのURLの「/d/」と「/edit」の間の文字列を設定してください。"
        )
    gc = _get_client()
    workbook = gc.open_by_key(key)
    sheet = workbook.sheet1  # 最初のシートを使用
    return sheet


def _ensure_header(sheet):
    """
    ［解説］シートの1行目がヘッダーでない場合、ヘッダーを書き込みます。
    """
    row1 = sheet.row_values(1)
    if row1 != HEADER_ROW:
        sheet.update("A1:D1", [HEADER_ROW])


def get_all_tasks():
    """
    ［解説］スプレッドシートから「やること」をすべて取得し、リストで返します。
    各要素は id（行番号）, タイトル, 内容, 期日 を持つ辞書です。
    """
    sheet = _get_sheet()
    _ensure_header(sheet)
    records = sheet.get_all_records()
    result = []
    for i, row in enumerate(records, start=2):  # 2行目からがデータ
        result.append({
            "id": i,
            "title": row.get("タイトル", ""),
            "content": row.get("内容", ""),
            "due_date": row.get("期日", ""),
        })
    return result


def get_task(row_id):
    """
    ［解説］指定した行番号の「やること」を1件取得します。
    """
    sheet = _get_sheet()
    _ensure_header(sheet)
    row = sheet.row_values(int(row_id))
    if len(row) < 3:
        return None
    return {
        "id": int(row_id),
        "title": row[0] if len(row) > 0 else "",
        "content": row[1] if len(row) > 1 else "",
        "due_date": row[2] if len(row) > 2 else "",
    }


def add_task(title, content, due_date):
    """
    ［解説］新しい「やること」を1行追加します。
    """
    sheet = _get_sheet()
    _ensure_header(sheet)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = [str(title).strip(), str(content).strip(), str(due_date).strip(), now]
    sheet.append_row(row, value_input_option="USER_ENTERED")
    # 追加した行番号は「現在の行数」
    return sheet.row_count


def update_task(row_id, title, content, due_date):
    """
    ［解説］指定した行の「やること」を更新します。
    """
    sheet = _get_sheet()
    _ensure_header(sheet)
    row_idx = int(row_id)
    row = [str(title).strip(), str(content).strip(), str(due_date).strip()]
    sheet.update(f"A{row_idx}:C{row_idx}", [row], value_input_option="USER_ENTERED")


def delete_task(row_id):
    """
    ［解説］指定した行の「やること」を削除します。
    """
    sheet = _get_sheet()
    sheet.delete_rows(int(row_id))
