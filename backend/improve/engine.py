import faiss
import numpy as np
import json
import os
import time
import torch
import cn_clip.clip as clip
from sentence_transformers import SentenceTransformer

try:
    from . import config
except ImportError:
    import config

class SearchEngine:
    def __init__(self):
        print("⚙️ 初始化 CN-CLIP 强力搜索引擎 (RRF融合版)...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model = None # CN-CLIP
        self.text_model = None # M3E
        self.image_index = None
        self.text_index = None
        self.metadata = []
        self.index_size = 0
        self._load_resources()

    def _load_resources(self):
        """加载资源：CN-CLIP + M3E + FAISS"""
        try:
            print(f"🔄 加载 CN-CLIP 模型: {config.MODEL_ARCH} (Device: {self.device})...")
            # download_root='./' 防止重复下载
            self.clip_model, _ = clip.load_from_name(config.MODEL_ARCH, device=self.device, download_root='./')
            self.clip_model.eval()
            
            print(f"🔄 加载内容模型: {config.TEXT_MODEL_NAME}...")
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
            print(f"❌ 加载资源失败: {e}")
            self.image_index = None

    def _get_ranks(self, I_result):
        """将 FAISS 索引矩阵转换为 {id: rank} 字典"""
        # I_result[0] 是 Top-K 的 ID 列表
        return {id_val: rank for rank, id_val in enumerate(I_result[0]) if id_val != -1}

    def search_meme_internal(self, query: str, top_k: int, min_score: float) -> dict:
        # 🔍 [Log] 打印输入参数 (保留你要求的详细日志)
        print(f"\n{'='*60}")
        print(f"🔍 [search_meme_internal] 输入参数:")
        print(f"   query: '{query}'")
        print(f"   top_k: {top_k}")
        print(f"   min_score: {min_score}")
        print(f"{'='*60}\n")

        start_time = time.time()
        
        if not self.image_index or not self.text_index:
            raise Exception("FAISS index not loaded")

        # --- 1. 定义参数 ---
        SEARCH_K = max(100, top_k * 10)
        K_CONST = 60
        CONTENT_WEIGHT = 0.2

        # --- 2. CN-CLIP 图像路搜索 (中文 Query -> CN-CLIP -> Image Features) ---
        text = clip.tokenize([query]).to(self.device)
        with torch.no_grad():
            query_features = self.clip_model.encode_text(text)
            query_features /= query_features.norm(dim=-1, keepdim=True)
        
        query_vector_image = query_features.cpu().numpy().astype('float32')
        D_img, I_img = self.image_index.search(query_vector_image, SEARCH_K)

        # --- 3. M3E 文本路搜索 (中文 Query -> M3E -> Content Features) ---
        query_vector_text = self.text_model.encode([query])
        faiss.normalize_L2(query_vector_text)
        D_txt, I_txt = self.text_index.search(query_vector_text, SEARCH_K)

        # --- 4. 准备 Rank 数据 ---
        image_ranks = self._get_ranks(I_img)
        text_ranks = self._get_ranks(I_txt)
        all_ids = set(image_ranks.keys()) | set(text_ranks.keys())

        # --- 5. RRF 融合计算 ---
        # 计算理论最大分 (分母)
        max_image_score_part = (1.0 * (1.0 / (K_CONST + 0)))
        max_content_score_part = (CONTENT_WEIGHT * (1.0 / (K_CONST + 0)))
        
        fused_normalized_scores = {}
        
        # 调试：打印 Top 1 的排名情况
        if I_img[0][0] != -1:
            top_img_id = I_img[0][0]
            print(f"🔍 [Debug] 图像路第1名 ID: {top_img_id} (Rank 0)")
        else:
            print(f"🔍 [Debug] 图像路未找到结果")

        for id_val in all_ids:
            if id_val >= len(self.metadata): continue
            meta = self.metadata[id_val]
            
            rrf_score = 0.0
            # 基础分母至少包含图像部分
            max_possible = max_image_score_part 
            
            # --- 图像路得分 ---
            rank = image_ranks.get(id_val)
            if rank is not None:
                rrf_score += 1.0 * (1.0 / (K_CONST + rank))
            
            # --- 文本路得分 ---
            if meta.get('content'):
                max_possible += max_content_score_part
                rank = text_ranks.get(id_val)
                if rank is not None:
                    rrf_score += CONTENT_WEIGHT * (1.0 / (K_CONST + rank))
            
            # 归一化
            normalized = (rrf_score / max_possible) if max_possible > 0 else 0.0
            fused_normalized_scores[id_val] = min(normalized, 1.0)
        
        # 排序
        sorted_results = sorted(fused_normalized_scores.items(), key=lambda item: item[1], reverse=True)
        
        # [Log] 打印排名分析
        if sorted_results:
            top_id, top_score = sorted_results[0]
            img_rank = image_ranks.get(top_id, "没进前100")
            txt_rank = text_ranks.get(top_id, "没进前100")
            print(f"🧐 [分析] 最终第1名 (ID: {top_id}) 得分: {top_score:.4f}")
            print(f"    - 图像排名: {img_rank} (如果是60左右，分数就是0.4)")
            print(f"    - 文本排名: {txt_rank}")

        # --- 6. 过滤 & 组装 (按照你要求的指定结构) ---
        final_candidates = []
        filtered_count = 0
        
        for id_val, score in sorted_results:
            # 阈值过滤
            if score < min_score:
                filtered_count += 1
                continue
            
            # 收集 Top-K
            if len(final_candidates) < top_k:
                meta = self.metadata[id_val]
                final_candidates.append({
                    "image_path": os.path.join(config.IMAGES_DIR, meta['filename']),
                    "score": round(score, 4),
                    "tags": [meta['emotion']] if meta.get('emotion') else [],
                    "metadata": {
                        "file_size": meta.get('file_size', 0),
                        "dimensions": meta.get('dimensions', [0,0]),
                        "format": meta.get('format', 'unknown')
                    }
                })

        # 构建返回结果
        result = {
            "success": True,
            "data": {
                "query": query,
                "results": final_candidates,
                "total": len(final_candidates),
                "filtered": filtered_count
            },
            "metadata": {
                "search_time": time.time() - start_time,
                "index_size": self.index_size
            }
        }

        # 📤 [Log] 打印输出结果 (保留你要求的详细日志)
        print(f"\n{'='*60}")
        print(f"📤 [search_meme_internal] 输出结果:")
        print(f"   success: {result['success']}")
        print(f"   total_results: {result['data']['total']}")
        print(f"   search_time: {result['metadata']['search_time']:.4f}s")
        if result['data']['results']:
            print(f"   Top-1:")
            top1 = result['data']['results'][0]
            print(f"      - path: {top1['image_path']}")
            print(f"      - score: {top1['score']}")
            print(f"      - tags: {top1['tags']}")
        print(f"{'='*60}\n")

        return result

# --- 单例与接口 ---
_engine_instance = None
def get_search_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SearchEngine()
    return _engine_instance

def search_meme(query: str, top_k: int = 5, min_score: float = 0.0) -> dict:
    return get_search_engine().search_meme_internal(query, top_k, min_score)