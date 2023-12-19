# 用户图像和输出图像
INPUT_FOLDER = "/mnt/input"
OUTPUT_FOLDER = "/mnt/output"
FINAL_OUTPUT_FOLDER = OUTPUT_FOLDER + "/final_output"
API_URL = "http://172.18.2.190:5000"

# 存储请求状态的字典（后期转数据库）目前单线程的话应该不会被杀死
request_status = {}
