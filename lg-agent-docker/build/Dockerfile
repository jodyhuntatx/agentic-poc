FROM ubuntu:22.04

# install utilities
RUN apt-get update -y \
    && apt-get install -y \
    vim \
    ssh \
    curl \
    wget \
    unzip

RUN apt update -y \
    && apt install -y jq git

# install full python3 env
ENV PYTHONUNBUFFERED=1
RUN apt-get update -y             \
    && apt-get install -y python3 python3-pip \
    && ln -sf python3 /usr/bin/python
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y python3-venv
RUN pip3 install --no-cache --upgrade pip 		\
	setuptools requests keyring keyrings.alt poetry

WORKDIR /agent

# Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
