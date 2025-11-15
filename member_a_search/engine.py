import faiss
import numpy as np
import json
import os
import time
from sentence_transformers import SentenceTransformer

try:
    from . import config
except ImportError:
    import config

class SearchEngine:
    # ... (init, _load_resources, _get_ranks functions are all correct and unchanged) ...
    def __init__(self):
        print("⚙️ 初始化 *两路混合* 搜索引擎...")
        self.image_model = None
        self.text_model = None
        self.image_index = None
        self.text_index = None
        self.metadata = []
        self.index_size = 0
        self._load_resources()

    def _load_resources(self):
        """加载所有模型、索引和元数据文件"""
        try:
            print(f"🔄 加载图像模型: {config.IMAGE_MODEL_NAME}...")
            self.image_model = SentenceTransformer(config.IMAGE_MODEL_NAME)
            print(f"🔄 加载文本模型: {config.TEXT_MODEL_NAME}...")
            self.text_model = SentenceTransformer(config.TEXT_MODEL_NAME)
            
            print(f"🔄 加载图像索引: {config.IMAGE_FAISS_INDEX_FILE}...")
            self.image_index = faiss.read_index(config.IMAGE_FAISS_INDEX_FILE)
            print(f"🔄 加载文本索引: {config.TEXT_FAISS_INDEX_FILE}...")
            self.text_index = faiss.read_index(config.TEXT_FAISS_INDEX_FILE)
            
            print(f"🔄 加载元数据: {config.METADATA_FILE}...")
            with open(config.METADATA_FILE, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            self.index_size = len(self.metadata)
            print(f"✅ 搜索引擎准备就绪 (共 {self.index_size} 条数据)")
            
        except Exception as e:
            print(f"❌ 加载资源时出错: {e}")
            self.image_index = None # 确保在出错时搜索会失败

    def _get_ranks(self, search_results):
        indices = search_results[1][0]
        return {id_val: rank for rank, id_val in enumerate(indices) if id_val != -1}

    def search_meme_internal(self, query: str, top_k: int, min_score: float) -> dict:
        
        start_time = time.time() 

        if not self.image_index or not self.text_index:
            raise Exception("FAISS index not found or not loaded") 

        SEARCH_K = max(100, top_k * 10) 
        K_CONST = 60
        # (*** 你在你的代码中 将其改为了 0.25, 我保留这个修改 ***)
        CONTENT_WEIGHT = 0.25 

        # ... (搜索、融合、归一化部分 都是正确的，保持不变) ...
        query_vector_image = self.image_model.encode([query])
        faiss.normalize_L2(query_vector_image)
        D_img, I_img = self.image_index.search(query_vector_image, SEARCH_K)
        query_vector_text = self.text_model.encode([query])
        faiss.normalize_L2(query_vector_text)
        D_txt, I_txt = self.text_index.search(query_vector_text, SEARCH_K)
        image_ranks = self._get_ranks((D_img, I_img))
        text_ranks = self._get_ranks((D_txt, I_txt))
        fused_scores = {}
        all_ids = set(image_ranks.keys()) | set(text_ranks.keys())
        max_image_score_part = (1.0 * (1.0 / (K_CONST + 0)))
        max_content_score_part = (CONTENT_WEIGHT * (1.0 / (K_CONST + 0)))
        fused_normalized_scores = {}
        for id_val in all_ids:
            if id_val >= len(self.metadata): continue
            meta = self.metadata[id_val]
            rrf_score = 0.0
            max_possible_rrf_score = 0.0
            rank = image_ranks.get(id_val)
            if rank is not None:
                rrf_score += 1.0 * (1.0 / (K_CONST + rank))
            max_possible_rrf_score += max_image_score_part
            if meta.get('content'):
                rank = text_ranks.get(id_val)
                if rank is not None:
                    rrf_score += CONTENT_WEIGHT * (1.0 / (K_CONST + rank))
                max_possible_rrf_score += max_content_score_part
            normalized_score = (rrf_score / max_possible_rrf_score) if max_possible_rrf_score > 0 else 0.0
            fused_normalized_scores[id_val] = min(normalized_score, 1.0)
        
        sorted_results = sorted(fused_normalized_scores.items(), key=lambda item: item[1], reverse=True)
        
        # --- (*** 核心修正：应用你的新规则 ***) ---
        
        # 1. 仍然先按 API 的 min_score 过滤 (通常是 0.0)
        filtered_by_min_score = [(id_val, score) for id_val, score in sorted_results if score >= min_score]
        
        # 2. 检查：是否找到了任何结果？
        if not filtered_by_min_score:
            raise Exception("Search failed: No results found matching min_score") 

        # 3. 检查：Top 1 的分数是否达标？ (按你的新要求)
        top_1_score = filtered_by_min_score[0][1]
        SCORE_THRESHOLD = 0.8 #
        
        if top_1_score <= SCORE_THRESHOLD:
            raise Exception(f"Search failed: Top 1 result score ({top_1_score:.4f}) is not > {SCORE_THRESHOLD}")

        # 4. 如果 Top 1 达标，则搜索成功。我们从这个列表中取 top_k
        final_candidates = filtered_by_min_score[:top_k]
        
        # --- (*** 修正结束 ***) ---
        
        results_list = []
        for id_val, normalized_score in final_candidates:
            meta = self.metadata[id_val]
            
            results_list.append({
                "image_path": os.path.join(config.IMAGES_DIR, meta['filename']), 
                "score": round(normalized_score, 4),
                "tags": [meta['emotion']] if meta.get('emotion') else [], 
                "metadata": { 
                    "file_size": meta.get('file_size', 0),
                    "dimensions": meta.get('dimensions', [0,0]),
                    "format": meta.get('format', 'unknown')
                }
            })
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results": results_list,
                "total": len(results_list),
                # (*** 修正 'filtered' 的计算逻辑 ***)
                "filtered": len(filtered_by_min_score) - len(final_candidates)
            },
            "metadata": {
                "search_time": time.time() - start_time,
                "index_size": self.index_size,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }

# --- (对外暴露的接口不变) ---
_engine_instance = None
def get_search_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SearchEngine()
    return _engine_instance

def search_meme(query: str, top_k: int = 5, min_score: float = 0.0) -> dict: 
    engine = get_search_engine()
    
    try:
        return engine.search_meme_internal(
            query=query, 
            top_k=top_k, 
            min_score=min_score
        )
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "SEARCH_ERROR"
        }