# 如果报错需要更新版本 https://hub.docker.com/r/nvidia/cuda
FROM mobowuhan/oldphoto

WORKDIR /app/api_server

CMD ["python3", "app.py"]
