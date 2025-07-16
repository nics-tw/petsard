---
title: Docker 開發
type: docs
weight: 89
prev: docs/developer-guide/test-coverage
next: docs/developer-guide
---

本指南涵蓋 PETsARD 開發者的 Docker 開發設定、測試和部署。

## 開發環境設定

### 先決條件

- 已安裝並運行 Docker Desktop
- 已在本地複製 Git 儲存庫
- 對 Docker 概念有基本了解

### 快速環境檢查

使用基本指令驗證您的 Docker 設定：

```bash
# 檢查 Docker 安裝和版本
docker --version

# 檢查 Docker daemon 狀態
docker info

# 測試基本 Docker 功能
docker run --rm hello-world
```

這將：
- 驗證 Docker 版本
- 檢查 Docker daemon 狀態
- 測試基本 Docker 功能

## 使用 Docker 進行本地開發

### 建置本地映像檔

```bash
# 建置標準版本（預設 - 不含 Jupyter）
docker build -t petsard:latest .

# 建置包含 Jupyter Lab 的 Jupyter 版本
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .

# 針對 ARM64 平台（Apple Silicon）
docker buildx build --platform linux/arm64 --load --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter --no-cache .
```

### 運行容器

#### 標準容器

```bash
# 運行標準容器（不含 Jupyter）- Python REPL
docker run -it --entrypoint /opt/venv/bin/python3 petsard:latest

# 使用資料卷掛載運行
docker run -it -v $(pwd):/app/data --entrypoint /opt/venv/bin/python3 petsard:latest
```

#### Jupyter Lab 容器

```bash
# 運行包含 Jupyter Lab 的容器（預設行為）
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter

# 在 Jupyter 容器中運行 Python REPL
docker run -it --entrypoint /opt/venv/bin/python3 petsard:jupyter

# 在 http://localhost:8888 存取 Jupyter Lab
```

**特點：**
- Jupyter Lab 介面用於互動式開發
- 開放 8888 端口供瀏覽器存取
- 卷掛載以保持資料和 notebook 持久化
- ARM64 優化，適用於 Apple Silicon

## 開發環境管理

### Docker 建置變體

PETsARD 提供靈活的 Docker 建置，可選擇性包含 Jupyter Lab 支援：

```bash
# 建置 Jupyter 版本（包含 Jupyter Lab）
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .

# 建置標準版本（不含 Jupyter）
docker build --build-arg INCLUDE_JUPYTER=false -t petsard:standard .

# 預設建置（包含 Jupyter）
docker build -t petsard:latest .
```

### Jupyter 版 vs 標準版環境

#### Jupyter 環境特點

- **Jupyter Lab 整合** - 完整的 Jupyter 環境，可在 http://localhost:8888 存取
- **互動式開發** - 卷掛載以進行即時開發
- **完整開發堆疊** - 來自 pyproject.toml [docker] 群組的所有依賴
- **較大映像檔大小** - 包含 Jupyter Lab 和開發工具

```bash
# 運行包含 Jupyter Lab 的 Jupyter 容器
docker run -it --rm \
  -p 8888:8888 \
  -v $(pwd):/workspace \
  petsard:jupyter
# 在 http://localhost:8888 存取 Jupyter Lab
```

#### 標準環境特點

- **核心運行時** - 僅包含 PETsARD 核心功能的必要依賴
- **較小映像檔大小** - 針對部署優化，不含 Jupyter
- **安全優化** - 非 root 使用者執行（UID 1000）
- **Distroless 基礎** - 使用 gcr.io/distroless/python3 的最小攻擊面

```bash
# 運行標準容器
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  petsard:standard
```

### 配置檔案

Docker 環境使用這些關鍵檔案：

- **`Dockerfile`** - 多階段生產優化映像檔，可選擇性支援 Jupyter
- **`pyproject.toml`** - 專案配置與依賴群組
- **`.github/workflows/docker-publish.yml`** - 自動建置的 CI/CD 流水線

### 環境變數

容器會自動配置：

```bash
# Python 優化
PYTHONPATH=/app
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Jupyter 專用（當 INCLUDE_JUPYTER=true 時）
JUPYTER_ENABLE_LAB=yes
JUPYTER_ALLOW_ROOT=1

# 建置變體指示器
INCLUDE_JUPYTER=true/false
```

## 開發工作流程

### 功能開發

1. **設定開發環境**
   ```bash
   # 建置包含 Jupyter Lab 的 Jupyter 映像檔（ARM64 優化）
   docker buildx build --platform linux/arm64 --load --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter --no-cache .
   
   # 啟動包含 Jupyter Lab 的容器
   docker run -it -p 8888:8888 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/notebooks:/app/notebooks \
     petsard:jupyter
   
   # 在 http://localhost:8888 存取 Jupyter Lab
   ```

2. **編碼和測試**
   ```bash
   # 運行 Python REPL 進行測試
   docker run -it --entrypoint /opt/venv/bin/python3 petsard:jupyter
   
   # 使用資料卷運行測試
   docker run -it -v $(pwd):/app/data --entrypoint /opt/venv/bin/python3 petsard:jupyter
   
   # 在容器內測試 PETsARD 功能
   # python -m petsard.executor demo/use-cases/data-constraining.yaml
   ```

3. **測試兩種建置變體**
   ```bash
   # 測試 Jupyter 建置（包含 Jupyter Lab）
   docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .
   
   # 測試標準建置（預設，不含 Jupyter）
   docker build -t petsard:latest .
   
   # 針對 ARM64 平台
   docker buildx build --platform linux/arm64 --load --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter --no-cache .
   ```

### 研究和實驗工作流程

1. **啟動 Jupyter 環境**
   ```bash
   # 運行包含 Jupyter Lab 的容器
   docker run -it --rm \
     -p 8888:8888 \
     -v $(pwd):/workspace \
     petsard:jupyter
   # 導航至 http://localhost:8888
   ```

2. **建立和運行 Notebook**
   - 使用 `/workspace` 目錄存放持久化 notebook
   - 直接存取 PETsARD 模組：`import petsard`
   - 實驗不同的配置

3. **匯出結果**
   ```bash
   # 存取容器 shell 進行檔案操作
   docker run -it --rm \
     -v $(pwd):/workspace \
     petsard:jupyter \
     bash
   # 您的 notebook 和資料會持久保存在掛載的卷中
   ```

## 測試和驗證

### 手動測試指令

```bash
# 測試基本功能（預設包含 Jupyter）
docker run --rm petsard:latest python -c "
import petsard
import importlib.metadata
print(f'✅ PETsARD v{importlib.metadata.version(\"petsard\")} 已載入')
from petsard.executor import Executor
print('✅ 所有模組匯入成功')
"

# 使用範例配置測試
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  petsard:latest \
  python -m petsard.executor demo/use-cases/data-constraining.yaml

# 測試 Jupyter 變體
docker run --rm \
  -p 8888:8888 \
  -v $(pwd):/workspace \
  petsard:jupyter \
  python -c "import jupyterlab; print('✅ Jupyter Lab 可用')"

# 測試標準變體
docker run --rm \
  petsard:standard \
  python -c "import petsard; print('✅ 標準建置正常')"
```

### 建置測試

```bash
# 測試標準建置（不含 Jupyter）
docker build --build-arg INCLUDE_JUPYTER=false -t petsard:test-standard .
docker run --rm petsard:test-standard python -c "import petsard; print('✅ 標準建置正常')"

# 測試 Jupyter 建置（包含 Jupyter Lab）
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:test-jupyter .
docker run --rm petsard:test-jupyter python -c "import jupyterlab; print('✅ Jupyter 建置正常')"

# 清理測試映像檔
docker rmi petsard:test-standard petsard:test-jupyter
```

## 多階段 Dockerfile 架構

Dockerfile 使用多階段建置進行優化：

### 建置階段
- 基於 `python:3.11-slim`
- 安裝建置依賴和編譯工具
- 在 `/opt/venv` 建置虛擬環境
- **ARM64 優化** - 針對 Apple Silicon 特別處理 CPU 版本的 PyTorch
- 根據 `INCLUDE_JUPYTER` 建置參數安裝 PETsARD 與依賴
- 使用 `--dependency-groups=docker` 安裝 Jupyter Lab

### 生產階段
- 基於 `python:3.11-slim`（非 distroless，以提供更好的相容性）
- 建立專用的 `petsard` 使用者以提高安全性
- 從建置階段複製虛擬環境和應用程式檔案
- 適應性入口腳本，處理 Jupyter 和 Python REPL 模式
- **ARM64 效能調校** - 針對 Apple Silicon 優化的環境變數

### 主要特點
- **Python 3.11** - 穩定的 Python 版本，與 anonymeter 相容
- **虛擬環境隔離** - 依賴隔離在 `/opt/venv`
- **ARM64 優化** - 針對 Apple Silicon 特別安裝 CPU 版本的 PyTorch
- **條件性 Jupyter** - 基於建置參數的可選 Jupyter Lab
- **非 root 執行** - 以專用的 `petsard` 使用者運行以提高安全性
- **跨平台支援** - 針對 x86_64 和 ARM64 架構優化

## CI/CD 整合

### 自動建置

專案使用 GitHub Actions 進行自動 Docker 建置：

```yaml
# 由 semantic release 完成觸發
workflow_run:
  workflows: ["Semantic Release"]
  types: [completed]
  branches: [main, dev]
```

### 版本管理

- **Semantic Release 整合** - 版本號自動管理
- **動態標籤** - 每次發布創建多個標籤：
  - `latest`（main 分支）
  - `v1.4.0`（特定版本）
  - `1.4`（主要.次要版本）
  - `1`（主要版本）

### 註冊表發布

映像檔發布到 GitHub Container Registry：
- `ghcr.io/nics-tw/petsard:latest`
- `ghcr.io/nics-tw/petsard:v1.4.0`

## 除錯問題

### 檢查容器日誌

```bash
# 檢查運行中容器的日誌
docker logs <container_id>

# 即時追蹤日誌
docker logs -f <container_id>
```

### 互動式除錯

```bash
# 啟動具有除錯存取權限的容器
docker run -it --rm \
  -v $(pwd):/workspace \
  petsard:jupyter \
  bash

# 除錯標準版本
docker run -it --rm \
  -v $(pwd):/workspace \
  petsard:standard \
  python
```

### 健康檢查除錯

```bash
# 手動健康檢查
docker run --rm petsard:latest python -c "
import importlib.metadata
try:
    version = importlib.metadata.version('petsard')
    print(f'✅ 健康檢查通過 - PETsARD v{version}')
except Exception as e:
    print(f'❌ 健康檢查失敗: {e}')
"
```

## 效能優化

### 建置優化

- **層快取** - Dockerfile 針對 Docker 層快取優化
- **多階段建置** - 更小的最終映像檔
- **依賴快取** - 在程式碼複製前安裝需求

### 運行時優化

- **虛擬環境** - 隔離的 Python 環境
- **最小基礎映像檔** - `python:3.11-slim` 以減少佔用空間
- **非 root 執行** - 安全性和權限優化

## 疑難排解

### 常見問題

1. **建置失敗**
   ```bash
   # 無快取的乾淨建置
   docker build --no-cache -t petsard:debug .
   ```

2. **權限問題**
   ```bash
   # 修正檔案權限
   docker run --rm -v $(pwd):/workspace \
     --user $(id -u):$(id -g) \
     petsard:dev chown -R $(id -u):$(id -g) /workspace
   ```

3. **記憶體問題**
   ```bash
   # 增加 Docker 記憶體限制
   docker run --memory=4g petsard:dev
   ```

### 環境變數

容器中使用的關鍵環境變數：

```bash
# Python 優化
PYTHONPATH=/app
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Jupyter 專用（當 INCLUDE_JUPYTER=true 時）
JUPYTER_ENABLE_LAB=yes
JUPYTER_ALLOW_ROOT=1

# 建置變體指示器
INCLUDE_JUPYTER=true/false
```

## 最佳實踐

1. **使用 Docker Compose** 進行開發工作流程
2. **本地測試** 後再推送變更
3. **監控映像檔大小** 保持最小化
4. **使用健康檢查** 進行生產部署
5. **遵循語義版本控制** 進行映像檔標籤
6. **記錄環境變數** 和配置選項

## 安全考量

- **非 root 使用者** 在生產環境執行
- **最小攻擊面** 使用精簡基礎映像檔
- **無硬編碼機密** 在 Dockerfile 中
- **定期基礎映像檔更新** 以獲得安全修補程式