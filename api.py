# Biến toàn cục lưu các client đang chờ
from flask import Flask, request, jsonify
import threading
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
pending_clients = {}

@app.route("/wait_for_image", methods=["GET"])
def wait_for_image():
    client_id = request.args.get("client_id")
    if not client_id:
        return {"error": "Missing client_id"}, 400

    # Tạo event cho client này
    event = threading.Event()
    pending_clients[client_id] = {"event": event, "image": None}

    # Chờ tối đa 30 giây
    event.wait(timeout=60)

    # Sau khi chụp xong, trả về ảnh
    result = pending_clients.pop(client_id, None)
    if result and result["image"]:
        return jsonify({"status": "received", "image_data": result["image"]})
    else:
        return jsonify({"status": "timeout"})

@app.route("/upload_from_phone", methods=["POST"])
def upload_from_phone():
    client_id = request.form.get("client_id")
    file = request.files.get("file")

    if not client_id or not file:
        return {"error": "Missing data"}, 400

    # Lưu file vào bộ nhớ hoặc ổ cứng
    img_data = file.read()
    img_base64 = base64.b64encode(img_data).decode("utf-8")

    # Thông báo cho client đang chờ
    if client_id in pending_clients:
        pending_clients[client_id]["image"] = img_base64
        pending_clients[client_id]["event"].set()

    return {"status": "uploaded"}


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)