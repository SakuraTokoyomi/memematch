#!/bin/bash

# MemeMatch 系统停止脚本

echo "🛑 停止 MemeMatch 系统..."

# 读取保存的PID
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "   停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "   停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    rm .frontend.pid
fi

# 强制清理端口
echo "   清理端口..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

sleep 2

echo "✅ 所有服务已停止"

