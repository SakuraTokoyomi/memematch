import os

# --- 路径配置 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'dataset')
CSV_PATH = os.path.join(DATA_DIR, 'memeWithEmo.csv')
IMAGES_DIR = os.path.join(DATA_DIR, 'meme') 
OUTPUT_DIR = os.path.join(BASE_DIR, 'search', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True) 

# --- 模型配置 (CN-CLIP) ---
# 使用 ViT-B-16 追求最高精度 (这是分数能高的关键)
MODEL_ARCH = "ViT-B-16"

# 文本模型 (保持不变)
TEXT_MODEL_NAME = 'moka-ai/m3e-base'

# --- 索引文件路径 ---
IMAGE_EMBEDDING_FILE = os.path.join(OUTPUT_DIR, 'image_embeddings.npy')
METADATA_FILE = os.path.join(OUTPUT_DIR, 'metadata.json')
IMAGE_FAISS_INDEX_FILE = os.path.join(OUTPUT_DIR, 'image.index')
TEXT_EMBEDDING_FILE = os.path.join(OUTPUT_DIR, 'text_embeddings.npy')
TEXT_FAISS_INDEX_FILE = os.path.join(OUTPUT_DIR, 'text.index')