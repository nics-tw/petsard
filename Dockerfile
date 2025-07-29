# syntax=docker/dockerfile:1
# check=error=true

FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime

WORKDIR /app
COPY pyproject.toml ./
COPY README.md ./
COPY petsard/ ./petsard/
COPY demo/ ./demo/
COPY entrypoint.sh ./

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir --group jupyter


# Create necessary directories for Jupyter
# 為 Jupyter 創建必要的目錄
ENV JUPYTER_CONFIG_DIR=/app/.jupyter JUPYTER_DATA_DIR=/app/.local/share/jupyter
RUN mkdir -p /app/.local/share/jupyter /app/.jupyter

EXPOSE 8888

# Define build arguments for labels
ARG BUILD_DATE
ARG VCS_REF

# Metadata labels
LABEL maintainer="matheme.justyn@gmail.com" \
	description="PETsARD Production Environment" \
	com.nvidia.volumes.needed="nvidia_driver" \
	org.opencontainers.image.source="https://github.com/nics-tw/petsard" \
	org.opencontainers.image.documentation="https://nics-tw.github.io/petsard/" \
	org.opencontainers.image.licenses="MIT" \
	org.opencontainers.image.created=${BUILD_DATE} \
	org.opencontainers.image.revision=${VCS_REF} \
	org.opencontainers.image.title="PETsARD Development Environment" \
	org.opencontainers.image.description="Full development environment with Jupyter Lab, all dev tools, and PETsARD"
