import uuid
import os

from config import INPUT_FOLDER, OUTPUT_FOLDER, FINAL_OUTPUT_FOLDER, 

def get_folder_path(file):
    request_id = str(uuid.uuid4())
    input_folder = INPUT_FOLDER + "/" + request_id
    os.makedirs(input_folder)
    output_folder = OUTPUT_FOLDER + "/" + request_id
    os.makedirs(output_folder)
    # 保存文件
    file_path = os.path.join(input_folder, file.filename)
    file.save(file_path)
    return request_id, input_folder, output_folder, file_path
