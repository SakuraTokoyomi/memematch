"""
工具管理模块

提供工具注册、mock 工具等功能
用于开发阶段和与其他成员对接
"""

from typing import Dict, List, Any, Callable
import random
import os


class ToolRegistry:
    """工具注册器"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable, description: str = ""):
        """注册工具"""
        self.tools[name] = func
        if description:
            func.__doc__ = description
        print(f"✓ 工具已注册: {name}")
    
    def get(self, name: str) -> Callable:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有已注册工具"""
        return list(self.tools.keys())


# ========== Mock 工具（用于开发测试） ==========

def mock_search_meme(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Mock 版本的 search_meme
    
    实际由成员 A 提供。这个版本仅用于开发测试。
    
    Args:
        query: 检索关键词
        top_k: 返回结果数量
        
    Returns:
        {
            "query": "...",
            "results": [
                {"image_path": "...", "score": 0.85, "tags": [...]}
            ]
        }
    """
    # 模拟不同情绪的 meme
    mock_database = {
        "tired": [
            {"image_path": "dataset/train/tired_001.jpg", "tags": ["tired", "exhausted", "sleep"]},
            {"image_path": "dataset/train/tired_002.jpg", "tags": ["tired", "no energy"]},
        ],
        "happy": [
            {"image_path": "dataset/train/happy_001.jpg", "tags": ["happy", "smile", "cute"]},
            {"image_path": "dataset/train/happy_002.jpg", "tags": ["joy", "celebrate"]},
        ],
        "surprised": [
            {"image_path": "dataset/train/surprised_001.jpg", "tags": ["shocked", "wow", "omg"]},
            {"image_path": "dataset/train/surprised_002.jpg", "tags": ["surprised", "confused"]},
        ],
        "angry": [
            {"image_path": "dataset/train/angry_001.jpg", "tags": ["angry", "mad", "rage"]},
        ],
        "sad": [
            {"image_path": "dataset/train/sad_001.jpg", "tags": ["sad", "crying", "depressed"]},
        ],
    }
    
    # 简单匹配逻辑
    query_lower = query.lower()
    results = []
    
    for emotion, memes in mock_database.items():
        if emotion in query_lower:
            results.extend(memes)
    
    # 如果没匹配到，返回随机的
    if not results:
        all_memes = []
        for memes in mock_database.values():
            all_memes.extend(memes)
        results = random.sample(all_memes, min(top_k, len(all_memes)))
    
    # 添加模拟的相似度分数
    results_with_score = []
    for i, meme in enumerate(results[:top_k]):
        score = 0.95 - i * 0.1  # 递减的分数
        results_with_score.append({
            "image_path": meme["image_path"],
            "score": score,
            "tags": meme["tags"],
            "metadata": {"source": "mock"}
        })
    
    return {
        "query": query,
        "results": results_with_score,
        "total": len(results_with_score)
    }


def mock_generate_meme(text: str, template: str = "drake") -> Dict[str, Any]:
    """
    Mock 版本的 generate_meme
    
    实际由成员 C 提供。这个版本仅用于开发测试。
    
    Args:
        text: 要显示在 meme 上的文字
        template: 模板类型
        
    Returns:
        {
            "image_path": "...",
            "template": "...",
            "text": "..."
        }
    """
    # 模拟生成的文件路径
    filename = f"generated_{template}_{hash(text) % 10000}.png"
    output_path = f"member_b_agent/outputs/{filename}"
    
    print(f"[Mock] 模拟生成 meme: template={template}, text={text[:20]}...")
    
    return {
        "image_path": output_path,
        "template": template,
        "text": text,
        "status": "success",
        "note": "这是 mock 版本，实际图片由成员 C 生成"
    }


# ========== 工具接口定义（给其他成员参考） ==========

def search_meme_interface(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    search_meme 工具的接口定义
    
    【成员 A 需要实现这个接口】
    
    Args:
        query: 英文检索关键词，例如 "tired reaction meme"
        top_k: 返回结果数量，默认 5
        
    Returns:
        {
            "query": str,           # 查询关键词
            "results": [            # 检索结果列表
                {
                    "image_path": str,      # 图片路径
                    "score": float,         # 相似度分数 (0-1)
                    "tags": List[str],      # 标签列表
                    "metadata": dict        # 其他元数据
                },
                ...
            ],
            "total": int,           # 总结果数
            "search_time": float    # 检索耗时（可选）
        }
    
    注意：
    - results 按 score 从高到低排序
    - score 越接近 1 表示越相关
    - image_path 应该是可访问的文件路径
    """
    raise NotImplementedError("请成员 A 实现此函数")


def generate_meme_interface(text: str, template: str = "drake") -> Dict[str, Any]:
    """
    generate_meme 工具的接口定义
    
    【成员 C 需要实现这个接口】
    
    Args:
        text: 要显示在 meme 上的文字
        template: 模板类型，可选值：
            - "drake": Drake 模板（上下两段对比）
            - "doge": Doge 模板（柴犬）
            - "wojak": Wojak 模板（wojak 表情）
            - "distracted_boyfriend": 分心男友模板
            - "two_buttons": 两个按钮模板
        
    Returns:
        {
            "image_path": str,      # 生成的图片路径
            "template": str,        # 使用的模板
            "text": str,           # 显示的文字
            "status": str,         # "success" 或 "error"
            "generation_time": float  # 生成耗时（可选）
        }
    
    注意：
    - 生成的图片应保存到指定目录
    - 文字应自动换行和调整字号
    - 生成时间尽量控制在 0.5s 以内（模板版）
    """
    raise NotImplementedError("请成员 C 实现此函数")


# ========== 辅助函数 ==========

def setup_mock_tools(agent):
    """
    为 Agent 注册所有 mock 工具
    
    用于开发测试阶段
    
    Args:
        agent: MemeAgent 实例
    """
    agent.register_tool("search_meme", mock_search_meme)
    agent.register_tool("generate_meme", mock_generate_meme)
    print("✓ Mock 工具已全部注册")


def setup_production_tools(agent, search_func: Callable, generate_func: Callable):
    """
    为 Agent 注册生产环境的工具
    
    用于正式运行阶段
    
    Args:
        agent: MemeAgent 实例
        search_func: 成员 A 提供的 search_meme 实现
        generate_func: 成员 C 提供的 generate_meme 实现
    """
    agent.register_tool("search_meme", search_func)
    agent.register_tool("generate_meme", generate_func)
    print("✓ 生产工具已全部注册")


def validate_tool_interface(func: Callable, expected_params: List[str]) -> bool:
    """
    验证工具函数是否符合接口要求
    
    Args:
        func: 要验证的函数
        expected_params: 期望的参数列表
        
    Returns:
        是否符合接口
    """
    import inspect
    
    sig = inspect.signature(func)
    actual_params = list(sig.parameters.keys())
    
    for param in expected_params:
        if param not in actual_params:
            print(f"✗ 缺少参数: {param}")
            return False
    
    print(f"✓ 接口验证通过: {func.__name__}")
    return True

