# PETsARD 安裝器實作計劃

## 概述
創建一個簡化的 Python 腳本，用於下載和安裝 PETsARD 及其所有依賴項。

## 腳本規格

### 檔案名稱
`petsard_installer.py`

### 命令列介面
```bash
python petsard_installer.py --branch <branch_name> --python-version <version> --os <os_type>
```

### 參數說明
- `--branch`: Git 分支名稱（如：main, dev）
- `--python-version`: Python 版本（如：3.10, 3.11, 3.11.5）
- `--os`: 作業系統（linux, windows, macos）

## 核心功能實作

### 1. 命令列參數解析
```python
import argparse
import sys
import subprocess
import os
import tempfile
from datetime import datetime
import platform
```

### 2. 主要函數結構

#### `parse_arguments()`
- 使用 `argparse` 解析命令列參數
- 驗證參數有效性
- 設定預設值

#### `run_command(cmd, cwd=None)`
- 執行系統命令的通用函數
- 捕獲輸出和錯誤
- 返回執行結果

#### `get_git_info(branch)`
- Clone PETsARD 倉庫
- Checkout 指定分支
- 獲取最新 commit hash
- 獲取 PETsARD 版本號

#### `download_dependencies(python_version, os_type)`
- 使用 pip download 下載所有依賴，支援跨平台下載
- 使用 `--platform`, `--python-version`, `--abi` 參數指定目標環境
- 處理平台特定依賴
- 下載 PETsARD 本身

#### `write_installation_log(log_data)`
- 創建帶時間戳的日誌檔案
- 記錄所有安裝資訊
- 格式化輸出

### 3. 執行流程

1. **初始化**
   - 解析命令列參數
   - 創建臨時工作目錄
   - 驗證環境

2. **Git 操作**
   - Clone https://github.com/nics-tw/petsard.git
   - Checkout 指定分支
   - 獲取 commit hash 和版本資訊

3. **依賴下載**
   - 使用 `pip download` 下載所有輪子，支援跨平台下載
   - 使用以下參數指定目標環境：
     - `--platform`: 指定平台（如 linux_x86_64, win_amd64, macosx_10_9_x86_64）
     - `--python-version`: 指定 Python 版本（如 3.10, 3.11）
     - `--abi`: 指定 ABI（如 cp311, none）
     - `--implementation`: 指定實作（cp 為 CPython）
   - 處理依賴群組（pytorch, jupyter, dev）
   - 下載純 Python 套件（universal wheels）和平台特定套件

4. **日誌記錄**
   - 記錄安裝時間
   - 記錄 PETsARD 版本
   - 記錄指定參數
   - 記錄 Git commit hash
   - 記錄下載的套件清單

5. **清理**
   - 清理臨時檔案
   - 輸出完成訊息

## 日誌格式

### 檔案命名
`petsard_install_YYYYMMDD_HHMMSS.log`

### 日誌內容
```
=== PETsARD Installation Log ===
Installation Time: 2025-01-21 17:30:45 +0800
PETsARD Version: 1.6.0-rc.1
Git Branch: dev
Git Commit Hash: abc123def456...
Python Version: 3.11
Operating System: linux
Downloaded Packages: 45
Installation Status: SUCCESS

=== Parameters ===
Branch: dev
Python Version: 3.11
OS Type: linux

=== Downloaded Packages ===
petsard-1.6.0rc1-py3-none-any.whl
anonymeter-1.0.0-py3-none-any.whl
...

=== Git Information ===
Repository: https://github.com/nics-tw/petsard.git
Branch: dev
Latest Commit: abc123def456789...
Commit Date: 2025-01-21 10:15:30
```

## 錯誤處理

### 常見錯誤情況
1. 網路連線問題
2. Git 分支不存在
3. Python 版本不相容
4. 磁碟空間不足
5. 權限問題

### 處理策略
- 提供清楚的錯誤訊息
- 記錄錯誤到日誌檔案
- 適當的退出碼
- 清理臨時檔案

## 預期檔案大小
約 150-200 行 Python 程式碼

## 相依性
僅使用 Python 標準庫，無額外依賴

## 測試計劃
1. 測試不同分支
2. 測試不同 Python 版本
3. 測試不同作業系統
4. 測試錯誤情況
5. 驗證日誌格式

## 使用範例
```bash
# 基本使用
python petsard_installer.py --branch main --python-version 3.11 --os linux

# 開發分支
python petsard_installer.py --branch dev --python-version 3.10 --os windows

# macOS 環境
python petsard_installer.py --branch main --python-version 3.11.5 --os macos