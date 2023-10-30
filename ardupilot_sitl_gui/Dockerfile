FROM ubuntu:22.04

# Code fetch dependencies
RUN echo "UTC" > /etc/timezone && \
    apt-get update && apt-get install -y \
    git \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create a user
ARG USER=ardupilot
RUN adduser --disabled-password --gecos '' ${USER} && \
    adduser ${USER} sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Get a particular version of ArduPilot from GitHub
ARG ARDUPILOT_TAG=Copter-4.4.1
RUN git clone https://github.com/ArduPilot/ardupilot.git -b ${ARDUPILOT_TAG} --single-branch /ardupilot && \
    chown -R ${USER}:${USER} /ardupilot

# Set working directory
WORKDIR /ardupilot
# Switch to the default user
USER ${USER}

# Update submodules
RUN git submodule update --init --recursive

#------------------------------------------------------------------------------
# Build ArduPilot and SITL
#------------------------------------------------------------------------------

# Install build dependencies
USER root
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    lsb-release \
    tzdata \
    && rm -rf /var/lib/apt/lists/*
USER ${USER}

# Install all build prerequisites
ENV SKIP_AP_EXT_ENV=1 \
    # SKIP_AP_GRAPHIC_ENV=1 \
    SKIP_AP_COV_ENV=1 \
    SKIP_AP_GIT_CHECK=1
RUN USER=${USER} Tools/environment_install/install-prereqs-ubuntu.sh -y

# Build according to https://github.com/ArduPilot/ardupilot/blob/master/BUILD.md
RUN ./waf distclean
RUN ./waf configure --board sitl
RUN ./waf copter
RUN ./waf rover
RUN ./waf plane
RUN ./waf sub

#------------------------------------------------------------------------------
# Package SITL
#------------------------------------------------------------------------------

# Install execution dependencies
USER root
RUN apt-get update && apt-get install -y \
    socat \
    ncat \
    && rm -rf /var/lib/apt/lists/*
USER ${USER}

# Allow UDP broadcasting
RUN sudo sysctl net.ipv4.icmp_echo_ignore_broadcasts=0


# Default communication channel
# EXPOSE 5760/tcp

WORKDIR /home/${USER}

# install display
USER root
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    xvfb \
    xterm \
    x11-xserver-utils \
    x11vnc 

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
# RUN export PATH="$PATH:$HOME/.local/bin

USER root
RUN usermod -a -G dialout ${USER}
USER ${USER}

ENV DISPLAY=:1
# x11vnc
# EXPOSE 5900/tcp

# CMD ["bash", \
#     "-c", \
#     "(sudo Xvfb :1 -screen 0 1280x720x16 & sudo x11vnc -display :1 -rfbport 5900 -forever -loop -xkb -noxdamage -repeat -shared &) | /ardupilot/Tools/autotest/sim_vehicle.py -v ArduCopter --no-mavproxy --sim-address=$(hostname -i) --osd"]

CMD ["bash", "-c", "SITL_RITW_TERMINAL=bash /ardupilot/Tools/autotest/sim_vehicle.py -v ArduCopter --no-mavproxy --sim-address=$(hostname -i)"]

# docker build . -t test_sitl_gui
# docker run --rm -p 5900:5900 -it test_sitl_gui
# docker run --rm -it test_sitl_gui bash -c ".local/bin/mavproxy.py  --out 172.17.0.3:14551 --master tcp:$(hostname -i):5760 --sitl $(hostname -i):5501"
# docker run --rm -it test_sitl_gui bash -c "(SITL_RITW_TERMINAL=bash /ardupilot/Tools/autotest/sim_vehicle.py -v ArduCopter --no-mavproxy --sim-address=$(hostname -i) &) | .local/bin/mavproxy.py  --out 172.17.0.3:14551 --master tcp:$(hostname -i):5760 --sitl $(hostname -i):5501"