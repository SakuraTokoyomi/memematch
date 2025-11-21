import faiss
import numpy as np
from . import config
import os

def build_faiss_index(embedding_file_path, index_file_path, index_name=""):
    """
    通用的 FAISS 索引构建函数
    """
    if not os.path.exists(embedding_file_path):
        print(f"❌ 未找到 {index_name} 向量文件: {embedding_file_path}")
        return False
    print(f"📂 正在加载 {index_name} 向量: {embedding_file_path}...")
    embeddings = np.load(embedding_file_path)
    if embeddings.shape[0] == 0:
        print(f"❌ {index_name} 向量文件为空。")
        return False
    dimension = embeddings.shape[1]
    print(f"📊 向量维度: {dimension}, 数据量: {embeddings.shape[0]}")
    print("🔄 正在 L2 归一化向量 (用于余弦相似度)...")
    faiss.normalize_L2(embeddings)
    print("⚙️ 正在构建 FAISS 索引 (IndexFlatIP)...")
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    # --- 关键：确保文件写入磁盘 ---
    try:
        print(f"💾 正在保存 {index_name} 索引至: {index_file_path}")
        faiss.write_index(index, index_file_path)
        print(f"✅ {index_name} 索引构建完成！")
        return True
    except Exception as e:
        print(f"❌❌❌ 写入 FAISS 索引失败: {e} ❌❌❌")
        return False

def build_all_indexes():
    """
    构建所有索引
    """
    print("--- 1/2 开始构建图像索引 (Image Index) ---")
    img_success = build_faiss_index(
        embedding_file_path=config.IMAGE_EMBEDDING_FILE,
        index_file_path=config.IMAGE_FAISS_INDEX_FILE,
        index_name="图像"
    )
    
    print("\n--- 2/2 开始构建文本索引 (Text/Content Index) ---")
    txt_success = build_faiss_index(
        embedding_file_path=config.TEXT_EMBEDDING_FILE,
        index_file_path=config.TEXT_FAISS_INDEX_FILE,
        index_name="文本"
    )
    
    if img_success and txt_success:
        print("\n✅ 所有索引构建完成！")
        return True  # <--- 必须加上这一行！
    else:
        print("\n❌ 索引构建失败。")
        return False # <--- 加上这一行！

if __name__ == "__main__":
    build_all_indexes()