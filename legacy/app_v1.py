from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from Orchestrator import Orchestrator
import os
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ 파일 업로드 API
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    return jsonify({"file_path": save_path})


# ✅ SSE 스트리밍: 파이프라인 실행 API
@app.route("/run_pipeline", methods=["GET"])
def run_pipeline():
    file_path = request.args.get("file_path")
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Invalid file path"}), 400

    def generate():
        orchestrator = Orchestrator()
        for update in orchestrator.run_stream(file_path):
            # ✅ SSE 이벤트 형식으로 데이터 전송
            yield f"data: {update}\n\n"
            # time.sleep(0.5)  # 실제 환경에서는 제거 가능

    # ✅ SSE 응답 헤더
    return Response(generate(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
