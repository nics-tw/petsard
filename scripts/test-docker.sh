#!/bin/bash

# PETsARD Docker 測試腳本
# 此腳本用於測試 Docker 映像的建置和基本功能

set -e  # 遇到錯誤時停止執行

echo "🐳 PETsARD Docker 測試腳本"
echo "=========================="

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝或不在 PATH 中"
    exit 1
fi

echo "✅ Docker 已安裝: $(docker --version)"

# 檢查 Docker 是否運行
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon 未運行"
    exit 1
fi

echo "✅ Docker daemon 正在運行"

# 建置 Docker 映像
echo ""
echo "🔨 建置 Docker 映像..."
if docker build -t petsard:test .; then
    echo "✅ Docker 映像建置成功"
else
    echo "❌ Docker 映像建置失敗"
    exit 1
fi

# 測試映像基本功能
echo ""
echo "🧪 測試 Docker 映像基本功能..."

# 測試 Python 和 PETsARD 匯入
echo "測試 PETsARD 套件匯入..."
if docker run --rm petsard:test python -c "
import petsard
print('✅ PETsARD 套件匯入成功')

from petsard.executor import Executor
print('✅ Executor 類別可用')

from petsard import loader, constrainer, synthesizer, evaluator
print('✅ 主要模組匯入成功')

print('🎉 所有基本測試通過！')
"; then
    echo "✅ 基本功能測試通過"
else
    echo "❌ 基本功能測試失敗"
    exit 1
fi

# 測試健康檢查
echo ""
echo "🏥 測試健康檢查..."
if docker run --rm petsard:test python -c "import petsard; print('OK')"; then
    echo "✅ 健康檢查通過"
else
    echo "❌ 健康檢查失敗"
    exit 1
fi

# 檢查映像大小
echo ""
echo "📊 映像資訊:"
docker images petsard:test --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
echo "🎉 所有測試通過！Docker 映像已準備就緒。"
echo ""
echo "📝 使用方式:"
echo "  docker run -it --rm petsard:test"
echo "  docker run -it --rm -v \$(pwd):/workspace petsard:test bash"
echo ""
echo "🧹 清理測試映像:"
echo "  docker rmi petsard:test"