import uuid
import os
from flask import request, jsonify
from functools import wraps
from config import INPUT_FOLDER, OUTPUT_FOLDER


def get_folder_paths():
    request_id = str(uuid.uuid4())
    input_folder = os.path.join(INPUT_FOLDER, request_id)
    os.makedirs(input_folder, exist_ok=True)
    output_folder = os.path.join(OUTPUT_FOLDER, request_id)
    os.makedirs(output_folder, exist_ok=True)
    return request_id, input_folder, output_folder


def save_file(file, input_folder):
    file_path = os.path.join(input_folder, file.filename)
    file.save(file_path)
    return file_path


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if api_key != "1888":
            return jsonify({"error": "Invalid API key"}), 403
        return f(*args, **kwargs)

    return decorated_function
