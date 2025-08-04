#!/bin/bash
# PETsARD Pre-commit Hook
# 在提交前檢查功能設計文檔同步性

set -e

echo "🔍 PETsARD 開發檢查..."

# 檢查是否在 PETsARD 專案根目錄
if [ ! -f "pyproject.toml" ] || [ ! -d ".ai" ]; then
    echo "⚠️  不在 PETsARD 專案根目錄，跳過檢查"
    exit 0
fi

# 獲取修改的 Python 文件
MODIFIED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -n "$MODIFIED_PY_FILES" ]; then
    echo "📝 檢測到 Python 文件修改："
    echo "$MODIFIED_PY_FILES" | sed 's/^/  - /'
    echo ""
    
    # 檢查 Python 是否可用
    if ! command -v python3 &> /dev/null; then
        echo "⚠️  Python3 不可用，跳過自動檢查"
        echo "請手動檢查相關的功能設計文檔是否需要更新"
        exit 0
    fi
    
    # 運行開發助手
    echo "🤖 運行開發助手檢查..."
    if python3 .ai/scripts/development-assistant.py; then
        echo ""
        
        # 檢查是否有需要更新的文檔
        ANALYSIS_FILE=".ai/scripts/last_analysis.json"
        if [ -f "$ANALYSIS_FILE" ]; then
            # 使用 Python 檢查分析結果
            NEEDS_DOC_UPDATE=$(python3 -c "
import json
try:
    with open('$ANALYSIS_FILE', 'r') as f:
        data = json.load(f)
    print('yes' if data.get('analysis') else 'no')
except:
    print('no')
")
            
            if [ "$NEEDS_DOC_UPDATE" = "yes" ]; then
                echo "❓ 您是否已經檢查並更新了相關的功能設計文檔？"
                echo "   輸入 'y' 繼續提交，'n' 取消提交，'s' 跳過檢查："
                read -r response
                
                case "$response" in
                    [Yy]|[Yy][Ee][Ss])
                        echo "✅ 繼續提交"
                        ;;
                    [Ss]|[Ss][Kk][Ii][Pp])
                        echo "⚠️  跳過文檔檢查，繼續提交"
                        ;;
                    *)
                        echo "❌ 請先更新功能設計文檔後再提交"
                        echo ""
                        echo "💡 提示："
                        echo "   - 檢查 .ai/functional_design/ 目錄中對應的文檔"
                        echo "   - 更新 API 介面、使用範例或架構說明"
                        echo "   - 確保文檔與代碼實現一致"
                        exit 1
                        ;;
                esac
            fi
        fi
    else
        echo "⚠️  開發助手執行失敗，但不阻止提交"
    fi
else
    echo "✅ 沒有 Python 文件修改"
fi

# 檢查是否修改了功能設計文檔
MODIFIED_DOC_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.ai/functional_design/.*\.md$' || true)

if [ -n "$MODIFIED_DOC_FILES" ]; then
    echo "📚 檢測到功能設計文檔修改："
    echo "$MODIFIED_DOC_FILES" | sed 's/^/  - /'
    echo "✅ 感謝您保持文檔同步！"
fi

# 檢查提交訊息格式（如果使用 conventional commits）
COMMIT_MSG_FILE="$1"
if [ -n "$COMMIT_MSG_FILE" ] && [ -f "$COMMIT_MSG_FILE" ]; then
    COMMIT_MSG=$(head -n1 "$COMMIT_MSG_FILE")
    
    # 檢查是否符合 conventional commits 格式
    if [[ ! "$COMMIT_MSG" =~ ^(feat|fix|docs|style|refactor|perf|test|chore|build|ci)(\(.+\))?: .+ ]]; then
        echo ""
        echo "💡 建議使用 Conventional Commits 格式："
        echo "   feat: 新功能"
        echo "   fix: 錯誤修復"
        echo "   docs: 文檔更新"
        echo "   refactor: 代碼重構"
        echo "   test: 測試相關"
        echo ""
        echo "   範例: feat(loader): 新增 CSV 載入功能"
        echo ""
        echo "是否繼續提交？ (y/n)"
        read -r response
        
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "❌ 提交已取消"
            exit 1
        fi
    fi
fi

echo ""
echo "✅ 所有檢查通過，準備提交"
echo "🚀 感謝您遵循 PETsARD 開發規範！"

exit 0