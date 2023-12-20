# 如果报错需要更新版本 https://hub.docker.com/r/nvidia/cuda
#FROM nvidia/cuda:12.3.1-base-ubuntu20.04
FROM registry-vpc.us-east-1.aliyuncs.com/moboaigc/oldphotomobo:tas

# 将代码复制到容器中
WORKDIR /app

# 首先只复制requirements.txt
COPY requirements.txt /app/

# 然后复制其余代码
COPY . /app/

# 启动服务
WORKDIR /app/api_server

CMD ["python3", "app.py"]
