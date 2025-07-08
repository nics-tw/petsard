---
title: 使用 Docker
type: docs
weight: 15
prev: docs/tutorial/external-synthesis-default-evaluation
next: docs/tutorial/use-cases
---

PETsARD 提供預先建置的 Docker 容器，方便部署和使用。本指南將說明如何從 GitHub Container Registry 開始使用 Docker 容器。

## 快速開始

### 拉取並運行容器

```bash
# 拉取最新版本
docker pull ghcr.io/nics-tw/petsard:latest

# 運行互動式容器
docker run -it --rm ghcr.io/nics-tw/petsard:latest
```

### 使用您的資料運行

```bash
# 掛載資料目錄並運行
docker run -it --rm \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/output:/workspace/output \
  ghcr.io/nics-tw/petsard:latest \
  bash
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
  python -m petsard.executor demo/use-cases/data-constraining.yaml
```

### 互動式開發

```bash
# 啟動互動式會話
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ghcr.io/nics-tw/petsard:latest \
  bash

# 在容器內，您可以運行：
python -c "import petsard; print('PETsARD 已準備就緒！')"
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