import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import cn_clip.clip as clip
import torch
from PIL import Image
import os
import json
from . import config

def build_embeddings():
    # 检查设备
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙️ [Builder] 加载 CN-CLIP 模型: {config.MODEL_ARCH} (Device: {device})...")
    
    # 加载 CN-CLIP
    model, preprocess = clip.load_from_name(config.MODEL_ARCH, device=device, download_root='./')
    model.eval()
    
    print(f"🔄 [Builder] 加载文本模型: {config.TEXT_MODEL_NAME}...")
    text_model = SentenceTransformer(config.TEXT_MODEL_NAME)
    
    print(f"📂 读取 CSV: {config.CSV_PATH}")
    try:
        df = pd.read_csv(config.CSV_PATH).fillna({'content': '', 'emotion': ''})
    except Exception as e:
        print(f"❌ CSV 读取失败: {e}")
        return

    valid_image_embeddings = []
    valid_text_embeddings = []
    valid_metadata = []
    
    print("🚀 开始生成向量 (CN-CLIP)...")
    
    for index, row in df.iterrows():
        filename = str(row['filename'])
        content = str(row['content'])
        emotion = str(row['emotion'])
        img_path = os.path.join(config.IMAGES_DIR, filename)
        
        if not os.path.exists(img_path):
            continue
            
        try:
            # CN-CLIP 图像预处理
            image = preprocess(Image.open(img_path)).unsqueeze(0).to(device)
            with torch.no_grad():
                image_features = model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True) # 归一化
                
            image_emb = image_features.cpu().numpy()[0]
            text_emb = text_model.encode(content)
            
            valid_image_embeddings.append(image_emb)
            valid_text_embeddings.append(text_emb)
            
            valid_metadata.append({
                "id": len(valid_metadata),
                "filename": filename,
                "content": content,
                "emotion": emotion,
                "file_size": os.path.getsize(img_path)
            })
            
            if len(valid_metadata) % 100 == 0:
                print(f"✅ 已处理 {len(valid_metadata)} 张")
                
        except Exception as e:
            print(f"❌ 错误 {filename}: {e}")

    if valid_metadata:
        np.save(config.IMAGE_EMBEDDING_FILE, np.array(valid_image_embeddings).astype('float32'))
        np.save(config.TEXT_EMBEDDING_FILE, np.array(valid_text_embeddings).astype('float32'))
        with open(config.METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(valid_metadata, f, ensure_ascii=False, indent=2)
        print("💾 向量生成完毕！")
    else:
        print("❌ 未生成任何数据")

if __name__ == "__main__":
    build_embeddings()