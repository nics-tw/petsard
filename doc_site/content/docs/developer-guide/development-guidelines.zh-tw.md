---
title: 開發指引
type: docs
weight: 81
prev: docs/developer-guide
next: docs/developer-guide/benchmark-datasets
---

## 開發流程

### 分支保護

- `main` 與 `dev` 分支已受到保護
- 除了受 CAPE 團隊核准的特殊操作外，所有合併動作都需要至少一名本人以外的 CAPE 團隊成員進行程式碼審查（Code Review）

### Issue 與 Pull Request 規範

1. **Issue 管理**
   - 所有功能變動都必須先開立 Issue
   - Issue 應清楚描述變動目的、預期行為和影響範圍

2. **Pull Request 要求**
   - 一個 Issue 對應一個 Pull Request
   - 一個 Pull Request 建議只包含一個 commit
   - PR 標題應符合 Angular commit 規範（[參考連結](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits)）
   - PR 完成後，對應的功能分支應該被刪除

3. **功能開發流程**
   - 建議依照 task 建立對應的功能分支進行開發
   - 理想情況下，新功能開發應分為三個獨立的 PR：
     1. 功能實作（feat）
     2. 文件更新（doc）
     3. 測試程式（test）
   - 允許在同一個功能 PR 中包含所有內容，但需在 commit message 中清楚說明

## 關鍵套件版本追蹤

以下列出關鍵套件的版本資訊，定期手動確認更新狀態。實際使用版本以 pyproject.toml 為準。

| 套件名稱 | 最低版本 | 使用中版本 | 最低版本發布日期 | 使用中版本發布日期 | 參考連結 |
|---------|---------|------------|----------------|------------------|---------|
| SDV | 1.17.4 | 1.17.4 | 2025/01/20 | 2025/01/20 | [GitHub](https://github.com/sdv-dev/SDV) |
| SDMetrics | 0.18.0 | 0.18.0 | 2024/12/14 | 2024/12/14 | [GitHub](https://github.com/sdv-dev/SDMetrics) |
| anonymeter | 1.0.0 | 1.0.0 | 2024/02/02 | 2024/02/02 | [GitHub](https://github.com/statice/anonymeter) |

## 開發環境設定

### 套件管理備忘錄

```bash
uv venv --python 3.10
uv sync
```

```bash
uv --project petsard add "urllib3>=2.2.2"
uv --project petsard add --group dev "tornado>=6.4.2"
```

```bash
uv export --format requirements-txt --no-group dev --no-editable > requirements.txt
uv export --format requirements-txt --all-groups --no-editable > requirements-dev.txt
```

## 版本控制備忘錄

```bash
semantic-release generate-config -f toml --pyproject >> pyproject.toml
```

遵循 Angular commit 規範：
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文件更新
- `style`: 程式碼風格修改
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置或工具相關更新