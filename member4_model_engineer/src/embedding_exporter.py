"""
向量导出器
负责将表情包描述编码为向量并导出，供检索系统（成员3）使用
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer


class EmbeddingExporter:
    """
    向量导出器
    
    功能：
    1. 加载最佳模型
    2. 批量编码表情包描述
    3. 导出向量文件（.npy格式）
    4. 导出元数据（ID映射、文本等）
    """
    
    def __init__(self, model_name_or_path: str):
        """
        初始化导出器
        
        Args:
            model_name_or_path: 模型名称或路径
        """
        self.model_name = model_name_or_path
        print(f"🔄 加载模型: {model_name_or_path}")
        self.model = SentenceTransformer(model_name_or_path)
        print(f"✅ 模型加载成功!")
    
    def export_meme_embeddings(self,
                              meme_data_path: str,
                              output_dir: str,
                              batch_size: int = 32):
        """
        导出表情包向量
        
        Args:
            meme_data_path: 表情包JSON文件路径
            output_dir: 输出目录
            batch_size: 批处理大小
        """
        print(f"\n📦 开始导出向量...")
        print(f"   输入: {meme_data_path}")
        print(f"   输出: {output_dir}")
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. 加载表情包数据
        print("📖 加载表情包数据...")
        with open(meme_data_path, 'r', encoding='utf-8') as f:
            memes = json.load(f)
        
        # 2. 构建描述文本
        meme_ids = []
        meme_texts = []
        meme_labels = []
        
        for meme in memes:
            meme_ids.append(meme['id'])
            meme_labels.append(meme['label'])
            
            # 组合：标签 + 关键词 + 描述
            keywords = ' '.join(meme.get('keywords', []))
            description = meme.get('description', '')
            text = f"{meme['label']} {keywords} {description}".strip()
            meme_texts.append(text)
        
        print(f"   表情包数量: {len(meme_ids)}")
        
        # 3. 编码向量
        print("🔢 编码向量...")
        embeddings = self.model.encode(
            meme_texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"   向量形状: {embeddings.shape}")
        print(f"   向量维度: {embeddings.shape[1]}")
        
        # 4. 保存向量文件
        embeddings_file = output_path / "meme_embeddings.npy"
        np.save(embeddings_file, embeddings.astype(np.float32))
        print(f"✅ 向量已保存: {embeddings_file}")
        
        # 5. 保存ID映射
        ids_file = output_path / "meme_ids.json"
        with open(ids_file, 'w', encoding='utf-8') as f:
            json.dump(meme_ids, f, ensure_ascii=False, indent=2)
        print(f"✅ ID映射已保存: {ids_file}")
        
        # 6. 保存文本列表（方便调试）
        texts_file = output_path / "meme_texts.txt"
        with open(texts_file, 'w', encoding='utf-8') as f:
            for meme_id, label, text in zip(meme_ids, meme_labels, meme_texts):
                f.write(f"{meme_id}\t{label}\t{text}\n")
        print(f"✅ 文本列表已保存: {texts_file}")
        
        # 7. 保存元数据
        metadata = {
            "model_name": self.model_name,
            "num_memes": len(meme_ids),
            "embedding_dimension": int(embeddings.shape[1]),
            "dtype": "float32",
            "files": {
                "embeddings": "meme_embeddings.npy",
                "ids": "meme_ids.json",
                "texts": "meme_texts.txt"
            },
            "usage": {
                "python": {
                    "load_embeddings": "embeddings = np.load('meme_embeddings.npy')",
                    "load_ids": "ids = json.load(open('meme_ids.json'))"
                },
                "description": "供成员3（检索系统工程师）使用"
            }
        }
        
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"✅ 元数据已保存: {metadata_file}")
        
        # 8. 输出使用说明
        print(f"\n{'='*60}")
        print(f"✅ 向量导出完成!")
        print(f"{'='*60}")
        print(f"📁 输出文件:")
        print(f"   - {embeddings_file.name}  (向量数据)")
        print(f"   - {ids_file.name}  (ID映射)")
        print(f"   - {texts_file.name}  (文本列表)")
        print(f"   - {metadata_file.name}  (元数据)")
        print(f"\n💡 使用方法（供成员3）:")
        print(f"   import numpy as np")
        print(f"   import json")
        print(f"   embeddings = np.load('{embeddings_file}')")
        print(f"   with open('{ids_file}') as f:")
        print(f"       meme_ids = json.load(f)")
        print(f"{'='*60}\n")
        
        return embeddings, meme_ids, meme_texts
    
    def export_query_embeddings(self,
                               query_texts: List[str],
                               query_ids: List[str],
                               output_file: str):
        """
        导出查询向量（可选，用于缓存）
        
        Args:
            query_texts: 查询文本列表
            query_ids: 查询ID列表
            output_file: 输出文件路径
        """
        print(f"📝 编码查询向量...")
        embeddings = self.model.encode(
            query_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # 保存
        np.save(output_file, embeddings.astype(np.float32))
        
        # 保存ID映射
        ids_file = output_file.replace('.npy', '_ids.json')
        with open(ids_file, 'w', encoding='utf-8') as f:
            json.dump(query_ids, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 查询向量已保存: {output_file}")
        return embeddings

