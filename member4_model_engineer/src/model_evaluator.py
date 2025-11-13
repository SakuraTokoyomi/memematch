"""
模型评估器
负责加载句向量模型、编码文本、计算相似度、评估性能
"""

import numpy as np
import time
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import compute_metrics


class MemeModelEvaluator:
    """
    表情包匹配模型评估器
    
    核心功能：
    1. 加载预训练句向量模型
    2. 编码文本为向量
    3. 计算语义相似度
    4. 评估检索性能（Recall@k, MRR）
    """
    
    def __init__(self, model_name: str, device: str = None):
        """
        初始化评估器
        
        Args:
            model_name: HuggingFace模型名称或本地路径
            device: 'cpu', 'cuda', 'mps' 或 None（自动选择）
        """
        self.model_name = model_name
        print(f"🔄 正在加载模型: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name, device=device)
            print(f"✅ 模型加载成功!")
            print(f"   设备: {self.model.device}")
            print(f"   向量维度: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            raise
    
    def encode_texts(self, texts: List[str], batch_size: int = 32, 
                     show_progress: bool = True) -> np.ndarray:
        """
        编码文本为向量
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
            show_progress: 是否显示进度条
            
        Returns:
            向量矩阵 (n_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings
    
    def compute_similarity(self, query_embeddings: np.ndarray, 
                          meme_embeddings: np.ndarray) -> np.ndarray:
        """
        计算查询与表情包之间的相似度
        
        Args:
            query_embeddings: 查询向量 (n_queries, dim)
            meme_embeddings: 表情包向量 (n_memes, dim)
            
        Returns:
            相似度矩阵 (n_queries, n_memes)
        """
        similarities = cosine_similarity(query_embeddings, meme_embeddings)
        return similarities
    
    def evaluate(self, 
                 query_texts: List[str],
                 meme_texts: List[str],
                 ground_truth: Dict[str, List[str]],
                 query_ids: List[str],
                 meme_ids: List[str]) -> Tuple[Dict[str, float], np.ndarray, np.ndarray, float]:
        """
        完整评估流程
        
        Args:
            query_texts: 查询文本列表
            meme_texts: 表情包描述文本列表
            ground_truth: 标注答案 {query_id: [meme_ids]}
            query_ids: 查询ID列表
            meme_ids: 表情包ID列表
            
        Returns:
            (metrics, query_embeddings, meme_embeddings, inference_time)
        """
        print(f"\n🔬 开始评估模型: {self.model_name}")
        print(f"   查询数量: {len(query_texts)}")
        print(f"   表情包数量: {len(meme_texts)}")
        
        # 1. 编码表情包（只需一次）
        print("📝 编码表情包描述...")
        start_time = time.time()
        meme_embeddings = self.encode_texts(meme_texts, show_progress=False)
        meme_time = time.time() - start_time
        
        # 2. 编码查询
        print("📝 编码查询句子...")
        start_time = time.time()
        query_embeddings = self.encode_texts(query_texts, show_progress=False)
        query_time = time.time() - start_time
        
        total_time = meme_time + query_time
        print(f"⏱️  编码耗时: {total_time:.3f}s")
        print(f"   - 表情包: {meme_time:.3f}s ({len(meme_texts)/meme_time:.1f} 句/秒)")
        print(f"   - 查询: {query_time:.3f}s ({len(query_texts)/query_time:.1f} 句/秒)")
        
        # 3. 计算相似度
        print("🔢 计算相似度矩阵...")
        similarities = self.compute_similarity(query_embeddings, meme_embeddings)
        
        # 4. 计算指标
        print("📊 计算评估指标...")
        metrics = compute_metrics(similarities, ground_truth, query_ids, meme_ids)
        
        return metrics, query_embeddings, meme_embeddings, total_time
    
    def get_top_k_predictions(self,
                             query_text: str,
                             meme_texts: List[str],
                             meme_ids: List[str],
                             k: int = 3) -> List[Tuple[str, float]]:
        """
        获取单个查询的Top-k预测
        
        Args:
            query_text: 查询文本
            meme_texts: 表情包描述列表
            meme_ids: 表情包ID列表
            k: 返回Top-k个结果
            
        Returns:
            [(meme_id, similarity_score), ...]
        """
        # 编码
        query_emb = self.encode_texts([query_text], show_progress=False)[0]
        meme_embs = self.encode_texts(meme_texts, show_progress=False)
        
        # 计算相似度
        similarities = cosine_similarity([query_emb], meme_embs)[0]
        
        # 获取Top-k
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        results = [(meme_ids[i], similarities[i]) for i in top_k_indices]
        
        return results
    
    def get_embedding_dimension(self) -> int:
        """获取向量维度"""
        return self.model.get_sentence_embedding_dimension()
    
    def save_model(self, output_path: str):
        """
        保存模型（如果是微调后的模型）
        
        Args:
            output_path: 输出路径
        """
        self.model.save(output_path)
        print(f"✅ 模型已保存至: {output_path}")


