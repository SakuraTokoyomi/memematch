#!/bin/bash

# MemeMatch 完整系统一键启动脚本

echo "🚀 MemeMatch 系统启动中..."
echo "================================"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查后端端口
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}⚠️  端口8000已被占用，正在清理...${NC}"
    kill $(lsof -t -i:8000) 2>/dev/null
    sleep 2
fi

# 检查前端端口
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}⚠️  端口3000已被占用，正在清理...${NC}"
    kill $(lsof -t -i:3000) 2>/dev/null
    sleep 2
fi

echo ""
echo -e "${BLUE}📦 步骤1: 启动后端API服务...${NC}"
cd member_b_agent
nohup python api/api_server.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端PID: $BACKEND_PID"
echo "   日志: backend.log"

sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ 后端启动成功！${NC}"
else
    echo -e "${RED}   ❌ 后端启动失败，查看日志: tail backend.log${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🎨 步骤2: 启动前端开发服务器...${NC}"
cd ../member_d_frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端PID: $FRONTEND_PID"
echo "   日志: frontend.log"

echo ""
echo "⏳ 等待前端启动..."
sleep 8

echo ""
echo "================================"
echo -e "${GREEN}🎉 系统启动完成！${NC}"
echo "================================"
echo ""
echo "📍 访问地址:"
echo -e "   ${BLUE}前端界面:${NC} http://localhost:3000"
echo -e "   ${BLUE}后端API:${NC}  http://localhost:8000"
echo -e "   ${BLUE}API文档:${NC}  http://localhost:8000/docs"
echo ""
echo "📊 进程信息:"
echo "   后端PID: $BACKEND_PID"
echo "   前端PID: $FRONTEND_PID"
echo ""
echo "📝 日志文件:"
echo "   后端: tail -f backend.log"
echo "   前端: tail -f frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   或运行: ./stop_all.sh"
echo ""
echo "💡 提示: 在浏览器打开 http://localhost:3000 开始使用"
echo ""

# 保存PID到文件
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

