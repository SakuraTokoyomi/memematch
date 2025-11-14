"""
交互式示例（稳定版）：带错误重试和更好的错误处理
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.agent_core import create_agent
from agent.tools import setup_mock_tools


def query_with_retry(agent, user_input, max_retries=2, debug=False):
    """
    带重试的查询函数
    
    Args:
        agent: Agent 实例
        user_input: 用户输入
        max_retries: 最大重试次数
        debug: 是否显示调试信息
        
    Returns:
        查询结果
    """
    for attempt in range(max_retries):
        try:
            result = agent.process_query(user_input, max_iterations=4, debug=debug)
            
            # 如果成功，直接返回
            if result.get('status') == 'success':
                return result
            
            # 如果是 API 错误，重试
            if 'API' in result.get('error', '') or '500' in result.get('error', ''):
                if attempt < max_retries - 1:
                    print(f"\n⚠️  API 错误，{2 ** attempt} 秒后重试...")
                    time.sleep(2 ** attempt)
                    continue
            
            # 其他错误，直接返回
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"\n⚠️  错误: {e}")
                print(f"   {2 ** attempt} 秒后重试...")
                time.sleep(2 ** attempt)
            else:
                return {
                    "error": str(e),
                    "status": "error"
                }
    
    return {
        "error": "重试失败",
        "status": "error"
    }


def main():
    """交互式主函数"""
    
    print("=" * 60)
    print("🎭 Meme Agent - 交互式命令行（稳定版）")
    print("=" * 60)
    
    # 检查 API key
    api_key = os.getenv("SAMBANOVA_API_KEY")
    if not api_key:
        # 从 config 获取
        from agent.config import AgentConfig as DefaultConfig
        import inspect
        sig = inspect.signature(DefaultConfig)
        default_key = sig.parameters['api_key'].default
        if default_key and default_key != inspect.Parameter.empty and default_key != "":
            api_key = default_key
            print("\n✓ 使用 config.py 中的 API key")
        else:
            print("\n⚠️  未检测到 SAMBANOVA_API_KEY")
            print("将使用 Mock 工具（本地模拟）")
            api_key = None
    
    # 创建 Agent
    print("\n初始化 Agent...")
    agent = create_agent(api_key=api_key if api_key else "demo-key")
    setup_mock_tools(agent)
    print("✓ Agent 已就绪\n")
    
    print("提示：")
    print("  - 输入你想表达的情绪或想要的 meme")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'debug' 切换调试模式")
    print()
    
    if not api_key:
        print("⚠️  注意: 当前使用 Mock 工具，不会调用真实 API")
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
            
            # 处理查询（带重试）
            print("\n🤖 Agent 正在思考...")
            
            if api_key:
                # 使用真实 API，带重试
                result = query_with_retry(agent, user_input, max_retries=2, debug=debug_mode)
            else:
                # Mock 模式，无需重试
                result = agent.process_query(user_input, max_iterations=3, debug=debug_mode)
            
            # 显示结果
            print("\n" + "-" * 60)
            
            if result.get('status') == 'error':
                print(f"❌ 错误: {result.get('error')}")
                print("\n💡 建议:")
                print("  1. 等待几秒后重试")
                print("  2. 输入更简单的查询")
                print("  3. 如果频繁失败，API 可能不稳定")
            else:
                print(f"🎨 Meme: {result.get('meme_path')}")
                print(f"💬 {result.get('explanation')}")
                
                if result.get('source'):
                    print(f"📍 来源: {result['source']}")
                
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
            print("可以继续输入其他查询")


if __name__ == "__main__":
    main()

