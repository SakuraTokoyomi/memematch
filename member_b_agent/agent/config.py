"""
配置管理模块
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Agent 配置类"""
    
    # SambaNova API 配置
    api_key: str = "9a2266c7-a96a-4459-be90-af5dfc58a655"
    base_url: str = "https://api.sambanova.ai/v1"
    
    # 模型选择
    model: str = "Meta-Llama-3.1-8B-Instruct"
    
    # 推理参数
    temperature: float = 0.7
    max_iterations: int = 6  # 减少到 6 次，避免过多 API 调用
    timeout: int = 30
    
    # 检索阈值
    search_score_threshold: float = 0.6
    
    # 日志级别
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """从环境变量加载配置"""
        # 如果环境变量为空，使用硬编码的默认值
        api_key = os.getenv("SAMBANOVA_API_KEY", "")
        if not api_key:  # 环境变量为空时使用硬编码值
            api_key = "9a2266c7-a96a-4459-be90-af5dfc58a655"
        
        return cls(
            api_key=api_key,
            base_url=os.getenv("SAMBANOVA_BASE_URL", "https://api.sambanova.ai/v1"),
            model=os.getenv("SAMBANOVA_MODEL", "Meta-Llama-3.1-8B-Instruct"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
            max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "10")),
            search_score_threshold=float(os.getenv("SEARCH_SCORE_THRESHOLD", "0.6"))
        )


# 可用的 SambaNova 模型
AVAILABLE_MODELS = {
    "best": {
        "name": "Meta-Llama-3.1-70B-Instruct",
        "description": "最强性能，适合复杂推理",
        "cost": "高"
    },
    "balanced": {
        "name": "Meta-Llama-3.1-8B-Instruct",
        "description": "平衡性能和成本，推荐使用",
        "cost": "中"
    },
    "fast": {
        "name": "Meta-Llama-3.2-3B-Instruct",
        "description": "快速响应，适合简单任务",
        "cost": "低"
    }
}


def get_model_name(tier: str = "balanced") -> str:
    """获取指定级别的模型名称"""
    return AVAILABLE_MODELS.get(tier, AVAILABLE_MODELS["balanced"])["name"]


def print_available_models():
    """打印所有可用模型"""
    print("可用的 SambaNova 模型：")
    print("-" * 60)
    for tier, info in AVAILABLE_MODELS.items():
        print(f"{tier:10} | {info['name']:30} | 成本: {info['cost']}")
        print(f"           | {info['description']}")
        print("-" * 60)

