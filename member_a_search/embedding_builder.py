import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from PIL import Image
import os
import json
from . import config # 相对导入

def build_embeddings():
    print(f"🔄 正在加载图像模型: {config.IMAGE_MODEL_NAME} ...")
    image_model = SentenceTransformer(config.IMAGE_MODEL_NAME)
    
    print(f"🔄 正在加载文本模型: {config.TEXT_MODEL_NAME} ...")
    text_model = SentenceTransformer(config.TEXT_MODEL_NAME)
    
    print(f"📂 正在读取 CSV: {config.CSV_PATH}")
    try:
        df = pd.read_csv(config.CSV_PATH).fillna({'content': '', 'emotion': ''})
    except Exception as e:
        print(f"❌ 读取 CSV 失败: {e}")
        return

    valid_image_embeddings = []
    valid_text_embeddings = []
    valid_metadata = []
    
    print("🚀 开始处理图片和文本 (两路混合)...")
    
    for index, row in df.iterrows():
        filename = str(row['filename'])
        content = str(row['content']) 
        emotion = str(row['emotion'])
        img_path = os.path.join(config.IMAGES_DIR, filename)
        
        if not os.path.exists(img_path):
            print(f"⚠️ 跳过丢失的图片: {filename}")
            continue
            
        try:
            image = Image.open(img_path)
            file_size = os.path.getsize(img_path) #
            dimensions = image.size # (width, height)
            img_format = image.format or 'JPEG' #
            
            image_emb = image_model.encode(image)
            text_emb = text_model.encode(content)
            
            valid_image_embeddings.append(image_emb)
            valid_text_embeddings.append(text_emb)
            
            current_id = len(valid_metadata) 
            valid_metadata.append({
                "id": current_id,
                "filename": filename,
                "content": content,
                "emotion": emotion,
                "file_size": file_size,
                "dimensions": dimensions,
                "format": img_format
            })
            
            if (current_id + 1) % 100 == 0:
                print(f"✅ 已处理 {current_id + 1} 张图片")
                
        except Exception as e:
            print(f"❌ 处理 {filename} 出错: {e}")

    if valid_metadata:
        image_embeddings_array = np.array(valid_image_embeddings).astype('float32')
        np.save(config.IMAGE_EMBEDDING_FILE, image_embeddings_array)
        print(f"\n💾 图像向量已保存: {config.IMAGE_EMBEDDING_FILE}, {image_embeddings_array.shape}")
        
        text_embeddings_array = np.array(valid_text_embeddings).astype('float32')
        np.save(config.TEXT_EMBEDDING_FILE, text_embeddings_array)
        print(f"💾 文本向量已保存: {config.TEXT_EMBEDDING_FILE}, {text_embeddings_array.shape}")
        
        with open(config.METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(valid_metadata, f, ensure_ascii=False, indent=2)
        print(f"💾 元数据已保存: {config.METADATA_FILE}")
    else:
        print("❌ 未生成任何有效向量。")

if __name__ == "__main__":
    build_embeddings()