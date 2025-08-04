# PETsARD AI 輔助開發設置指南

## 🚀 快速開始

這個指南將幫助您設置 PETsARD 的 AI 輔助開發環境，確保團隊協作時保持架構一致性。

## 📋 前置需求

- Python 3.10+
- Git
- Roo (AI 代碼助手)

## 🔧 設置步驟

### 1. 安裝 Pre-commit Hook

```bash
# 複製 pre-commit hook
cp .ai/scripts/pre-commit-hook.sh .git/hooks/pre-commit

# 設置執行權限
chmod +x .git/hooks/pre-commit

# 測試 hook 是否正常工作
.git/hooks/pre-commit
```

### 2. 配置 Roo

在 Roo 中載入專案配置：

```bash
# Roo 會自動讀取 .roo/project.yaml 配置
# 確保以下文件存在：
ls .roo/project.yaml
ls .ai/roo-config/project-context.md
ls .ai/roo-config/architecture-rules.md
```

### 3. 測試開發助手

```bash
# 手動運行開發助手
python3 .ai/scripts/development-assistant.py

# 或者修改一個 Python 文件後運行
echo "# test comment" >> petsard/loader/loader.py
python3 .ai/scripts/development-assistant.py
git checkout petsard/loader/loader.py  # 恢復文件
```

## 📖 使用方式

### 日常開發流程

1. **開始開發前**
   ```
   # 在 Roo 中輸入
   "我要修改 [模組名稱]，請載入相關的功能設計文檔"
   ```

2. **進行代碼修改**
   - Roo 會自動提醒遵循架構規則
   - 參考載入的功能設計文檔
   - 遵循統一的 API 設計規範

3. **提交代碼**
   ```bash
   git add .
   git commit -m "feat(loader): 新增 CSV 載入功能"
   # 自動觸發 pre-commit hook 檢查
   ```

### Roo 使用範例

#### 修改 Loader 模組
```
開發者: "我要在 loader 模組新增 Excel 載入功能"

Roo (自動載入 .ai/functional_design/loader.md):
"根據 loader 模組的功能設計，新的載入功能需要：
1. 繼承 LoaderBase 抽象類別
2. 實現 load() 方法，回傳 tuple[pd.DataFrame, SchemaMetadata]
3. 使用 Metadater.create_schema() 生成詮釋資料
4. 更新 LoaderConfig 配置

我會幫您遵循現有的架構設計來實現 Excel 載入功能。"
```

#### 修改 Evaluator 模組
```
開發者: "我要新增一個隱私評估器"

Roo (自動載入 .ai/functional_design/evaluator.md):
"根據 evaluator 模組的功能設計，新的評估器需要：
1. 繼承 BaseEvaluator 抽象類別
2. 實現 _eval() 方法，回傳 dict[str, pd.DataFrame]
3. 在 EvaluatorMap 中註冊新的評估器
4. 創建對應的配置類別

請問您要實現什麼類型的隱私評估？我會確保遵循統一的評估結果格式。"
```

## 🔍 開發助手功能

### 自動檢查項目

- **文檔同步檢查**: 修改代碼時自動提醒更新對應文檔
- **架構規則檢查**: 確保遵循模組間依賴規則
- **API 一致性檢查**: 檢查方法命名和回傳格式
- **向後相容性提醒**: API 變更時的相容性檢查

### 生成的提醒範例

```
🔔 PETsARD 開發提醒

您修改了以下模組，請檢查對應的功能設計文檔是否需要更新：

## 📁 模組: petsard/loader/

修改的文件:
- petsard/loader/loader.py
  - ⚠️  檢測到類別或方法定義變更

對應文檔: .ai/functional_design/loader.md

架構檢查清單:
- [ ] 確認 load() 方法回傳 tuple[pd.DataFrame, SchemaMetadata]
- [ ] 檢查是否正確使用 Metadater.create_schema()
- [ ] 驗證向後相容性

💡 提醒事項:
1. 保持代碼與文檔同步是團隊協作的關鍵
2. API 變更時請確保向後相容性
3. 新增功能時請更新使用範例
```

## 📁 目錄結構說明

```
.ai/
├── README.md                    # AI 輔助開發總覽
├── SETUP-GUIDE.md              # 本設置指南
├── development-workflow.md      # 詳細開發流程
├── roo-config/                  # Roo 配置文件
│   ├── project-context.md       # 專案上下文
│   └── architecture-rules.md    # 架構規則
├── functional_design/           # 功能設計文檔
│   ├── system.md               # 整體系統設計
│   ├── loader.md               # Loader 模組設計
│   ├── metadater.md            # Metadater 模組設計
│   └── evaluator.md            # Evaluator 模組設計
└── scripts/                     # 自動化腳本
    ├── development-assistant.py # 開發助手
    └── pre-commit-hook.sh       # Git pre-commit hook

.roo/
└── project.yaml                 # Roo 專案配置
```

## 🎯 最佳實踐

### 1. 開發前準備
- 在 Roo 中載入相關模組的功能設計文檔
- 了解模組的架構原則和 API 規範
- 檢查是否有相關的測試需要更新

### 2. 代碼修改
- 遵循統一的命名規範 (create_*/analyze_*/validate_*)
- 使用完整的型別註解
- 保持函數式設計原則
- 確保不可變資料結構

### 3. 提交前檢查
- 運行 pre-commit hook 檢查
- 確認功能設計文檔已更新
- 驗證向後相容性
- 執行相關測試

### 4. 文檔維護
- 代碼變更時同步更新文檔
- 新增功能時添加使用範例
- 重大架構變更時更新系統設計

## 🆘 常見問題

### Q: Pre-commit hook 檢查失敗怎麼辦？
A: 根據提示檢查對應的功能設計文檔，確保代碼與文檔同步。

### Q: Roo 沒有自動載入配置怎麼辦？
A: 確認 `.roo/project.yaml` 文件存在，並重新啟動 Roo。

### Q: 如何跳過文檔檢查？
A: 在 pre-commit hook 提示時輸入 's' 跳過檢查，但不建議經常這樣做。

### Q: 如何添加新的模組文檔映射？
A: 在 `.ai/scripts/development-assistant.py` 中的 `module_doc_map` 添加新的映射關係。

## 🔗 相關資源

- [開發流程詳細說明](.ai/development-workflow.md)
- [專案上下文配置](.ai/roo-config/project-context.md)
- [架構規則說明](.ai/roo-config/architecture-rules.md)
- [功能設計文檔目錄](.ai/functional_design/)

## 📞 支援

如果在設置或使用過程中遇到問題，請：
1. 檢查本指南的常見問題部分
2. 查看相關的配置文件是否正確
3. 聯繫團隊技術負責人

---

🎉 **歡迎使用 PETsARD AI 輔助開發環境！**

這個設置將幫助團隊保持代碼品質和架構一致性，讓協作更加順暢。