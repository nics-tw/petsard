# Multi-stage optimized build for development environment
# 多階段優化建置開發環境
FROM python:3.11-slim AS builder

ARG TARGETPLATFORM

# Install build dependencies
# 安裝建置依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	git \
	&& rm -rf /var/lib/apt/lists/* \
	&& python -m venv /opt/venv

# Set working directory and copy source
# 設定工作目錄並複製源碼
WORKDIR /app
COPY pyproject.toml README.md ./
COPY petsard/ ./petsard/
COPY demo/ ./demo/

# Create virtual environment
# 建立虛擬環境
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies based on build argument and platform
# 根據建置參數和平台安裝依賴
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN case ${TARGETPLATFORM} in \
	amd64) \
	pip install --no-cache-dir -e . && \
	pip install --no-cache-dir --dependency-groups=docker ;; \
	arm64) \
	echo "aarch64 detected - installing with CPU-only PyTorch..." && \
	pip install --no-cache-dir torch==2.7.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
	pip install --no-cache-dir -e . && \
	pip install --no-cache-dir --dependency-groups=docker ;;\
	esac

# Skip build-time testing for ARM64
# ARM64 平台跳過建置時測試
RUN case ${TARGETPLATFORM} in \
	arm64) \
	echo "ARM64 platform - skipping build-time tests" ;; \
	amd64) \
	python -c "import torch; print('✅ torch imported successfully')" && \
	python -c "import petsard; print('✅ petsard imported successfully')" ;; \
	esac


# Production stage
# 生產階段
FROM python:3.11-slim AS production

# Create user for security
# 為安全建立使用者
RUN groupadd -r petsard && useradd -r -g petsard -d /app petsard

# Set environment variables
# 設定環境變數
ENV PYTHONPATH=/app \
	PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PATH="/opt/venv/bin:$PATH" \
	TORCH_DISABLE_DISTRIBUTED=1 \
	OMP_NUM_THREADS=1 \
	HOME=/app \
	JUPYTER_CONFIG_DIR=/app/.jupyter \
	JUPYTER_DATA_DIR=/app/.local/share/jupyter

# Copy virtual environment and app files
# 複製虛擬環境和應用程式檔案
COPY --from=builder --chown=petsard:petsard /opt/venv /opt/venv
COPY --from=builder --chown=petsard:petsard /app /app

# Create necessary directories for Jupyter
# 為 Jupyter 創建必要的目錄
RUN mkdir -p /app/.local/share/jupyter /app/.jupyter && \
	chown -R petsard:petsard /app/.local /app/.jupyter

WORKDIR /app
USER petsard:petsard

EXPOSE 8888

# Create simple entrypoint script
# 創建簡單的入口腳本
COPY --chown=petsard:petsard <<EOF /app/entrypoint.py
#!/opt/venv/bin/python
import os
import sys
import subprocess
import platform

# ARM64/aarch64 optimization
if platform.machine() == 'aarch64':
    os.environ['TORCH_DISABLE_DISTRIBUTED'] = '1'
    os.environ['OMP_NUM_THREADS'] = '1'

RUN /opt/venv/bin/python -m jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token= --ServerApp.password= --ServerApp.allow_origin=* --ServerApp.allow_remote_access=True

try:
    subprocess.run(cmd, check=True)
except KeyboardInterrupt:
    sys.exit(0)
EOF

RUN chmod +x /app/entrypoint.py

ENTRYPOINT ["/opt/venv/bin/python", "/app/entrypoint.py"]

# Define build arguments for labels
# 定義用於標籤的建置參數
ARG BUILD_DATE
ARG VCS_REF

# Metadata labels
# 詮釋資料標籤
LABEL maintainer="matheme.justyn@gmail.com" \
	description="PETsARD Production Environment" \
	org.opencontainers.image.source="https://github.com/nics-tw/petsard" \
	org.opencontainers.image.documentation="https://nics-tw.github.io/petsard/" \
	org.opencontainers.image.licenses="MIT" \
	org.opencontainers.image.created=${BUILD_DATE} \
	org.opencontainers.image.revision=${VCS_REF} \
	org.opencontainers.image.title="PETsARD Development Environment" \
	org.opencontainers.image.description="Full development environment with Jupyter Lab, all dev tools, and PETsARD"
