# Multi-stage build for smaller final image
# 多階段建置以減少最終映像檔大小
FROM python:3.12-slim AS builder

# Install build dependencies
# 安裝建置依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
# 安裝 uv 以加速依賴管理
RUN pip install --no-cache-dir uv

# Set working directory
# 設定工作目錄
WORKDIR /app

# Copy dependency files first for better layer caching
# 先複製依賴檔案以優化層快取
COPY pyproject.toml uv.lock requirements.txt ./

# Create and activate virtual environment
# 建立並啟用虛擬環境
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with better error handling
# 安裝 Python 依賴，包含錯誤處理機制
RUN uv pip install -r requirements.txt \
    || (echo "uv install failed, falling back to pip" && pip install --no-cache-dir -r requirements.txt --timeout 300 --retries 3)

# Copy source code
# 複製原始碼
COPY petsard/ ./petsard/
COPY demo/ ./demo/
COPY templates/ ./templates/
COPY README.md LICENSE CHANGELOG.md ./

# Install PETsARD package in development mode
# 以開發模式安裝 PETsARD 套件
RUN uv pip install -e . || pip install --no-cache-dir -e .

# Production stage
# 生產階段
FROM python:3.12-slim AS production

# Install minimal runtime dependencies only
# 僅安裝最小運行時依賴
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set environment variables for Python optimization
# 設定 Python 優化環境變數
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user with specific UID for security
# 建立特定 UID 的非 root 使用者以提升安全性
RUN useradd --create-home --shell /bin/bash --uid 1000 petsard

# Copy virtual environment from builder stage
# 從建置階段複製虛擬環境
COPY --from=builder /opt/venv /opt/venv

# Set working directory
# 設定工作目錄
WORKDIR /app

# Copy application files from builder stage
# 從建置階段複製應用程式檔案
COPY --from=builder /app /app

# Change ownership to non-root user
# 將擁有權變更為非 root 使用者
RUN chown -R petsard:petsard /app /opt/venv

# Switch to non-root user for security
# 切換到非 root 使用者以提升安全性
USER petsard

# Add health check with meaningful test
# 新增有意義的健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import petsard; from importlib.metadata import version; print(f'PETsARD v{version(\"petsard\")} OK')" || exit 1

# Set default command to show PETsARD information
# 設定預設指令以顯示 PETsARD 資訊
CMD ["python", "-c", "import petsard; from importlib.metadata import version; print(f'🎉 PETsARD v{version(\"petsard\")} is ready to use!')"]

# Metadata labels for container registry
# 容器註冊表的元資料標籤
ARG BUILD_DATE
ARG VCS_REF
LABEL maintainer="alexchen830@gmail.com, matheme.justyn@gmail.com" \
      description="PETsARD - Privacy Enhancing Technologies Analysis, Research, and Development" \
      org.opencontainers.image.source="https://github.com/nics-tw/petsard" \
      org.opencontainers.image.documentation="https://nics-tw.github.io/petsard/" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}"