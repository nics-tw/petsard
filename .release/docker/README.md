# Docker 相關檔案 Docker Related Files

此目錄包含 PETsARD 專案的 Docker 容器相關配置檔案。
This directory contains Docker container related configuration files for the PETsARD project.

## 檔案說明 File Descriptions

### [`entrypoint.sh`](entrypoint.sh)
Docker 容器的進入點腳本，用於啟動 Jupyter Lab 服務。
Docker container entrypoint script for starting Jupyter Lab service.

**功能 Features:**
- 啟動 Jupyter Lab 在 0.0.0.0:8888
- 允許 root 使用者執行
- 無需認證令牌（開發環境用）
- 允許跨域存取

**使用方式 Usage:**
此檔案會在 Docker 容器啟動時自動執行，無需手動呼叫。
This file is automatically executed when the Docker container starts, no manual invocation required.

## 目錄結構 Directory Structure

```
.release/docker/
├── README.md          # 此說明檔案 This documentation file
└── entrypoint.sh      # Docker 進入點腳本 Docker entrypoint script
```

## 相關檔案 Related Files

- [`../../Dockerfile`](../../Dockerfile) - 主要的 Docker 建置檔案
- [`../../compose.yml`](../../compose.yml) - Docker Compose 配置檔案（如果存在）

## 維護注意事項 Maintenance Notes

- 修改 `entrypoint.sh` 後需要重新建置 Docker 映像檔
- 確保腳本具有執行權限（chmod +x）
- 生產環境使用時請考慮安全性設定