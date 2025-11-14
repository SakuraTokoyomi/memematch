"""
简单示例：演示如何使用 Meme Agent

使用前请设置环境变量：
export SAMBANOVA_API_KEY="your-api-key"
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.agent_core import create_agent
from agent.config import AgentConfig
from agent.tools import setup_mock_tools


def main():
    """主函数"""
    
    print("=" * 60)
    print("Meme Agent - 简单示例")
    print("=" * 60)
    
    # 1. 获取 API key（优先使用环境变量，否则使用 config 中的默认值）
    api_key = os.getenv("SAMBANOVA_API_KEY")
    if not api_key:
        # 从 config.py 读取默认 API key（不需要实例化，直接使用默认值）
        from agent.config import AgentConfig as DefaultConfig
        # 检查默认值
        import inspect
        sig = inspect.signature(DefaultConfig)
        default_key = sig.parameters['api_key'].default
        if default_key and default_key != inspect.Parameter.empty and default_key != "":
            api_key = default_key
            print("\n✓ 使用 config.py 中配置的默认 API key")
        else:
            print("\n⚠️  警告: 未找到 API key")
            print("请在 config.py 中设置 api_key 默认值或设置环境变量")
            print("\n继续使用 mock 工具进行演示...\n")
    
    # 2. 创建 Agent
    print("\n[1] 创建 Agent...")
    agent = create_agent(
        api_key=api_key if api_key else "demo-key",
        model="Meta-Llama-3.1-8B-Instruct"
    )
    print(f"    模型: Meta-Llama-3.1-8B-Instruct")
    print(f"    API key: {'已配置 ✓' if api_key else '未配置 ✗'}")
    
    # 3. 注册工具（mock 版本）
    print("[2] 注册工具...")
    setup_mock_tools(agent)
    
    # 4. 测试查询
    print("\n[3] 测试查询...\n")
    
    test_queries = [
        "我真的不想努力了",
        "太离谱了",
        "我无语了",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {query}")
        print('='*60)
        
        try:
            if not api_key:
                print("⚠️  跳过（无 API key）")
                continue
            
            # 处理查询
            result = agent.process_query(query, debug=True)
            
            # 打印结果
            print("\n" + "="*60)
            print("结果:")
            print("="*60)
            print(f"状态: {result.get('status')}")
            print(f"Meme 路径: {result.get('meme_path')}")
            print(f"来源: {result.get('source')}")
            print(f"推荐理由: {result.get('explanation')}")
            
            if result.get('candidates'):
                print(f"\n候选 Meme 数量: {len(result['candidates'])}")
                for j, candidate in enumerate(result['candidates'][:3], 1):
                    print(f"  {j}. {candidate.get('image_path')} (score: {candidate.get('score', 0):.2f})")
            
            print(f"\n推理步骤数: {len(result.get('reasoning_steps', []))}")
            for step in result.get('reasoning_steps', []):
                print(f"  步骤 {step['step']}: {step['tool']}({list(step['arguments'].keys())})")
        
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("演示完成!")
    print("="*60)


if __name__ == "__main__":
    main()

