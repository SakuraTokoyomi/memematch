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

def mock_search_meme_v2(query: str, top_k: int = 5, min_score: float = 0.0, **kwargs) -> Dict[str, Any]:
    """
    Mock 版本的 search_meme（优化版 v2.0）
    
    实际由成员 A 提供。这个版本仅用于开发测试。
    
    Args:
        query: 检索关键词
        top_k: 返回结果数量
        min_score: 最小分数阈值（0-1）
        
    Returns:
        {
            "success": bool,        # 是否成功
            "data": {
                "query": str,
                "results": [...],
                "total": int,
                "filtered": int     # 被过滤的数量
            },
            "metadata": {           # 元数据
                "search_time": float,
                "index_size": int,
                "timestamp": str
            }
        }
    """
    import time
    start_time = time.time()
    
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
    
    try:
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
        
        # 添加模拟的相似度分数并应用过滤
        results_with_score = []
        filtered_count = 0
        
        for i, meme in enumerate(results[:top_k]):
            score = 0.95 - i * 0.1  # 递减的分数
            
            if score >= min_score:  # 应用分数过滤
                results_with_score.append({
                    "image_path": meme["image_path"],
                    "score": score,
                    "tags": meme["tags"],
                    "metadata": {
                        "source": "mock",
                        "file_size": 102400,
                        "dimensions": [512, 512],
                        "format": "jpg"
                    }
                })
            else:
                filtered_count += 1
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results": results_with_score,
                "total": len(results_with_score),
                "filtered": filtered_count
            },
            "metadata": {
                "search_time": round(time.time() - start_time, 3),
                "index_size": sum(len(memes) for memes in mock_database.values()),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "MOCK_SEARCH_ERROR",
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }


def mock_search_meme(query: str, top_k: int = 5, min_score: float = 0.0, **kwargs) -> Dict[str, Any]:
    """
    Mock 版本的 search_meme（v2.0 格式）
    
    实际由成员 A 提供。这个版本仅用于开发测试。
    
    Args:
        query: 检索关键词
        top_k: 返回结果数量
        min_score: 最小分数阈值（0-1）
        
    Returns:
        {
            "success": bool,        # 是否成功
            "data": {
                "query": str,
                "results": [...],
                "total": int,
                "filtered": int     # 被过滤的数量
            },
            "metadata": {           # 元数据
                "search_time": float,
                "index_size": int,
                "timestamp": str
            }
        }
    """
    # 直接调用 v2 版本
    return mock_search_meme_v2(query, top_k, min_score, **kwargs)


def mock_generate_meme_v2(text: str, template: str = "drake", options: Dict = None) -> Dict[str, Any]:
    """
    Mock 版本的 generate_meme（优化版 v2.0）
    
    实际由成员 C 提供。这个版本仅用于开发测试。
    
    Args:
        text: 要显示在 meme 上的文字
        template: 模板类型
        options: 生成选项（字体、颜色等）
        
    Returns:
        {
            "success": bool,        # 是否成功
            "data": {
                "image_path": str,
                "template": str,
                "text": str,
                "dimensions": [w, h],
                "file_size": int,
                "format": str
            },
            "metadata": {
                "generation_time": float,
                "template_version": str,
                "parameters_used": dict,
                "timestamp": str
            }
        }
    """
    import time
    start_time = time.time()
    
    # 支持的模板列表
    valid_templates = ["drake", "doge", "wojak", "distracted_boyfriend", "two_buttons"]
    
    try:
        if template not in valid_templates:
            return {
                "success": False,
                "error": f"Template '{template}' not found",
                "error_code": "TEMPLATE_NOT_FOUND",
                "metadata": {
                    "available_templates": valid_templates,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                }
            }
        
        # 模拟生成的文件路径
        filename = f"generated_{template}_{hash(text) % 10000}.png"
        output_path = f"member_b_agent/outputs/{filename}"
        
        # 处理选项
        if options is None:
            options = {}
        font_size = options.get("font_size", 32)
        font_family = options.get("font_family", "Arial")
        output_format = options.get("output_format", "png")
        
        print(f"[Mock] 模拟生成 meme: template={template}, text={text[:20]}...")
        
        return {
            "success": True,
            "data": {
                "image_path": output_path,
                "template": template,
                "text": text,
                "dimensions": [600, 600],
                "file_size": 85000,
                "format": output_format
            },
            "metadata": {
                "generation_time": round(time.time() - start_time, 3),
                "template_version": "1.0",
                "parameters_used": {
                    "font_size": font_size,
                    "font_family": font_family
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "note": "这是 mock 版本，实际图片由成员 C 生成"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "MOCK_GENERATION_ERROR",
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }


def mock_generate_meme(text: str, template: str = "drake", options: Dict = None, **kwargs) -> Dict[str, Any]:
    """
    Mock 版本的 generate_meme（v2.0 格式）
    
    实际由成员 C 提供。这个版本仅用于开发测试。
    
    Args:
        text: 要显示在 meme 上的文字
        template: 模板类型
        options: 生成选项（字体、颜色等）
        
    Returns:
        {
            "success": bool,        # 是否成功
            "data": {
                "image_path": str,
                "template": str,
                "text": str,
                "dimensions": [w, h],
                "file_size": int,
                "format": str
            },
            "metadata": {
                "generation_time": float,
                "template_version": str,
                "parameters_used": dict,
                "timestamp": str
            }
        }
    """
    # 直接调用 v2 版本
    return mock_generate_meme_v2(text, template, options)


# ========== 工具接口定义（给其他成员参考） ==========

def search_meme_interface(query: str, top_k: int = 5, min_score: float = 0.0) -> Dict[str, Any]:
    """
    search_meme 工具的接口定义（v2.0）
    
    【成员 A 需要实现这个接口】
    
    Args:
        query: 英文检索关键词，例如 "tired reaction meme"
        top_k: 返回结果数量，默认 5
        min_score: 最小相似度阈值 (0-1)，默认 0.0
        
    Returns:
        {
            "success": bool,        # 是否成功
            "data": {
                "query": str,       # 查询关键词
                "results": [        # 检索结果列表
                    {
                        "image_path": str,      # 图片路径
                        "score": float,         # 相似度分数 (0-1)
                        "tags": List[str],      # 标签列表
                        "metadata": {           # 文件元数据
                            "file_size": int,
                            "dimensions": [w, h],
                            "format": str
                        }
                    },
                    ...
                ],
                "total": int,       # 返回的结果数
                "filtered": int     # 被过滤的数量
            },
            "metadata": {
                "search_time": float,      # 检索耗时（秒）
                "index_size": int,         # 索引总数
                "timestamp": str           # 时间戳
            }
        }
    
    失败时返回:
        {
            "success": False,
            "error": str,              # 错误描述
            "error_code": str          # 错误代码
        }
    
    注意：
    - results 按 score 从高到低排序
    - score 越接近 1 表示越相关
    - image_path 应该是可访问的文件路径
    - min_score 可以过滤低分结果
    """
    raise NotImplementedError("请成员 A 实现此函数")


def generate_meme_interface(text: str, template: str = "drake", options: Dict = None) -> Dict[str, Any]:
    """
    generate_meme 工具的接口定义（v2.0）
    
    【成员 C 需要实现这个接口】
    
    Args:
        text: 要显示在 meme 上的文字
        template: 模板类型，可选值：
            - "drake": Drake 模板（上下两段对比）
            - "doge": Doge 模板（柴犬）
            - "wojak": Wojak 模板（wojak 表情）
            - "distracted_boyfriend": 分心男友模板
            - "two_buttons": 两个按钮模板
        options: 生成选项（可选），可包含：
            - "font_size": int      # 字体大小
            - "font_family": str    # 字体名称
            - "text_color": str     # 文字颜色（hex）
            - "output_format": str  # 输出格式（png/jpg）
        
    Returns:
        {
            "success": bool,        # 是否成功
            "data": {
                "image_path": str,      # 生成的图片路径
                "template": str,        # 使用的模板
                "text": str,           # 显示的文字
                "dimensions": [w, h],   # 图片尺寸
                "file_size": int,       # 文件大小（字节）
                "format": str          # 文件格式
            },
            "metadata": {
                "generation_time": float,      # 生成耗时（秒）
                "template_version": str,       # 模板版本
                "parameters_used": dict,       # 实际使用的参数
                "timestamp": str              # 时间戳
            }
        }
    
    失败时返回:
        {
            "success": False,
            "error": str,              # 错误描述
            "error_code": str,         # 错误代码
            "metadata": {
                "available_templates": List[str]  # 可用的模板列表
            }
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


# ========== 接口适配器（向后兼容） ==========

def adapt_search_result_to_v1(result_v2: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 v2 格式的搜索结果转换为 v1 格式
    
    用于向后兼容旧版接口
    
    Args:
        result_v2: v2 格式的结果 {"success": bool, "data": {...}, "metadata": {...}}
        
    Returns:
        v1 格式的结果 {"query": str, "results": [...], "total": int}
    """
    if result_v2.get("success"):
        data = result_v2["data"]
        return {
            "query": data["query"],
            "results": data["results"],
            "total": data["total"]
        }
    else:
        # 失败时返回空结果
        return {
            "query": "",
            "results": [],
            "total": 0,
            "error": result_v2.get("error", "Unknown error")
        }


def adapt_generate_result_to_v1(result_v2: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 v2 格式的生成结果转换为 v1 格式
    
    用于向后兼容旧版接口
    
    Args:
        result_v2: v2 格式的结果 {"success": bool, "data": {...}, "metadata": {...}}
        
    Returns:
        v1 格式的结果 {"image_path": str, "template": str, "text": str, "status": str}
    """
    if result_v2.get("success"):
        data = result_v2["data"]
        return {
            "image_path": data["image_path"],
            "template": data["template"],
            "text": data["text"],
            "status": "success"
        }
    else:
        return {
            "status": "error",
            "error": result_v2.get("error", "Unknown error")
        }


def create_v2_wrapper(func_v1: Callable, tool_type: str) -> Callable:
    """
    为 v1 格式的函数创建 v2 格式的包装器
    
    当成员 A/C 提供的是旧版格式函数时，自动适配为 v2 格式
    
    Args:
        func_v1: 旧版格式的函数
        tool_type: 工具类型（"search" 或 "generate"）
        
    Returns:
        v2 格式的包装函数
    """
    import time
    
    def wrapper_search(query: str, top_k: int = 5, **kwargs):
        """Search wrapper for v2 format"""
        start_time = time.time()
        try:
            result_v1 = func_v1(query, top_k)
            return {
                "success": True,
                "data": {
                    "query": result_v1.get("query", query),
                    "results": result_v1.get("results", []),
                    "total": result_v1.get("total", 0),
                    "filtered": 0
                },
                "metadata": {
                    "search_time": round(time.time() - start_time, 3),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "adapted_from": "v1"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SEARCH_ERROR"
            }
    
    def wrapper_generate(text: str, template: str = "drake", **kwargs):
        """Generate wrapper for v2 format"""
        start_time = time.time()
        try:
            result_v1 = func_v1(text, template)
            if result_v1.get("status") == "success":
                return {
                    "success": True,
                    "data": {
                        "image_path": result_v1["image_path"],
                        "template": result_v1.get("template", template),
                        "text": result_v1.get("text", text),
                        "dimensions": [600, 600],
                        "file_size": 0,
                        "format": "png"
                    },
                    "metadata": {
                        "generation_time": round(time.time() - start_time, 3),
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "adapted_from": "v1"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result_v1.get("error", "Generation failed"),
                    "error_code": "GENERATION_ERROR"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "GENERATION_ERROR"
            }
    
    if tool_type == "search":
        return wrapper_search
    elif tool_type == "generate":
        return wrapper_generate
    else:
        raise ValueError(f"Unknown tool type: {tool_type}")

