#!/bin/bash

# 重启后端服务脚本

echo "🔄 重启后端服务..."

# 停止旧服务
echo "   停止旧服务..."
lsof -t -i:8000 | xargs kill -9 2>/dev/null
sleep 2

# 设置DEBUG环境变量
export DEBUG=true
export PYTHONUNBUFFERED=1

# 启动新服务
echo "   启动新服务..."
cd /Applications/MyWorkPlace/7607/memematch/member_b_agent

python api/api_server.py 2>&1 | tee ../backend_debug.log

