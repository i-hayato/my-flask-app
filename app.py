from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return "Flask is working on Render!"

@app.route("/get_report", methods=["POST"])
def get_report():
    data = request.get_json()
    return jsonify({
        "student_id": data.get("student_id"),
        "期間": f"{data.get('start_date')}〜{data.get('end_date')}",
        "記録": [
            {"日付": "2024/05/01", "内容": "計算ドリル"},
            {"日付": "2024/05/02", "内容": "読解プリント"},
        ]
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)  # Renderではポート指定不要でもOK
