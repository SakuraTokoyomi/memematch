import os

# --- 1. 基础路径配置 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'dataset')

# --- 2. 输入数据路径 ---
CSV_PATH = os.path.join(DATA_DIR, 'memeWithEmo.csv')
IMAGES_DIR = os.path.join(DATA_DIR, 'meme') 

# --- 3. 输出文件路径 ---
OUTPUT_DIR = os.path.join(BASE_DIR, 'search', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True) 

# --- 4. 模型配置 ---
IMAGE_MODEL_NAME = 'clip-ViT-B-32'
TEXT_MODEL_NAME = 'moka-ai/m3e-base' # M3E 只需要处理 content

# --- 5. 混合搜索索引文件 ---
# 图像索引
IMAGE_EMBEDDING_FILE = os.path.join(OUTPUT_DIR, 'image_embeddings.npy')
METADATA_FILE = os.path.join(OUTPUT_DIR, 'metadata.json') # 元数据是共用的
IMAGE_FAISS_INDEX_FILE = os.path.join(OUTPUT_DIR, 'image.index')

# 文本索引 (Content)
TEXT_EMBEDDING_FILE = os.path.join(OUTPUT_DIR, 'text_embeddings.npy')
TEXT_FAISS_INDEX_FILE = os.path.join(OUTPUT_DIR, 'text.index')

# (Emotion 索引已彻底移除)