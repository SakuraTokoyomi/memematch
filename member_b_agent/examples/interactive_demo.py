"""
交互式示例：命令行交互式使用 Meme Agent
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.agent_core import create_agent
from agent.tools import setup_mock_tools


def main():
    """交互式主函数"""
    
    print("=" * 60)
    print("🎭 Meme Agent - 交互式命令行")
    print("=" * 60)
    
    # 检查 API key
    api_key = os.getenv("SAMBANOVA_API_KEY")
    if not api_key:
        print("\n⚠️  未检测到 SAMBANOVA_API_KEY")
        print("请设置环境变量后重试")
        return
    
    # 创建 Agent
    print("\n初始化 Agent...")
    agent = create_agent(api_key=api_key)
    setup_mock_tools(agent)
    print("✓ Agent 已就绪\n")
    
    print("提示：")
    print("  - 输入你想表达的情绪或想要的 meme")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'debug' 切换调试模式")
    print()
    
    debug_mode = False
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n🧑 你: ").strip()
            
            if not user_input:
                continue
            
            # 特殊命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n再见! 👋")
                break
            
            if user_input.lower() == 'debug':
                debug_mode = not debug_mode
                print(f"\n调试模式: {'开启' if debug_mode else '关闭'}")
                continue
            
            # 处理查询
            print("\n🤖 Agent 正在思考...")
            result = agent.process_query(user_input, debug=debug_mode)
            
            # 显示结果
            print("\n" + "-" * 60)
            
            if result.get('status') == 'error':
                print(f"❌ 错误: {result.get('error')}")
            else:
                print(f"🎨 Meme: {result.get('meme_path')}")
                print(f"💬 {result.get('explanation')}")
                
                if debug_mode and result.get('reasoning_steps'):
                    print(f"\n🔍 推理步骤:")
                    for step in result['reasoning_steps']:
                        print(f"  {step['step']}. {step['tool']}")
            
            print("-" * 60)
        
        except KeyboardInterrupt:
            print("\n\n再见! 👋")
            break
        
        except Exception as e:
            print(f"\n❌ 出错了: {e}")


if __name__ == "__main__":
    main()

