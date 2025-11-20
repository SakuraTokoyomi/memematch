#!/bin/bash

# ===================================================================
# MemeMatch 统一启动脚本
# 适用于重构后的目录结构
# ===================================================================

set -e  # 遇到错误立即退出

echo "🚀 MemeMatch 启动中..."
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 进入项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo -e "${BLUE}📂 项目根目录: $PROJECT_ROOT${NC}"
echo ""

# 创建日志目录
mkdir -p logs

# ============ 后端启动 ============

echo -e "${BLUE}🔧 步骤1: 启动后端服务...${NC}"

# 检查后端目录
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ backend目录不存在，请先运行重构脚本${NC}"
    exit 1
fi

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}   创建Python虚拟环境...${NC}"
    python3.11 -m venv venv || python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（如果需要）
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}   安装后端依赖（首次可能较慢）...${NC}"
    pip install --upgrade pip -q
    
    # 检查requirements.txt
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q
    else
        echo -e "${RED}❌ 未找到requirements.txt${NC}"
        exit 1
    fi
    
    touch venv/.installed
    echo -e "${GREEN}   ✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}   ✅ 依赖已安装${NC}"
fi

# 检查端口占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}   ⚠️  端口8000已被占用，正在清理...${NC}"
    kill $(lsof -t -i:8000) 2>/dev/null || true
    sleep 2
fi

# 启动后端
echo -e "${BLUE}   启动后端API服务...${NC}"
nohup python api/api_server.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid

deactivate
cd "$PROJECT_ROOT"

# 等待后端启动（需要加载模型，可能较慢）
echo -e "${YELLOW}   等待后端启动（加载模型中...）${NC}"

# 循环检查健康状态（最多等待30秒）
MAX_WAIT=30
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ 后端服务已启动 (PID: $BACKEND_PID, 耗时: ${WAITED}秒)${NC}"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    if [ $WAITED -eq 10 ]; then
        echo -e "${YELLOW}   ⏳ 仍在启动中...${NC}"
    fi
done

# 最终检查
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}   ❌ 后端启动超时，查看日志: tail -f logs/backend.log${NC}"
    echo -e "${YELLOW}   提示: 后端可能仍在启动中，请稍后手动检查${NC}"
    # 不退出，继续启动前端
fi

echo ""

# ============ 前端启动 ============

echo -e "${BLUE}🎨 步骤2: 启动前端服务...${NC}"

# 检查前端目录（兼容新旧结构）
FRONTEND_DIR=""
if [ -d "frontend" ]; then
    FRONTEND_DIR="frontend"
elif [ -d "member_d_frontend" ]; then
    FRONTEND_DIR="member_d_frontend"
else
    echo -e "${RED}❌ 未找到前端目录${NC}"
    exit 1
fi

cd "$FRONTEND_DIR"

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   安装前端依赖（首次可能较慢）...${NC}"
    npm install
    echo -e "${GREEN}   ✅ 前端依赖安装完成${NC}"
else
    echo -e "${GREEN}   ✅ 前端依赖已安装${NC}"
fi

# 检查端口占用
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}   ⚠️  端口3000已被占用，正在清理...${NC}"
    kill $(lsof -t -i:3000) 2>/dev/null || true
    sleep 2
fi

# 启动前端
echo -e "${BLUE}   启动前端开发服务器...${NC}"
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

cd "$PROJECT_ROOT"

# 等待前端启动
echo -e "${YELLOW}   等待前端启动...${NC}"
sleep 5

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
echo "   后端: tail -f logs/backend.log"
echo "   前端: tail -f logs/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   运行: ./scripts/stop.sh"
echo ""
echo "💡 提示: 在浏览器打开 http://localhost:3000 开始使用"
echo ""
