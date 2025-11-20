#!/bin/bash

# ===================================================================
# MemeMatch V2.0 完整系统一键启动脚本
# ===================================================================
# 
# 功能：
# - 自动检查系统环境（Python 3.11+, Node.js 18+）
# - 自动创建Python虚拟环境
# - 自动安装所有模块依赖（成员A, B, C）
# - 自动安装前端npm依赖（成员D）
# - 检查数据集和模型文件
# - 启动后端API服务（端口8000）
# - 启动前端开发服务器（端口3000）
#
# 使用方法：
#   ./start_all.sh
#
# 停止服务：
#   ./stop_all.sh 或 kill $(cat .backend.pid .frontend.pid)
#
# ===================================================================

echo "🚀 MemeMatch V2.0 系统启动中..."
echo "================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 前置检查：Python和Node.js
echo -e "${BLUE}🔍 检查系统环境...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到Python3，请先安装Python 3.11+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}   ✅ Python $PYTHON_VERSION${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 未找到Node.js，请先安装Node.js${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}   ✅ Node.js $NODE_VERSION${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 未找到npm，请先安装npm${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}   ✅ npm $NPM_VERSION${NC}"

echo ""

# 检查数据集和关键文件
echo -e "${BLUE}📁 检查项目文件...${NC}"

MISSING_FILES=0

if [ ! -f "dataset/memeWithEmo.csv" ]; then
    echo -e "${RED}   ❌ 数据集文件不存在: dataset/memeWithEmo.csv${NC}"
    MISSING_FILES=1
fi

if [ ! -d "dataset/meme" ]; then
    echo -e "${RED}   ❌ 梗图目录不存在: dataset/meme${NC}"
    MISSING_FILES=1
fi

if [ ! -f "member_a_search/output/image.index" ] || [ ! -f "member_a_search/output/text.index" ]; then
    echo -e "${YELLOW}   ⚠️  向量索引文件不存在，首次运行会自动构建（可能需要几分钟）${NC}"
fi

if [ $MISSING_FILES -eq 1 ]; then
    echo -e "${RED}   ❌ 缺少必要文件，请检查项目结构${NC}"
    exit 1
fi

echo -e "${GREEN}   ✅ 项目文件检查通过${NC}"
echo ""

# 检查API Key（可选）
if [ -z "$SAMBANOVA_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  未设置 SAMBANOVA_API_KEY 环境变量${NC}"
    echo -e "${YELLOW}   将使用默认API Key（可能有限流）${NC}"
    echo ""
fi

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
echo -e "${BLUE}📦 步骤1: 检查并安装搜索引擎依赖（成员A）...${NC}"
cd member_a_search

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "   🔨 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "   📥 安装/更新搜索引擎依赖..."
source venv/bin/activate
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ 搜索引擎依赖安装完成${NC}"
else
    echo -e "${RED}   ❌ 搜索引擎依赖安装失败${NC}"
    exit 1
fi
deactivate

echo ""
echo -e "${BLUE}📦 步骤2: 检查并安装后端Agent依赖（成员B）...${NC}"
cd ../member_b_agent

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "   🔨 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "   📥 安装/更新后端依赖..."
source venv/bin/activate
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ 后端Agent依赖安装完成${NC}"
else
    echo -e "${RED}   ❌ 后端Agent依赖安装失败${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📦 步骤3: 检查并安装生成引擎依赖（成员C）...${NC}"
cd ../member_c_generate

# 检查虚拟环境（如果有requirements.txt）
if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "   🔨 创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    echo "   📥 安装/更新生成引擎依赖..."
    source venv/bin/activate
    pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✅ 生成引擎依赖安装完成${NC}"
    else
        echo -e "${RED}   ❌ 生成引擎依赖安装失败${NC}"
        exit 1
    fi
    deactivate
else
    echo -e "${GREEN}   ✅ 生成引擎无需额外依赖${NC}"
fi

# 确保输出目录存在
mkdir -p outputs
echo -e "${GREEN}   ✅ 输出目录已准备${NC}"

echo ""
echo -e "${BLUE}🚀 步骤4: 启动后端API服务...${NC}"
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
echo -e "${BLUE}🎨 步骤5: 检查并安装前端依赖（成员D）...${NC}"
cd ../member_d_frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "   📥 安装前端依赖（首次可能较慢）..."
    npm install
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✅ 前端依赖安装完成${NC}"
    else
        echo -e "${RED}   ❌ 前端依赖安装失败${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}   ✅ 前端依赖已存在，跳过安装${NC}"
fi

echo ""
echo -e "${BLUE}🎨 步骤6: 启动前端开发服务器...${NC}"
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端PID: $FRONTEND_PID"
echo "   日志: frontend.log"

echo ""
echo "⏳ 等待前端启动..."
sleep 8

echo ""
echo "================================"
echo -e "${GREEN}🎉 MemeMatch V2.0 系统启动完成！${NC}"
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
echo "💡 使用提示:"
echo "   1. 在浏览器打开 http://localhost:3000"
echo "   2. 输入你的心情（如：今天好开心）"
echo "   3. 系统会自动：识别情绪 → 搜索梗图 → 返回结果"
echo "   4. 如果检索不满意，会自动生成个性化梗图"
echo ""
echo "🏗️  系统架构 V2.0:"
echo "   用户输入 → LLM情绪识别 → 查询融合 → 向量检索 → 判断score → 生成/返回"
echo ""
echo "📚 更多文档:"
echo "   - PROJECT_REPORT.md - 完整项目报告"
echo "   - ARCHITECTURE_V2.md - 新架构说明"
echo "   - QUERY_FUSION_STRATEGY.md - 查询融合策略"
echo ""

# 保存PID到文件
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

