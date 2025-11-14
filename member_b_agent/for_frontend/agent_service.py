"""
Meme Agent 服务 - 前端集成专用

这是前端同学需要导入的唯一文件！
"""

import os
import sys

# 添加项目路径（自动处理）
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from agent.agent_core import create_agent
from agent.tools import setup_mock_tools


class MemeAgentService:
    """
    Meme Agent 服务类
    
    这是前端唯一需要使用的类，封装了所有 Agent 功能
    
    使用示例：
        agent = MemeAgentService()
        result = agent.query("我太累了")
        
        if result["success"]:
            print(result["meme_path"])
            print(result["explanation"])
    """
    
    def __init__(self, use_mock=True, verbose=False):
        """
        初始化 Agent 服务
        
        参数：
            use_mock (bool): 是否使用模拟数据
                - True: 使用模拟数据（开发/测试）
                - False: 使用真实数据（正式环境）
            verbose (bool): 是否显示详细日志
                - False: 简洁输出（推荐）
                - True: 显示所有技术日志（调试用）
        """
        # 隐藏技术性日志
        if not verbose:
            import logging
            logging.getLogger("agent.agent_core").setLevel(logging.WARNING)
            logging.getLogger("httpx").setLevel(logging.WARNING)
            logging.getLogger("openai").setLevel(logging.WARNING)
        
        # 创建 Agent
        self.agent = create_agent(
            api_key=os.getenv("SAMBANOVA_API_KEY", "your-default-key"),
            model="Meta-Llama-3.1-8B-Instruct"
        )
        
        # 注册工具
        if use_mock:
            setup_mock_tools(self.agent)
        else:
            # TODO: 等待成员 A 和 C 完成后，替换为真实工具
            # from member_a_search import search_meme
            # from member_c_generate import generate_meme
            # from agent.tools import setup_production_tools
            # setup_production_tools(self.agent, search_meme, generate_meme)
            setup_mock_tools(self.agent)  # 暂时使用 mock
    
    def query(self, user_input: str, max_iterations: int = 4):
        """
        处理用户查询（核心方法）
        
        参数：
            user_input (str): 用户输入的文本
                例如："我太累了"、"开心"、"无语"
            max_iterations (int): 最大推理次数（一般不用改）
        
        返回：
            dict: 结果字典
            
            成功时：
            {
                "success": True,
                "meme_path": "图片路径",
                "explanation": "推荐理由",
                "source": "search" 或 "generated",
                "candidates": [...]  # 可选：其他候选
            }
            
            失败时：
            {
                "success": False,
                "error": "错误描述"
            }
        
        使用示例：
            result = agent.query("我太累了")
            if result["success"]:
                显示图片(result["meme_path"])
                显示文字(result["explanation"])
            else:
                显示错误(result["error"])
        """
        try:
            # 调用 Agent
            result = self.agent.process_query(
                user_input, 
                max_iterations=max_iterations
            )
            
            # 标准化输出格式（方便前端使用）
            if result.get("status") == "success":
                return {
                    "success": True,
                    "meme_path": result.get("meme_path"),
                    "explanation": result.get("explanation"),
                    "candidates": result.get("candidates", []),
                    "source": result.get("source", "unknown")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "未知错误")
                }
        
        except Exception as e:
            # 捕获所有异常，返回友好的错误信息
            return {
                "success": False,
                "error": f"系统错误: {str(e)}"
            }


# ============ 测试代码 ============

def run_test():
    """
    测试 Agent 是否正常工作
    
    运行方式：
        python agent_service.py
    """
    print("=" * 60)
    print("🎭 Meme Agent 服务测试")
    print("=" * 60)
    print()
    
    # 初始化
    print("初始化 Agent...")
    agent = MemeAgentService(use_mock=True, verbose=False)
    print("✓ 初始化完成")
    print()
    
    # 测试查询
    test_cases = [
        "我太累了",
        "开心",
        "无语"
    ]
    
    for query in test_cases:
        print(f"测试: {query}")
        result = agent.query(query)
        
        if result["success"]:
            print(f"  ✓ 成功")
            print(f"  Meme: {result['meme_path']}")
            print(f"  理由: {result['explanation'][:50]}...")
            print(f"  来源: {result['source']}")
        else:
            print(f"  ✗ 失败: {result['error']}")
        print()
    
    print("=" * 60)
    print("测试完成！")
    print()
    print("📖 使用方法：")
    print("""
    from agent_service import MemeAgentService
    
    agent = MemeAgentService()
    result = agent.query("用户输入")
    
    if result["success"]:
        # 显示 meme
        print(result["meme_path"])
        print(result["explanation"])
    else:
        # 显示错误
        print(result["error"])
    """)


if __name__ == "__main__":
    run_test()

