# /search/ 模块 (成员 A 交付物)

本模块实现了 Meme Agent 项目的**两路加权混合搜索引擎**。

它负责将原始图片数据和元数据（`content` 描述） 转换为可搜索的向量索引，并提供一个严格符合 API 规范 的 `search_meme()` 函数 供 Agent (成员 B) 调用。

## 核心架构
* **搜索方式**: 两路混合搜索（Two-pass Hybrid Search）。
    * **赛道 1 (权重 1.0)**: 图像搜索 (Image Search)，使用 `clip-ViT-B-32`。
    * **赛道 2 (权重 0.2)**: 文本搜索 (Content Search)，使用 `moka-ai/m3e-base`。
* **融合算法**: **基于分数的融合 (Score Fusion)**。
    * 我们**彻底抛弃**了 RRF（基于排名）的融合，因为那会导致低匹配度搜索（如 "asdf"） 也获得人为的高分（如 0.8）。
    * 现在我们使用 FAISS 返回的**真实分数**（0-1） 进行加权计算，分数是真实的。
* **关键业务逻辑**:
    * `search_meme` 只有在**Top 1 匹配结果的真实分数 > 0.8** (可在 `engine.py` 中配置) 时，才会返回 `success: true`。
    * 否则，它将返回 `success: false` 和错误信息 `Search failed: No results found with score > 0.8`，这正是成员 B 所需要的“检索失败”信号。

## 交付物文件

* `search/config.py`: 配置文件（模型、路径）。
* `search/embedding_builder.py`: **[步骤 1]** 读取 `dataset.csv` 并生成向量 (`.npy`) 和元数据 (`.json`)。
* `search/faiss_index.py`: **[步骤 2]** 读取 `.npy` 文件并构建 `.index` 数据库。
* `search/engine.py`: **[步骤 3]** 你的核心 API `search_meme()`。
* `test_search.py`: **[步骤 4]** 你的单元测试脚本。

## 用法
```bash
## 1. 安装依赖
pip install -r requirements.txt

## 2. 导入函数
from search.engine import search_meme

# 定义查询词
query = "狗"

# 执行调用
results_dict = search_meme(query=query, top_k=3, min_score=0.0)

