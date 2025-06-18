from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

app = Flask(__name__)

# 🔑 サービスアカウント認証
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]
SERVICE_ACCOUNT_FILE = 'credentials.json'  # ← 適宜変更

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

gc = gspread.authorize(credentials)
drive_service = credentials.with_scopes(
    ['https://www.googleapis.com/auth/drive']
).with_subject(credentials.service_account_email)

from googleapiclient.discovery import build
drive = build('drive', 'v3', credentials=credentials)

# 📁 フォルダID（Google Drive内の日報フォルダ）
FOLDER_ID = "1BnHfbkccgmy_3jOOZlUhBCzz0m4wrnRe"  # ← 実際のフォルダIDに置き換えてください

def search_spreadsheet_by_student_id(student_id):
    """Google Driveでファイル名にstudent_idを含むスプレッドシートを検索"""
    query = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and name contains '{student_id}'"
    response = drive.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])
    if not files:
        return None
    return files[0]['id']  # 最初に見つかったもの

def extract_records(spreadsheet_id, start_date, end_date):
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet = spreadsheet.sheet1  # ✅ 最初のワークシートを取得

    start_dt = datetime.strptime(start_date, '%Y/%m/%d')
    end_dt = datetime.strptime(end_date, '%Y/%m/%d')

    filtered = []
    for row in sheet.get_all_records():
        try:
            date_str = str(row.get("レッスン日")).replace("-", "/")
            if start_date <= date_str <= end_date:
                content_parts = [
                    row.get("レッスン中の様子") or "",
                    row.get("成長した事・褒めてあげたい事") or "",
                    row.get("弱点・課題") or ""
                ]
                content = " / ".join([part for part in content_parts if part])
                filtered.append({"日付": date_str, "内容": content})
        except Exception:
            continue
    return filtered


@app.route("/get_report", methods=["POST"])
def get_report():
    data = request.get_json()
    student_id = data["student_id"]
    start_date = data["start_date"]
    end_date = data["end_date"]

    spreadsheet_id = search_spreadsheet_by_student_id(student_id)
    if not spreadsheet_id:
        return jsonify({"error": "該当するスプレッドシートが見つかりませんでした"}), 404

    records = extract_records(spreadsheet_id, start_date, end_date)

    return jsonify({
        "student_id": student_id,
        "期間": f"{start_date}〜{end_date}",
        "記録": records
    })



import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # デフォルト10000
    # app.run(host="0.0.0.0", port=port)

