#!/bin/bash
# 快速测试脚本

echo "🎭 Meme Agent - 快速测试"
echo "================================"
echo ""

# 检查虚拟环境
if [ -d "../venv" ]; then
    echo "激活虚拟环境..."
    source ../venv/bin/activate
fi

# 运行测试
echo "运行测试..."
echo ""
python agent_service.py

echo ""
echo "================================"
echo "✓ 测试完成！"
echo ""
echo "下一步："
echo "  • 阅读 README.md"
echo "  • 查看 examples/ 中的完整示例"
echo "  • 开始集成到你的应用"
