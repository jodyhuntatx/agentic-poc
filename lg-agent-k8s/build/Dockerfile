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

# Disable virtual environment creation
RUN poetry config virtualenvs.create false --local

# Copy executable resources to container
COPY *.py pyproject.toml run-agent.sh set_api_keys.sh uid_entrypoint.sh /agent/

# Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# As root create a non-root user
USER root
ARG USERNAME=agent
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG USER_HOME_DIR=/agent

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN chown $USERNAME:$USER_GID -R $USER_HOME_DIR

WORKDIR /agent

# setup entrypoint for default user
RUN chmod g=u /etc/passwd /agent/*
ENTRYPOINT [ "/agent/uid_entrypoint.sh" ]

USER $USERNAME
RUN poetry update
