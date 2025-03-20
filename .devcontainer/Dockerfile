FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

RUN curl --proto '=https' --tlsv1.2 -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt update -y && \
    apt install -y --no-install-recommends curl gnupg2 jq less nano nodejs procps psmisc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
