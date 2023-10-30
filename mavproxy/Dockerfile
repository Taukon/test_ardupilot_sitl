FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

# Code fetch dependencies
RUN echo "UTC" > /etc/timezone && \
    apt-get update && apt-get install -y \
    git \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create a user
ARG USER=mavproxy
RUN adduser --disabled-password --gecos '' ${USER} && \
    adduser ${USER} sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set working directory
WORKDIR /home/${USER}
# Switch to the default user
USER ${USER}

# install display
USER root
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    xvfb \
    xterm \
    x11-xserver-utils \
    x11vnc 

ENV DISPLAY=:1

# install mavproxy
USER root
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3-dev \
        python3-opencv \
        python3-wxgtk4.0 \
        python3-pip \
        python3-matplotlib \
        python3-lxml \
        python3-pygame

USER ${USER}
RUN pip3 install PyYAML mavproxy --user
RUN echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc

USER root
RUN usermod -a -G dialout ${USER}
USER ${USER}

CMD ["bash"]


# docker build . -t test_mavproxy
# docker run --rm  -it test_mavproxy bash
# mavproxy.py --out 127.0.0.1:14551 --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501
# DISPLAY=:1 .local/bin/mavproxy.py --out $(hostname -i):14550 --out $(hostname -i):14551 --master tcp:172.17.0.3:5760 --sitl 172.17.0.3:5501 --map

# CLI
# docker run --rm -it test_mavproxy bash -c ".local/bin/mavproxy.py  --out 172.17.0.3:14551 --master tcp:172.17.0.2:5760 --sitl 172.17.0.2:5501"

#GUI
# docker run --rm -p 5900:5900 -it test_mavproxy bash -c "(sudo Xvfb :1 -screen 0 1280x720x16 & sudo x11vnc -display :1 -rfbport 5900 -forever -loop -xkb -noxdamage -repeat -shared &) | .local/bin/mavproxy.py  --out 172.17.0.3:14551 --master tcp:172.17.0.2:5760 --sitl 172.17.0.2:5501 --map"
