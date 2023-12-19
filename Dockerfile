# 如果报错需要更新版本 https://hub.docker.com/r/nvidia/cuda
FROM nvidia/cuda:12.3.1-base-ubuntu20.04
# FROM nvidia/cuda:11.1-base-ubuntu20.04

# RUN apt-get update && apt-get install -y python3 python3-pip
# 准备ubuntu环境
# RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 54404762BBB6E853 && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BDE6D2B9216EC7A8
RUN apt update && apt install git bzip2 wget unzip python3-pip python3-dev cmake libgl1-mesa-dev python-is-python3 libgtk2.0-dev -yq

# 将代码复制到容器中
ADD . /app
WORKDIR /app

# 准备模型
RUN cd Face_Enhancement/models/networks/ &&\
  git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch &&\
  cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm . &&\
  cd ../../../

RUN cd Global/detection_models &&\
  git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch &&\
  cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm . &&\
  cd ../../

RUN cd Face_Detection/ &&\
  wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 &&\
  bzip2 -d shape_predictor_68_face_landmarks.dat.bz2 &&\
  cd ../ 

RUN cd Face_Enhancement/ &&\
  wget https://facevc.blob.core.windows.net/zhanbo/old_photo/pretrain/Face_Enhancement/checkpoints.zip &&\
  unzip checkpoints.zip &&\
  cd ../ &&\
  cd Global/ &&\
  wget https://facevc.blob.core.windows.net/zhanbo/old_photo/pretrain/Global/checkpoints.zip &&\
  unzip checkpoints.zip &&\
  rm -f checkpoints.zip &&\
  cd ../

# 安装Python依赖1
RUN pip3 install -r requirements.txt

# 切换到api_server目录
WORKDIR /app/api_server

# 设置启动命令
CMD ["python3", "app.py"]
