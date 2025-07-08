#!/bin/bash

# 快速 Docker 測試腳本
echo "🐳 快速 Docker 測試"
echo "=================="

# 檢查 Docker 狀態
echo "1. 檢查 Docker 版本..."
docker --version

echo ""
echo "2. 檢查 Docker daemon 狀態..."
if docker info > /dev/null 2>&1; then
    echo "✅ Docker daemon 正在運行"
else
    echo "❌ Docker daemon 未運行"
    echo "請確保 Docker Desktop 已啟動"
    exit 1
fi

echo ""
echo "3. 測試基本 Docker 功能..."
if docker run --rm hello-world > /dev/null 2>&1; then
    echo "✅ Docker 基本功能正常"
else
    echo "❌ Docker 基本功能測試失敗"
    exit 1
fi

echo ""
echo "🎉 Docker 安裝和配置正確！"
echo "現在可以建置 PETsARD Docker 映像了。"