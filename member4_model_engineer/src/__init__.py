"""
MemeMatch 模型工程师模块
负责文本表示模型的评估、选型与向量导出
"""

__version__ = "0.1.0"
__author__ = "Member 4 - Model Engineer"

from .model_evaluator import MemeModelEvaluator
from .embedding_exporter import EmbeddingExporter
from .utils import load_data, compute_metrics, save_results

__all__ = [
    "MemeModelEvaluator",
    "EmbeddingExporter",
    "load_data",
    "compute_metrics",
    "save_results",
]


