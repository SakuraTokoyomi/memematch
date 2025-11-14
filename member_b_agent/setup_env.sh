#!/bin/bash
# 快速设置环境变量脚本

# 加载 .env 文件中的环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ 环境变量已从 .env 文件加载"
    echo ""
    echo "已设置的变量："
    echo "  SAMBANOVA_API_KEY: ${SAMBANOVA_API_KEY:0:20}..."
    echo "  SAMBANOVA_MODEL: $SAMBANOVA_MODEL"
    echo "  AGENT_MAX_ITERATIONS: $AGENT_MAX_ITERATIONS"
else
    echo "❌ 未找到 .env 文件"
    exit 1
fi

