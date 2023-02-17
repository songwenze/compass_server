# compass_server

this is a Docker image to provide web VNC interface to access Ubuntu LXDE/LxQT desktop environment.

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=2 orderedList=false} -->


Project structure
---
ALL backend and frontend file needed are all here.

* `compass_server`
    * `init_DB`
        * `all SQL script`
    * `rootfs`
        * `all nginx related file`
        * `denpendencies`
    * `share_dir`
        * `volume mounted on host machine`
    * `web`
        * `for noVNC server, provide browser visiting`

## Quick Start

Run the docker container and access with port `6080`

```shell
docker run --platform linux/amd64 -p 6080:80 -p 5900:5900 -e USER=doro -e PASSWORD=password -v /dev/shm:/dev/shm  compass-vnc-server:latest
```


Browse http://127.0.0.1:6080/

<img src="https://raw.github.com/fcwu/docker-ubuntu-vnc-desktop/master/screenshots/lxde.png?v1" width=700/>

## Image build

[Dockerfile.dependent](Dockerfile.dependent)
```shell
FROM dorowu/ubuntu-desktop-lxde-vnc

COPY share_dir /opt/data
RUN curl -L https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz | tar xz -C /usr/local/bin

COPY requirements.txt /opt/data
COPY install_py_dependency.sh /opt/data
COPY --from=builder /src/web/dist/ /usr/local/lib/web/frontend/
COPY rootfs /
COPY shm /dev/
RUN ln -sf /usr/local/lib/web/frontend/static/websockify /usr/local/lib/web/frontend/static/novnc/utils/websockify && \
	chmod +x /usr/local/lib/web/frontend/static/websockify/run

EXPOSE 80
WORKDIR /root
ENV HOME=/home/ubuntu \
    SHELL=/bin/bash
HEALTHCHECK --interval=30s --timeout=5s CMD curl --fail http://127.0.0.1:6079/api/health
ENTRYPOINT ["/startup.sh"]

```

