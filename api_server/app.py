from flask import Flask, request, send_from_directory
from flask_cors import CORS
import os
import threading

from config import API_URL, OUTPUT_FOLDER, INPUT_FOLDER
from views.image_process import process_image
from utils import get_folder_paths, save_file, require_api_key

app = Flask(__name__)
CORS(app)


@app.route("/new", methods=["POST"])
@require_api_key
def new_task():
    if "file" not in request.files:
        return {"error": "No file part"}, 400
    files = request.files.getlist("file")

    if not files or all(file.filename == "" for file in files):
        return {"error": "No selected file"}, 400

    # 是否修复划痕，默认false
    with_scratch = request.args.get("with_scratch", "false").lower() == "true"

    request_id, input_folder, output_folder = get_folder_paths()

    for file in files:
        save_file(file, input_folder)

    opts = {
        "input_folder": input_folder,
        "output_folder": output_folder,
        "GPU": "0",
        "checkpoint_name": "Setting_9_epoch_100",
        "with_scratch": with_scratch,
        # 是否属于高像素模糊图片
        "HR": False,
    }

    thread = threading.Thread(target=process_image, args=(opts,))
    thread.start()
    return {"requestId": request_id}, 200


@app.route("/status/<request_id>", methods=["GET"])
@require_api_key
def task_status(request_id):
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
                f"{API_URL}/images/{request_id}/{image_file}"
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
        status = "PROCESSING"
        response = {"requestId": request_id, "status": status}

    return response, 200


@app.route("/retry/<request_id>", methods=["GET"])
@require_api_key
def retry_task(request_id):
    if not request_id:
        return {"error": "缺少requestid参数"}, 400
    try:
        # 拼接文件夹路径
        input_folder = os.path.join(INPUT_FOLDER, request_id)
        output_folder = os.path.join(OUTPUT_FOLDER, request_id, "final_output")

        # 确保文件夹存在
        if not os.path.exists(input_folder) or not os.path.exists(output_folder):
            return {"error": "找不到相应的文件夹"}, 404

        input_files = set(os.listdir(input_folder))
        output_files = set(os.listdir(output_folder))

        # 检查是否需要重试
        to_retry_files = [f for f in input_files if f not in output_files]

        if not to_retry_files:
            return {"message": "所有图片已成功生成，无需重试"}, 202

        # 重启任务
        opts = {
            "input_folder": input_folder,
            "output_folder": output_folder,
            "GPU": "0",
            "checkpoint_name": "Setting_9_epoch_100",
            "with_scratch": False,
            "HR": False,
        }

        # 重新启动处理流程
        thread = threading.Thread(target=process_image, args=(opts))
        thread.start()

        return {"requestId": request_id}, 200

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/images/<request_id>/<image_name>", methods=["GET"])
def get_image(request_id, image_name):
    # 构建完整的文件路径
    full_path = os.path.join(OUTPUT_FOLDER, request_id, "final_output", image_name)
    # 返回文件
    return (
        send_from_directory(os.path.dirname(full_path), os.path.basename(full_path)),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
