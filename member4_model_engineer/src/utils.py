"""
工具函数模块
提供数据加载、指标计算、结果保存等通用功能
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
import yaml


def load_config(config_path: str = "config/models.yaml") -> Dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_meme_data(meme_path: str) -> Tuple[List[str], List[str], List[str]]:
    """
    加载表情包数据
    
    Args:
        meme_path: 表情包JSON文件路径
        
    Returns:
        (meme_ids, meme_texts, meme_labels)
    """
    with open(meme_path, 'r', encoding='utf-8') as f:
        memes = json.load(f)
    
    meme_ids = []
    meme_texts = []
    meme_labels = []
    
    for meme in memes:
        meme_ids.append(meme['id'])
        meme_labels.append(meme['label'])
        
        # 组合标签和关键词作为描述文本
        keywords = ' '.join(meme.get('keywords', []))
        description = meme.get('description', '')
        text = f"{meme['label']} {keywords} {description}".strip()
        meme_texts.append(text)
    
    return meme_ids, meme_texts, meme_labels


def load_query_data(query_path: str, split: str = 'test') -> Tuple[List[str], List[str]]:
    """
    加载查询数据
    
    Args:
        query_path: 查询JSON文件路径
        split: 'train' 或 'test'
        
    Returns:
        (query_ids, query_texts)
    """
    with open(query_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    queries = data.get(split, [])
    query_ids = [q['id'] for q in queries]
    query_texts = [q['text'] for q in queries]
    
    return query_ids, query_texts


def load_ground_truth(query_path: str, split: str = 'test') -> Dict[str, List[str]]:
    """
    加载标注答案
    
    Args:
        query_path: 包含ground_truth的JSON文件路径
        split: 'train' 或 'test'
        
    Returns:
        {query_id: [meme_ids]}
    """
    with open(query_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ground_truth = data.get('ground_truth', {}).get(split, {})
    return ground_truth


def compute_recall_at_k(predictions: np.ndarray, 
                        ground_truth: Dict[str, List[str]], 
                        query_ids: List[str],
                        meme_ids: List[str],
                        k: int) -> float:
    """
    计算 Recall@k
    
    Args:
        predictions: 相似度矩阵 (n_queries, n_memes)
        ground_truth: 标注答案字典
        query_ids: 查询ID列表
        meme_ids: 表情包ID列表
        k: Top-k
        
    Returns:
        recall@k 分数
    """
    recalls = []
    
    for query_idx, query_id in enumerate(query_ids):
        # 获取标注的正确答案
        relevant_memes = ground_truth.get(query_id, [])
        if not relevant_memes:
            continue
        
        # 获取Top-k预测
        top_k_indices = np.argsort(predictions[query_idx])[-k:][::-1]
        top_k_meme_ids = [meme_ids[i] for i in top_k_indices]
        
        # 计算命中数
        hits = len(set(top_k_meme_ids) & set(relevant_memes))
        recall = hits / len(relevant_memes)
        recalls.append(recall)
    
    return np.mean(recalls) if recalls else 0.0


def compute_mrr(predictions: np.ndarray,
                ground_truth: Dict[str, List[str]],
                query_ids: List[str],
                meme_ids: List[str]) -> float:
    """
    计算 Mean Reciprocal Rank (MRR)
    
    Args:
        predictions: 相似度矩阵
        ground_truth: 标注答案字典
        query_ids: 查询ID列表
        meme_ids: 表情包ID列表
        
    Returns:
        MRR 分数
    """
    mrrs = []
    
    for query_idx, query_id in enumerate(query_ids):
        relevant_memes = ground_truth.get(query_id, [])
        if not relevant_memes:
            continue
        
        # 获取排序后的预测
        ranked_indices = np.argsort(predictions[query_idx])[::-1]
        
        # 找到第一个相关结果的位置
        for rank, idx in enumerate(ranked_indices, 1):
            if meme_ids[idx] in relevant_memes:
                mrrs.append(1.0 / rank)
                break
    
    return np.mean(mrrs) if mrrs else 0.0


def compute_metrics(predictions: np.ndarray,
                    ground_truth: Dict[str, List[str]],
                    query_ids: List[str],
                    meme_ids: List[str]) -> Dict[str, float]:
    """
    计算所有评估指标
    
    Returns:
        包含各项指标的字典
    """
    metrics = {
        'recall@1': compute_recall_at_k(predictions, ground_truth, query_ids, meme_ids, k=1),
        'recall@3': compute_recall_at_k(predictions, ground_truth, query_ids, meme_ids, k=3),
        'recall@5': compute_recall_at_k(predictions, ground_truth, query_ids, meme_ids, k=5),
        'mrr': compute_mrr(predictions, ground_truth, query_ids, meme_ids)
    }
    
    return metrics


def save_results(results: List[Dict[str, Any]], output_path: str):
    """
    保存评估结果为CSV
    
    Args:
        results: 结果列表
        output_path: 输出文件路径
    """
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"✅ 结果已保存至: {output_path}")


def load_data(data_dir: str = "data", 
              meme_file: str = "memes.json",
              query_file: str = "queries_sample.json",
              split: str = "test") -> Tuple:
    """
    一站式数据加载函数
    
    Args:
        data_dir: 数据目录
        meme_file: 表情包文件名
        query_file: 查询文件名
        split: 数据集划分
        
    Returns:
        (meme_ids, meme_texts, query_ids, query_texts, ground_truth)
    """
    data_path = Path(data_dir)
    
    # 加载表情包
    meme_ids, meme_texts, _ = load_meme_data(str(data_path / meme_file))
    
    # 加载查询
    query_ids, query_texts = load_query_data(str(data_path / query_file), split)
    
    # 加载标注
    ground_truth = load_ground_truth(str(data_path / query_file), split)
    
    print(f"📊 数据加载完成:")
    print(f"   - 表情包数量: {len(meme_ids)}")
    print(f"   - 查询数量: {len(query_ids)} ({split} set)")
    print(f"   - 标注对数: {len(ground_truth)}")
    
    return meme_ids, meme_texts, query_ids, query_texts, ground_truth


def format_report(model_name: str, metrics: Dict[str, float], inference_time: float = None) -> str:
    """
    格式化评估报告
    
    Args:
        model_name: 模型名称
        metrics: 指标字典
        inference_time: 推理时间（可选）
        
    Returns:
        格式化的报告字符串
    """
    report = f"\n{'='*60}\n"
    report += f"模型: {model_name}\n"
    report += f"{'='*60}\n"
    report += f"Recall@1: {metrics['recall@1']:.4f}\n"
    report += f"Recall@3: {metrics['recall@3']:.4f}\n"
    report += f"Recall@5: {metrics['recall@5']:.4f}\n"
    report += f"MRR:      {metrics['mrr']:.4f}\n"
    
    if inference_time:
        report += f"推理时间: {inference_time:.3f}s\n"
    
    report += f"{'='*60}\n"
    
    return report


