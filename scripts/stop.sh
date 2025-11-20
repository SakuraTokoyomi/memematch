#!/bin/bash

# ===================================================================
# MemeMatch 停止脚本
# ===================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "🛑 停止 MemeMatch 服务..."
echo ""

# 进入项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 停止后端
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}   ✅ 后端服务已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "   ℹ️  后端服务已经停止"
    fi
    rm logs/backend.pid
else
    echo -e "   ℹ️  未找到后端PID文件"
fi

# 停止前端
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}   ✅ 前端服务已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "   ℹ️  前端服务已经停止"
    fi
    rm logs/frontend.pid
else
    echo -e "   ℹ️  未找到前端PID文件"
fi

# 强制清理端口（如果需要）
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "   🔨 清理端口8000..."
    kill $(lsof -t -i:8000) 2>/dev/null || true
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "   🔨 清理端口3000..."
    kill $(lsof -t -i:3000) 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo ""
