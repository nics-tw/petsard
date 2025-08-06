# PETsARD 開發流程與 AI 輔助規範

## 🎯 設計目標

建立一個自動化的開發流程，確保所有開發者在使用 Roo 進行代碼修改時：
1. 自動載入 `.ai/` 目錄中的功能設計規範
2. 在修改代碼時遵循既定的架構設計
3. 自動提醒更新相關的功能設計文檔
4. 保持團隊開發的一致性和架構完整性

## 📁 開發流程配置結構

```
.ai/
├── README.md                           # AI 輔助開發說明
├── development-workflow.md             # 本文件：開發流程規範
├── roo-config/                         # Roo 配置文件
│   ├── project-context.md              # 專案上下文配置
│   ├── coding-standards.md             # 編碼標準
│   ├── architecture-rules.md           # 架構規則
│   └── review-checklist.md             # 代碼審查清單
├── functional_design/                  # 功能設計文檔
│   ├── loader.md
│   ├── metadater.md
│   ├── evaluator.md
│   ├── system.md
│   └── ...
└── templates/                          # 開發模板
    ├── module-template.md              # 新模組開發模板
    ├── api-design-template.md          # API 設計模板
    └── documentation-template.md       # 文檔更新模板
```

## 🔧 Roo 配置整合

### 1. 專案上下文自動載入

創建 `.ai/roo-config/project-context.md`，讓 Roo 在每次啟動時自動載入：

```markdown
# PETsARD 專案上下文

## 核心架構原則
- 模組化設計：每個模組職責清晰分離
- 函數式程式設計：使用純函數和不可變資料結構
- 統一介面：透過公開 API 進行模組間互動
- 向後相容：保持現有 API 穩定性

## 模組架構
- **Loader**: 資料載入和分割
- **Metadater**: 詮釋資料管理核心
- **Processor**: 資料前處理
- **Synthesizer**: 資料合成
- **Evaluator**: 品質評估
- **Reporter**: 結果報告
- **Constrainer**: 約束條件

## 開發規範
1. 修改任何模組時，必須檢查對應的 `.ai/functional_design/` 文檔
2. 新增功能時，必須更新相關的功能設計文檔
3. API 變更時，必須確保向後相容性
4. 所有公開介面都要有完整的型別註解
```

### 2. 自動化開發提醒系統

創建 `.ai/roo-config/architecture-rules.md`：

```markdown
# 架構規則與自動提醒

## 代碼修改檢查清單

### 當修改 `petsard/loader/` 時：
- [ ] 檢查 `.ai/functional_design/loader.md` 是否需要更新
- [ ] 確認 API 變更不會破壞向後相容性
- [ ] 驗證與 Metadater 模組的整合是否正常

### 當修改 `petsard/metadater/` 時：
- [ ] 檢查 `.ai/functional_design/metadater.md` 是否需要更新
- [ ] 確認三層架構 (Metadata/Schema/Field) 的完整性
- [ ] 驗證函數式設計原則的遵循

### 當修改 `petsard/evaluator/` 時：
- [ ] 檢查 `.ai/functional_design/evaluator.md` 是否需要更新
- [ ] 確認新的評估器遵循 BaseEvaluator 介面
- [ ] 驗證評估結果格式的一致性

## 自動提醒規則
1. 修改任何 `.py` 文件時，自動檢查對應模組的功能設計文檔
2. 新增類別或函數時，提醒更新 API 文檔
3. 修改公開介面時，強制檢查向後相容性
```

## 🚀 實施步驟

### 步驟 1: 創建 Roo 專案配置

在專案根目錄創建 `.roo/project.yaml`：

```yaml
name: "PETsARD"
description: "Privacy Enhancing Technologies Synthetic and Real Data"

# 自動載入 AI 輔助配置
context_files:
  - ".ai/roo-config/project-context.md"
  - ".ai/roo-config/architecture-rules.md"
  - ".ai/roo-config/coding-standards.md"

# 開發流程規則
development_rules:
  - name: "functional_design_sync"
    description: "確保功能設計文檔與代碼同步"
    trigger: "file_modified"
    pattern: "petsard/**/*.py"
    action: "check_documentation"
  
  - name: "api_compatibility_check"
    description: "檢查 API 向後相容性"
    trigger: "public_interface_changed"
    action: "compatibility_review"

# 模組對應的文檔映射
module_documentation_map:
  "petsard/loader/": ".ai/functional_design/loader.md"
  "petsard/metadater/": ".ai/functional_design/metadater.md"
  "petsard/evaluator/": ".ai/functional_design/evaluator.md"
  "petsard/processor/": ".ai/functional_design/processor.md"
  "petsard/synthesizer/": ".ai/functional_design/synthesizer.md"
  "petsard/reporter/": ".ai/functional_design/reporter.md"
  "petsard/constrainer/": ".ai/functional_design/constrainer.md"
```

### 步驟 2: 創建自動化提醒腳本

創建 `.ai/scripts/development-assistant.py`：

```python
#!/usr/bin/env python3
"""
PETsARD 開發助手
自動檢查代碼修改與功能設計文檔的同步性
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

class DevelopmentAssistant:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.ai_dir = self.project_root / ".ai"
        self.module_doc_map = {
            "petsard/loader/": "functional_design/loader.md",
            "petsard/metadater/": "functional_design/metadater.md",
            "petsard/evaluator/": "functional_design/evaluator.md",
            # ... 其他模組映射
        }
    
    def check_modified_files(self, modified_files: List[str]) -> Dict[str, str]:
        """檢查修改的文件並返回需要更新的文檔"""
        docs_to_check = {}
        
        for file_path in modified_files:
            if file_path.endswith('.py'):
                for module_path, doc_path in self.module_doc_map.items():
                    if module_path in file_path:
                        docs_to_check[module_path] = doc_path
                        break
        
        return docs_to_check
    
    def generate_reminder_message(self, docs_to_check: Dict[str, str]) -> str:
        """生成提醒訊息"""
        if not docs_to_check:
            return ""
        
        message = "🔔 開發提醒：您修改了以下模組，請檢查對應的功能設計文檔是否需要更新：\n\n"
        
        for module_path, doc_path in docs_to_check.items():
            full_doc_path = self.ai_dir / doc_path
            message += f"📁 模組: {module_path}\n"
            message += f"📄 文檔: {full_doc_path}\n"
            message += f"🔗 請檢查: 架構設計、API 介面、使用範例是否需要更新\n\n"
        
        message += "💡 提醒：保持代碼與文檔同步是團隊協作的關鍵！"
        return message

if __name__ == "__main__":
    # 可以整合到 git hooks 或 IDE 中
    assistant = DevelopmentAssistant(".")
    # 示例用法
    modified_files = sys.argv[1:] if len(sys.argv) > 1 else []
    docs_to_check = assistant.check_modified_files(modified_files)
    reminder = assistant.generate_reminder_message(docs_to_check)
    if reminder:
        print(reminder)
```

### 步驟 3: Git Hooks 整合

創建 `.ai/scripts/pre-commit-hook.sh`：

```bash
#!/bin/bash
# PETsARD Pre-commit Hook
# 在提交前檢查功能設計文檔同步性

echo "🔍 檢查功能設計文檔同步性..."

# 獲取修改的 Python 文件
MODIFIED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$MODIFIED_PY_FILES" ]; then
    echo "📝 檢測到 Python 文件修改："
    echo "$MODIFIED_PY_FILES"
    
    # 運行開發助手
    python .ai/scripts/development-assistant.py $MODIFIED_PY_FILES
    
    echo ""
    echo "❓ 您是否已經檢查並更新了相關的功能設計文檔？ (y/n)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ 請先更新功能設計文檔後再提交"
        exit 1
    fi
fi

echo "✅ 功能設計文檔檢查完成"
```

## 📋 開發者使用指南

### 1. 初始設置

每個開發者在開始工作前：

```bash
# 1. 安裝 pre-commit hook
cp .ai/scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 2. 配置 Roo 載入專案上下文
# 在 Roo 中設置自動載入 .ai/roo-config/ 中的配置文件
```

### 2. 日常開發流程

```bash
# 1. 開始開發前，檢查相關功能設計文檔
roo "我要修改 loader 模組，請先載入相關的功能設計文檔"

# 2. 進行代碼修改
# Roo 會自動提醒遵循架構規則

# 3. 提交前自動檢查
git add .
git commit -m "feat: 新增資料載入功能"
# 自動觸發功能設計文檔同步檢查
```

### 3. Roo 使用範例

```
開發者: "我要在 evaluator 模組新增一個評估器"

Roo (自動載入 .ai/functional_design/evaluator.md): 
"根據 evaluator 模組的功能設計，新的評估器需要：
1. 繼承 BaseEvaluator 抽象類別
2. 實現 _eval() 方法
3. 遵循統一的評估結果格式
4. 更新 EvaluatorMap 枚舉

請問您要實現什麼類型的評估器？我會幫您遵循現有的架構設計。"
```

## 🔄 持續改進機制

### 1. 文檔同步檢查

定期運行自動化腳本檢查：
- 代碼與文檔的一致性
- API 文檔的完整性
- 架構設計的遵循程度

### 2. 團隊協作規範

- **代碼審查**: 必須檢查功能設計文檔更新
- **架構討論**: 重大變更需要更新系統設計文檔
- **文檔維護**: 定期檢查文檔的準確性和完整性

### 3. 自動化測試

```python
# 在 CI/CD 中加入文檔同步測試
def test_documentation_sync():
    """測試代碼與功能設計文檔的同步性"""
    # 檢查每個模組的公開 API 是否在文檔中有描述
    # 檢查文檔中的範例代碼是否可以正常執行
    pass
```

## 📈 預期效益

1. **架構一致性**: 確保所有開發者遵循統一的架構設計
2. **文檔同步**: 代碼與文檔始終保持同步
3. **知識傳承**: 新加入的開發者能快速理解系統架構
4. **品質保證**: 減少架構偏離和設計不一致的問題
5. **協作效率**: 提高團隊協作的效率和品質

這個開發流程確保了 PETsARD 專案在多人協作時能夠保持架構的完整性和一致性，同時讓 AI 輔助開發成為團隊的標準工作流程。