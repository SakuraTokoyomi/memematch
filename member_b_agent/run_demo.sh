#!/bin/bash
# Meme Agent 演示脚本

echo "=========================================="
echo "🤖 Meme Agent - 快速演示"
echo "=========================================="
echo ""

# 检查 API key
if [ -z "$SAMBANOVA_API_KEY" ]; then
    echo "⚠️  警告: 未设置 SAMBANOVA_API_KEY"
    echo ""
    echo "请先设置环境变量："
    echo "  export SAMBANOVA_API_KEY='your-api-key'"
    echo ""
    echo "或者在代码中直接指定 API key"
    echo ""
fi

# 检查依赖
echo "📦 检查依赖..."
pip list | grep -q openai
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

echo ""
echo "选择运行模式："
echo "  1) 简单示例"
echo "  2) 交互式命令行"
echo "  3) 运行测试"
echo ""

read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "运行简单示例..."
        python examples/simple_demo.py
        ;;
    2)
        echo ""
        echo "启动交互式命令行..."
        python examples/interactive_demo.py
        ;;
    3)
        echo ""
        echo "运行测试..."
        pytest tests/ -v
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

