#!/bin/bash

#docker build -f Dockerfile.arm64 --build-arg  --pull --no-cache -t desktop_ubuntu:latest .
#docker build -f Dockerfile.arm64 -t desktop_ubuntu:latest .

#cp -R /opt/data/shm/account91 shm/account91
#cp -R /opt/data/shm/script/ shm/script

docker build --platform=linux/amd64  -f Dockerfile.dependent  --build-arg  --pull --no-cache  -t compass-vnc-server:latest .
docker push whereisyap/compass-vnc-server:latest

#
#  1 导出image文件
#  docker save scrapyd > scrapyd.tar
#  2 文件上传到服务器上
#  3 服务器上运行导入镜像
#  docker load < scrapyd.tar
#  4 启动运行容器
#  docker run -d -p 6800:6800 scrapyd:latest