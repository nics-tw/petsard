#!/bin/bash

# PETsARD 開發環境 Docker 管理腳本
# 提供開發環境的建置、啟動、停止等功能

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 預設為開發版，可透過環境變數或參數覆蓋
BUILD_TYPE=${BUILD_TYPE:-dev}
if [ "$1" = "prod" ] || [ "$1" = "production" ]; then
    BUILD_TYPE="prod"
    shift  # 移除第一個參數
fi

if [ "$BUILD_TYPE" = "prod" ]; then
    IMAGE_NAME="petsard"
    CONTAINER_NAME="petsard"
    DOCKERFILE="Dockerfile"
    COMPOSE_FILE="docker-compose.yml"
else
    IMAGE_NAME="petsard-dev"
    CONTAINER_NAME="petsard-dev"
    DOCKERFILE="Dockerfile.dev"
    COMPOSE_FILE="docker-compose.dev.yml"
fi

# 顯示標題
show_header() {
    if [ "$BUILD_TYPE" = "prod" ]; then
        echo -e "${BLUE}🐳 PETsARD 生產環境管理${NC}"
        echo -e "${BLUE}========================${NC}"
    else
        echo -e "${BLUE}🐳 PETsARD 開發環境管理${NC}"
        echo -e "${BLUE}========================${NC}"
    fi
    echo -e "建置類型: ${GREEN}${BUILD_TYPE}${NC}"
    echo -e "映像檔: ${GREEN}${IMAGE_NAME}${NC}"
    echo -e "容器: ${GREEN}${CONTAINER_NAME}${NC}"
    echo -e "Dockerfile: ${GREEN}${DOCKERFILE}${NC}"
    echo ""
}

# 顯示幫助資訊
show_help() {
    show_header
    echo -e "${YELLOW}使用方式:${NC}"
    echo "  $0 [prod|production] <command>"
    echo "  BUILD_TYPE=prod $0 <command>"
    echo ""
    echo -e "${YELLOW}建置類型:${NC}"
    echo "  dev (預設)  - 開發版 (包含 Jupyter Lab 和開發工具)"
    echo "  prod        - 生產版 (精簡版本)"
    echo ""
    echo -e "${YELLOW}可用指令:${NC}"
    echo "  up      - 啟動環境"
    echo "  down    - 停止並移除環境"
    echo "  build   - 建置映像檔"
    echo "  shell   - 進入容器的 shell"
    echo "  test    - 在容器中運行測試"
    echo "  logs    - 顯示容器日誌"
    echo "  clean   - 清理映像檔和容器"
    echo "  help    - 顯示此幫助資訊"
    echo ""
    echo -e "${YELLOW}範例:${NC}"
    echo "  $0 up              # 啟動開發環境 (預設)"
    echo "  $0 prod up         # 啟動生產環境"
    echo "  BUILD_TYPE=prod $0 build  # 建置生產版映像檔"
    echo "  $0 shell           # 進入開發容器"
    echo "  $0 prod shell      # 進入生產容器"
}

# 檢查 Docker 是否可用
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安裝或不在 PATH 中${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon 未運行${NC}"
        exit 1
    fi
}

# 檢查必要檔案
check_files() {
    if [ ! -f "$DOCKERFILE" ]; then
        echo -e "${RED}❌ $DOCKERFILE 不存在${NC}"
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ $COMPOSE_FILE 不存在${NC}"
        exit 1
    fi
}

# 建置映像檔
build_image() {
    if [ "$BUILD_TYPE" = "prod" ]; then
        echo -e "${BLUE}🔨 建置生產版映像檔...${NC}"
        if docker build -f "$DOCKERFILE" -t "$IMAGE_NAME:latest" .; then
            echo -e "${GREEN}✅ 生產版映像檔建置成功${NC}"
        else
            echo -e "${RED}❌ 生產版映像檔建置失敗${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}🔨 建置開發版映像檔...${NC}"
        if docker-compose -f "$COMPOSE_FILE" build; then
            echo -e "${GREEN}✅ 開發版映像檔建置成功${NC}"
        else
            echo -e "${RED}❌ 開發版映像檔建置失敗${NC}"
            exit 1
        fi
    fi
}

# 啟動環境
start_env() {
    if [ "$BUILD_TYPE" = "prod" ]; then
        echo -e "${BLUE}🚀 啟動生產環境...${NC}"
        if docker-compose -f "$COMPOSE_FILE" up -d; then
            echo -e "${GREEN}✅ 生產環境已啟動${NC}"
            echo -e "${YELLOW}📝 使用 '$0 prod shell' 進入容器${NC}"
            echo -e "${YELLOW}📝 使用 '$0 prod logs' 查看日誌${NC}"
        else
            echo -e "${RED}❌ 生產環境啟動失敗${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}🚀 啟動開發環境...${NC}"
        if docker-compose -f "$COMPOSE_FILE" up -d; then
            echo -e "${GREEN}✅ 開發環境已啟動${NC}"
            echo -e "${YELLOW}📝 Jupyter Lab: http://localhost:8888${NC}"
            echo -e "${YELLOW}📝 使用 '$0 shell' 進入容器${NC}"
            echo -e "${YELLOW}📝 使用 '$0 logs' 查看日誌${NC}"
        else
            echo -e "${RED}❌ 開發環境啟動失敗${NC}"
            exit 1
        fi
    fi
}

# 停止環境
stop_env() {
    if [ "$BUILD_TYPE" = "prod" ]; then
        echo -e "${BLUE}🛑 停止生產環境...${NC}"
        if docker-compose -f "$COMPOSE_FILE" down; then
            echo -e "${GREEN}✅ 生產環境已停止${NC}"
        else
            echo -e "${RED}❌ 停止生產環境失敗${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}🛑 停止開發環境...${NC}"
        if docker-compose -f "$COMPOSE_FILE" down; then
            echo -e "${GREEN}✅ 開發環境已停止${NC}"
        else
            echo -e "${RED}❌ 停止開發環境失敗${NC}"
            exit 1
        fi
    fi
}

# 進入容器 shell
enter_shell() {
    echo -e "${BLUE}🐚 進入開發容器...${NC}"
    
    if docker-compose -f "$COMPOSE_FILE" exec petsard-dev bash; then
        echo -e "${GREEN}✅ 已退出容器${NC}"
    else
        echo -e "${RED}❌ 無法進入容器，請確保容器正在運行${NC}"
        echo -e "${YELLOW}💡 嘗試先運行: $0 up${NC}"
        exit 1
    fi
}

# 運行測試
run_tests() {
    echo -e "${BLUE}🧪 在開發容器中運行測試...${NC}"
    
    if docker-compose -f "$COMPOSE_FILE" exec petsard-dev python -m pytest tests/ -v; then
        echo -e "${GREEN}✅ 測試完成${NC}"
    else
        echo -e "${RED}❌ 測試失敗${NC}"
        exit 1
    fi
}

# 顯示日誌
show_logs() {
    echo -e "${BLUE}📋 顯示容器日誌...${NC}"
    
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# 清理映像檔和容器
cleanup() {
    echo -e "${BLUE}🧹 清理開發環境...${NC}"
    
    # 停止並移除容器
    docker-compose -f "$COMPOSE_FILE" down --rmi all --volumes --remove-orphans
    
    # 清理懸掛的映像檔
    if docker images -f "dangling=true" -q | grep -q .; then
        docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 主要邏輯
main() {
    case "${1:-help}" in
        "up")
            show_header
            check_docker
            check_files
            start_env
            ;;
        "down")
            show_header
            check_docker
            stop_env
            ;;
        "build")
            show_header
            check_docker
            check_files
            build_image
            ;;
        "shell")
            show_header
            check_docker
            enter_shell
            ;;
        "test")
            show_header
            check_docker
            run_tests
            ;;
        "logs")
            show_header
            check_docker
            show_logs
            ;;
        "clean")
            show_header
            check_docker
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知指令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 執行主要邏輯
main "$@"