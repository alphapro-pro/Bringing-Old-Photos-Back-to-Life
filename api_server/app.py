from flask import Flask, request, send_from_directory

import os
import threading

from config import API_URL
from views.image_process import process_image
from config import request_status
from utils import get_folder_path

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"error": "No file part"}, 400
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    if file:
        # 生成唯一的请求ID、并且准备模型的参数
        request_id, input_folder, output_folder, file_path = get_folder_path(file)
        # 新开线程 异步处理图片和参数
        opts = {
            "input_folder": input_folder,
            "output_folder": output_folder,
            "GPU": "0",
            # 默认值
            "checkpoint_name": "Setting_9_epoch_100",
            # 默认值
            "with_scratch": False,
            "HR": False,
        }
        # 返回请求ID
        request_status[request_id] = {"file_path": file_path, "status": "UPLOADED"}
        thread = threading.Thread(
            target=process_image, args=(request_id, file_path, opts)
        )
        thread.start()
        return {"requestId": request_id}


@app.route("/status/<request_id>", methods=["GET"])
def get_status(request_id):
    try:
        request_id_obj = request_status[request_id]
    except:
        return "数据有误", 400

    status = request_id_obj["status"]
    response = {"requestId": request_id, "status": status}
    # 如果处理完成，添加图片URL
    if status == "COMPLETED":
        response["imageUrl"] = f"{API_URL}/images/{request_id}"

    return response


@app.route("/images/<request_id>", methods=["GET"])
def get_image(request_id):
    try:
        request_info = request_status[request_id]
        file_path = request_info["file_path"]
    except KeyError:
        return "数据有误", 400

    directory, filename = os.path.split(file_path)
    return send_from_directory(directory, filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
