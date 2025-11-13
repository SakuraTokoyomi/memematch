# 成员4：模型工程师 - 工作目录

## 📋 职责概述

负责 MemeMatch 项目的核心文本表示模型，包括：
- 句向量模型选型与零样本评估
- 向量导出接口（供成员3检索系统使用）
- 可选：对比学习微调

---

## 🚀 快速开始

### 1. 环境安装

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**预计安装时间**：5-10分钟（取决于网络速度）

### 2. 准备数据

**⚠️ 重要：等待成员2提供数据**

将成员2提供的数据放入 `data/` 目录：
- `data/memes.json` - 表情包库（150-200个）
- `data/queries_train.json` - 训练查询句子
- `data/queries_test.json` - 测试查询句子
- `data/ground_truth.json` - 标注的正确答案

数据格式说明见：`data/README.md`

**暂时可以使用示例数据测试**：
- `data/memes_sample.json`
- `data/queries_sample.json`

### 3. 运行模型评估（阶段一核心任务）

```bash
# 对比多个模型性能
python scripts/01_compare_models.py

# 输出：outputs/model_comparison.csv + 控制台报告
```

### 4. 导出最佳模型的向量

```bash
# 导出表情包向量（供成员3使用）
python scripts/02_export_embeddings.py --model paraphrase-multilingual-MiniLM-L12-v2

# 输出：
# - outputs/meme_embeddings.npy
# - outputs/meme_ids.json
# - outputs/meme_texts.txt
```

---

## 📂 目录结构

```
member4_model_engineer/
├── README.md                    # 本文档
├── requirements.txt             # Python依赖
├── config/
│   └── models.yaml             # 模型配置（待评估的模型列表）
├── data/                        # 数据目录 [等待成员2]
│   ├── README.md               # 数据格式说明
│   ├── memes_sample.json       # 示例：表情包数据
│   ├── queries_sample.json     # 示例：查询数据
│   ├── memes.json              # [待填充] 完整表情包库
│   ├── queries_train.json      # [待填充] 训练集
│   ├── queries_test.json       # [待填充] 测试集
│   └── ground_truth.json       # [待填充] 标注答案
├── src/
│   ├── __init__.py
│   ├── model_evaluator.py      # 核心：模型评估器
│   ├── embedding_exporter.py   # 向量导出器
│   └── utils.py                # 工具函数
├── scripts/
│   ├── 01_compare_models.py    # 脚本：模型对比实验
│   └── 02_export_embeddings.py # 脚本：导出向量
├── outputs/                     # 输出目录
│   ├── model_comparison.csv    # [生成] 模型对比结果
│   ├── meme_embeddings.npy     # [生成] 表情包向量
│   └── evaluation_report.txt   # [生成] 详细评估报告
└── models/                      # 模型缓存目录
    └── (自动下载的预训练模型)
```

---

## 🎯 阶段一任务清单

### Week 1（当前）

- [x] 搭建项目结构
- [ ] **等待成员2提供数据**（预计1-2天）
- [ ] 运行模型对比实验（`01_compare_models.py`）
- [ ] 选出最佳模型并记录结果
- [ ] 导出向量文件给成员3
- [ ] 撰写模型选型报告（1页）

### 交付物

1. **代码**：`src/` 和 `scripts/` 中的所有脚本
2. **数据**：`outputs/meme_embeddings.npy`（向量文件）
3. **报告**：`outputs/model_comparison.csv` + 分析说明

---

## 📊 模型候选列表

已在 `config/models.yaml` 中配置了以下模型：

| 模型名称 | 语言支持 | 维度 | 参数量 | 特点 |
|---------|---------|------|-------|------|
| `paraphrase-multilingual-MiniLM-L12-v2` | 多语言 | 384 | 118M | 轻量高效 |
| `distiluse-base-multilingual-cased-v2` | 多语言 | 512 | 135M | 平衡性能 |
| `shibing624/text2vec-base-chinese` | 中文 | 768 | 102M | 中文优化 |
| `moka-ai/m3e-base` | 中文 | 768 | 102M | 中文场景 |

**评估标准**：
- Recall@1, Recall@3, Recall@5
- MRR (Mean Reciprocal Rank)
- 推理速度（句/秒）

---

## 🤝 协作接口

### 输入（从成员2获取）

```json
// data/memes.json 格式
[
  {
    "id": "meme_001",
    "label": "黑人问号",
    "keywords": ["困惑", "啥意思", "???", "不理解"],
    "image_path": "images/meme_001.jpg"
  }
]

// data/queries_test.json 格式
[
  {
    "id": "query_001",
    "text": "这是什么鬼操作",
    "emotion": "困惑"
  }
]

// data/ground_truth.json 格式
{
  "query_001": ["meme_001", "meme_023"],
  "query_002": ["meme_045"]
}
```

### 输出（给成员3检索系统）

```python
# outputs/meme_embeddings.npy - NumPy数组 (N, D)
# N = 表情包数量, D = 向量维度（如384）

# outputs/meme_ids.json - 对应的表情包ID列表
["meme_001", "meme_002", ...]

# 成员3使用示例：
import numpy as np
import json
embeddings = np.load('outputs/meme_embeddings.npy')
with open('outputs/meme_ids.json') as f:
    meme_ids = json.load(f)
```

---

## 🔧 高级功能（Week 2，可选）

### 微调脚本（暂未实现）

如果时间允许，可以开发对比学习微调：

```bash
# 预留接口
python scripts/03_fine_tune.py \
  --base_model paraphrase-multilingual-MiniLM-L12-v2 \
  --train_data data/queries_train.json \
  --epochs 3 \
  --output models/finetuned_model
```

---

## ❓ 常见问题

### Q1: 模型下载很慢怎么办？

A: 设置国内镜像源：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q2: 没有GPU可以运行吗？

A: 完全可以！所有选型的模型都是CPU友好的，推理速度足够快。

### Q3: 数据还没准备好，能先测试吗？

A: 可以！使用 `data/memes_sample.json` 和 `data/queries_sample.json` 示例数据。

### Q4: 如何验证向量文件正确性？

A: 运行快速测试：
```python
import numpy as np
embeddings = np.load('outputs/meme_embeddings.npy')
print(f"向量形状: {embeddings.shape}")  # 应该是 (N, D)
print(f"向量范围: [{embeddings.min():.3f}, {embeddings.max():.3f}]")
```

---

## 📞 联系与协作

- **需要数据时** → 联系成员2
- **向量导出后** → 通知成员3
- **评估结果** → 提交给成员1

---

## 📝 开发日志

### 2024-11-11
- ✅ 初始化项目结构
- ✅ 编写核心评估代码
- ⏳ 等待成员2提供数据

### 待更新...

---

**祝开发顺利！有问题随时沟通 💪**


