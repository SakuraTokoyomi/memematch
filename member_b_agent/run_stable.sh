#!/bin/bash
# 运行稳定版交互式 Demo

cd "$(dirname "$0")"

echo "🚀 启动 Meme Agent（稳定版）"
echo "================================"
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在"
    exit 1
fi

# 运行稳定版
python examples/interactive_demo_stable.py
