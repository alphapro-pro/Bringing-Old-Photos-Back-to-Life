from flask import Flask, request, send_from_directory

import os
import threading

from config import API_URL, OUTPUT_FOLDER
from views.image_process import process_image
from utils import get_folder_paths, save_file, require_api_key

app = Flask(__name__)


@app.route("/new_task", methods=["POST"])
@require_api_key
def new_task():
    if "file" not in request.files:
        return {"error": "No file part"}, 400
    files = request.files.getlist("file")

    if not files or all(file.filename == "" for file in files):
        return {"error": "No selected file"}, 400

    request_id, input_folder, output_folder = get_folder_paths()

    for file in files:
        file_path = save_file(file, input_folder)

    opts = {
        "input_folder": input_folder,
        "output_folder": output_folder,
        "GPU": "0",
        "checkpoint_name": "Setting_9_epoch_100",
        "with_scratch": False,
        "HR": False,
    }

    thread = threading.Thread(target=process_image, args=(request_id, file_path, opts))
    thread.start()
    return {"requestId": request_id}


@app.route("/status/<request_id>", methods=["GET"])
@require_api_key
def get_status(request_id):
    output_folder_path = os.path.join(OUTPUT_FOLDER, request_id, "final_output")

    if os.path.exists(output_folder_path) and os.path.isdir(output_folder_path):
        image_files = [
            f
            for f in os.listdir(output_folder_path)
            if os.path.isfile(os.path.join(output_folder_path, f))
        ]

        if image_files:
            status = "COMPLETED"
            image_urls = [
                f"{API_URL}/images/{request_id}/final_output/{image_file}"
                for image_file in image_files
            ]
            response = {
                "requestId": request_id,
                "status": status,
                "imageUrls": image_urls,
            }
        else:
            status = "PROCESSING"
            response = {"requestId": request_id, "status": status}
    else:
        return {"error": "输出目录不存在"}, 404

    return response


@app.route("/images/<request_id>/<image_name>", methods=["GET"])
def get_image(request_id, image_name):
    # 构建完整的文件路径
    full_path = os.path.join(OUTPUT_FOLDER, request_id, "final_output", image_name)
    # 发送文件
    return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))


# 任务重试
@app.route("/retry", methods=["GET"])
@require_api_key
def retry_task():
    pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
