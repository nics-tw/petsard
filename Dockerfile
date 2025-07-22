FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime

WORKDIR /app
COPY pyproject.toml ./
COPY README.md ./
COPY petsard/ ./petsard/
COPY demo/ ./demo/

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir --group jupyter

# Create user for security
RUN groupadd -r petsard && useradd -r -g petsard -d /app petsard

ENV JUPYTER_CONFIG_DIR=/app/.jupyter JUPYTER_DATA_DIR=/app/.local/share/jupyter

# Create necessary directories for Jupyter
# 為 Jupyter 創建必要的目錄
RUN mkdir -p /app/.local/share/jupyter /app/.jupyter && chown -R petsard:petsard /app/.local /app/.jupyter

WORKDIR /app
USER petsard:petsard

EXPOSE 8888

# Create simple entrypoint script
# 創建簡單的入口腳本
COPY --chown=petsard:petsard <<EOF /app/entrypoint.py
import os
import sys
import subprocess

cmd = [
        'python', '-m', 'jupyter', 'lab',
        '--ip=0.0.0.0',
        '--port=8888',
        '--no-browser',
        '--allow-root',
        '--ServerApp.token=',
        '--ServerApp.password=',
        '--ServerApp.allow_origin=*',
        '--ServerApp.allow_remote_access=True'
    ]

try:
    subprocess.run(cmd, check=True)
except KeyboardInterrupt:
    sys.exit(0)
EOF

RUN chmod +x /app/entrypoint.py

ENTRYPOINT ["python", "/app/entrypoint.py"]

# Define build arguments for labels
ARG BUILD_DATE
ARG VCS_REF

# Metadata labels
LABEL maintainer="matheme.justyn@gmail.com" \
	description="PETsARD Production Environment" \
	org.opencontainers.image.source="https://github.com/nics-tw/petsard" \
	org.opencontainers.image.documentation="https://nics-tw.github.io/petsard/" \
	org.opencontainers.image.licenses="MIT" \
	org.opencontainers.image.created=${BUILD_DATE} \
	org.opencontainers.image.revision=${VCS_REF} \
	org.opencontainers.image.title="PETsARD Development Environment" \
	org.opencontainers.image.description="Full development environment with Jupyter Lab, all dev tools, and PETsARD"
