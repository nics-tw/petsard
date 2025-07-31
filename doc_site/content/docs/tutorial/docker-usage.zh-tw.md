---
title: 使用 Docker
type: docs
weight: 10
prev: docs/tutorial/external-synthesis-default-evaluation
next: docs/tutorial/use-cases
---

PETsARD 提供預先建置的 Docker 容器和本地開發環境。本指南將說明如何開始使用 Docker 容器。

## 快速開始

### 選項 1：預先建置的容器（推薦給使用者）

```bash
# 拉取最新版本
docker pull ghcr.io/nics-tw/petsard:latest

# 運行互動式容器
docker run -it --rm ghcr.io/nics-tw/petsard:latest
```

### 選項 2：本地開發環境

如果您有 PETsARD 原始碼，可以建置並運行容器：

```bash
# 複製儲存庫（如果尚未完成）
git clone https://github.com/nics-tw/petsard.git
cd petsard

# 建置標準版本（預設 - 不含 Jupyter）
docker build -t petsard:latest .

# 建置並運行包含 Jupyter Lab 的 Jupyter 版本
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter

# 在 http://localhost:8888 存取 Jupyter Lab
```

### 使用您的資料運行

```bash
# 使用預先建置的容器（標準版本）
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  ghcr.io/nics-tw/petsard:latest

# 使用本地 Jupyter 環境
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter
# 然後在 http://localhost:8888 存取 Jupyter Lab
```

## 可用標籤

- `latest` - 最新穩定版本（來自 main 分支）
- `dev` - 開發版本（來自 dev 分支）
- `v1.4.0` - 特定版本標籤
- `1.4` - 主要.次要版本
- `1` - 主要版本

## 運行範例

### 執行配置檔案

```bash
# 運行特定的 YAML 配置
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ghcr.io/nics-tw/petsard:latest \
  python -m petsard.executor demo/tutorial/use-cases/data-constraining.yaml
```

### 互動式開發

```bash
# 啟動互動式 Python 會話
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  ghcr.io/nics-tw/petsard:latest

# 在容器內，您可以運行：
# import petsard
# print('PETsARD 已準備就緒！')
```

### 批次處理

```bash
# 處理多個配置檔案
docker run -it --rm \
  -v $(pwd)/configs:/app/configs \
  -v $(pwd)/output:/app/output \
  ghcr.io/nics-tw/petsard:latest \
  bash -c "
    for config in /app/configs/*.yaml; do
      echo \"正在處理 \$config\"
      python -m petsard.executor \"\$config\"
    done
  "
```

## 本地開發環境管理

如果您正在使用 PETsARD 原始碼，可以直接建置和管理容器：

### 可用建置選項

```bash
# 建置標準版本（預設 - 不含 Jupyter）
docker build -t petsard:latest .

# 建置 Jupyter 版本（包含 Jupyter Lab）
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .

# 針對 ARM64 平台（Apple Silicon）
docker buildx build --platform linux/arm64 --load --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter --no-cache .
```

### 運行不同變體

```bash
# 運行包含 Jupyter Lab 的 Jupyter 版本
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter

# 運行標準版本 Python REPL
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  petsard:latest

# 在 Jupyter 容器中運行 Python REPL 模式
docker run -it --entrypoint /opt/venv/bin/python3 petsard:jupyter
```

### Jupyter 版 vs 標準版模式

```bash
# Jupyter 模式 - 包含 Jupyter Lab 和開發工具
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter

# 標準模式 - 最小運行時環境（預設）
docker build -t petsard:latest .
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  petsard:latest
```

### 開發功能

- **Jupyter Lab**：可在 http://localhost:8888 存取（使用 Jupyter 變體時）
- **即時程式碼重載**：透過卷掛載，原始碼的變更會立即反映
- **完整開發堆疊**：包含來自 pyproject.toml [docker] 群組的依賴
- **卷掛載**：您的本地檔案會掛載到容器中以進行持久化開發

## 環境變數

容器支援以下環境變數：

- `PYTHONPATH` - Python 模組搜尋路徑（預設：`/app`）
- `PYTHONUNBUFFERED` - 禁用 Python 輸出緩衝（預設：`1`）
- `PYTHONDONTWRITEBYTECODE` - 禁止生成 .pyc 檔案（預設：`1`）

```bash
# 設定自訂環境變數
docker run -it --rm \
  -e PYTHONPATH=/workspace:/app \
  -v $(pwd):/workspace \
  ghcr.io/nics-tw/petsard:latest \
  python your_script.py
```

## 容器目錄結構

```
/app/
├── petsard/          # PETsARD 套件原始碼
├── demo/             # 範例檔案
├── templates/        # 模板檔案
├── pyproject.toml    # 專案配置
├── requirements.txt  # 依賴清單
└── README.md         # 說明文件
```

## 疑難排解

### 權限問題

```bash
# 如果遇到權限問題，可以指定使用者 ID
docker run -it --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd):/workspace \
  ghcr.io/nics-tw/petsard:latest \
  bash
```

### 記憶體限制

```bash
# 如需要可增加記憶體限制
docker run -it --rm \
  --memory=4g \
  ghcr.io/nics-tw/petsard:latest
```

### 健康檢查

```bash
# 驗證容器是否正常運作
docker run --rm ghcr.io/nics-tw/petsard:latest python -c "
import petsard
print('✅ PETsARD 載入成功')
from petsard.executor import Executor
print('✅ Executor 可用')
"
```

## 下一步

- 了解 [YAML 配置](../yaml-config) 進行實驗設定
- 探索 [預設合成](../default-synthesis) 範例
- 查看 [使用案例](../use-cases) 了解實際應用