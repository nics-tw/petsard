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

使用提供的腳本驗證您的 Docker 設定：

```bash
# 檢查 Docker 安裝和基本功能
./scripts/quick-docker-test.sh
```

此腳本將：
- 驗證 Docker 版本
- 檢查 Docker daemon 狀態
- 測試基本 Docker 功能

## 使用 Docker 進行本地開發

### 建置本地映像檔

```bash
# 建置開發映像檔
docker build -t petsard:dev .

# 使用特定建置參數建置
docker build \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$(git rev-parse --short HEAD)" \
  -t petsard:local .
```

### Docker Compose 開發

專案包含一個完整的 `docker-compose.yml`，提供三個服務：

#### 1. 開發服務 (`petsard`)

```bash
# 啟動開發容器
docker-compose up -d petsard

# 進入容器
docker-compose exec petsard bash

# 停止容器
docker-compose down
```

**特點：**
- 將整個專案目錄掛載到 `/workspace`
- 持續性容器用於開發
- 程式碼變更即時反映在容器中

#### 2. 範例服務 (`petsard-demo`)

```bash
# 運行範例容器
docker-compose up petsard-demo
```

**特點：**
- 專注於 `/app/demo` 目錄
- 自動列出可用的 YAML 配置
- 輕量化，適合展示用途

#### 3. Jupyter 服務 (`petsard-jupyter`)

```bash
# 啟動 Jupyter notebook 伺服器
docker-compose up -d petsard-jupyter

# 在 http://localhost:8888 存取
```

**特點：**
- Jupyter notebook 環境
- 開放 8888 端口供瀏覽器存取
- 開發時無需驗證

## 測試和驗證

### 完整測試腳本

```bash
# 運行完整的 Docker 映像檔測試
./scripts/test-docker.sh
```

此腳本執行：
- Docker 環境驗證
- 帶錯誤處理的映像檔建置
- PETsARD 套件匯入測試
- 模組功能驗證
- 健康檢查驗證
- 映像檔大小和元資料顯示

### 手動測試指令

```bash
# 測試基本功能
docker run --rm petsard:dev python -c "
import petsard
import importlib.metadata
print(f'✅ PETsARD v{importlib.metadata.version(\"petsard\")} 已載入')
from petsard.executor import Executor
print('✅ 所有模組匯入成功')
"

# 使用範例配置測試
docker run --rm \
  -v $(pwd)/demo:/app/demo \
  petsard:dev \
  python -m petsard.executor /app/demo/use-cases/data-constraining.yaml
```

## 多階段 Dockerfile 架構

Dockerfile 使用多階段建置進行優化：

### 建置階段
- 基於 `python:3.12-slim`
- 安裝建置依賴和編譯工具
- 使用 `uv` 套件管理器進行更快的依賴安裝
- 在 `/opt/venv` 建置虛擬環境
- 以可編輯模式安裝 PETsARD

### 生產階段
- 最小運行時環境
- 僅從建置階段複製必要檔案
- 以非 root 使用者（UID 1000）運行以提高安全性
- 包含使用 `importlib.metadata` 的健康檢查

### 主要特點
- **Python 3.12** - 最新穩定 Python 版本
- **虛擬環境隔離** - 依賴隔離在 `/opt/venv`
- **安全性** - 非 root 使用者執行
- **健康監控** - 內建健康檢查
- **ARM64 支援** - 相容 Apple Silicon

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

## 開發工作流程

### 功能開發

1. **設定開發環境**
   ```bash
   # 啟動開發容器
   docker-compose up -d petsard
   docker-compose exec petsard bash
   ```

2. **編碼和測試**
   ```bash
   # 在容器內 - 您的變更是即時掛載的
   python -m pytest tests/
   python -m petsard.executor demo/use-cases/data-constraining.yaml
   ```

3. **測試 Docker 建置**
   ```bash
   # 推送前測試本地建置
   ./scripts/test-docker.sh
   ```

### 除錯問題

1. **檢查容器日誌**
   ```bash
   docker logs <container_id>
   docker-compose logs petsard
   ```

2. **互動式除錯**
   ```bash
   # 啟動帶除錯工具的容器
   docker run -it --rm \
     -v $(pwd):/workspace \
     --entrypoint bash \
     petsard:dev
   ```

3. **健康檢查除錯**
   ```bash
   # 手動健康檢查
   docker run --rm petsard:dev python -c "
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
- **最小基礎映像檔** - `python:3.12-slim` 以減少佔用空間
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

開發的關鍵環境變數：

```bash
# Python 優化
PYTHONPATH=/workspace:/app
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# 開發模式
PETSARD_ENV=development
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