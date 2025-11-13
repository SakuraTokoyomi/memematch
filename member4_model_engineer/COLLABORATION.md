# 🤝 协作接口文档

本文档说明成员4（模型工程师）与其他成员的协作关系和数据接口。

---

## 📥 输入依赖（从其他成员获取）

### 从成员2（数据构建工程师）获取

#### 1. 表情包库 - `data/memes.json`

**预期交付时间**：Day 3-4  
**格式**：JSON数组

```json
[
  {
    "id": "meme_001",
    "label": "黑人问号",
    "keywords": ["困惑", "啥意思", "???", "不理解"],
    "description": "表示困惑不解",
    "emotion": "困惑",
    "safety_level": "safe"
  }
]
```

**验收标准**：
- ✅ 150-200个表情包
- ✅ 每个至少3个关键词
- ✅ JSON格式正确

#### 2. 查询数据集 - `data/queries_test.json`

**预期交付时间**：Day 3-4  
**格式**：JSON对象

```json
{
  "train": [...],
  "test": [...],
  "ground_truth": {
    "train": {...},
    "test": {...}
  }
}
```

**验收标准**：
- ✅ 测试集100-160条
- ✅ 包含ground_truth标注
- ✅ 与训练集无重叠

#### 接收流程

```bash
# 1. 成员2通知："数据已就绪"
# 2. 检查文件
ls -lh data/memes.json
ls -lh data/queries_test.json

# 3. 快速验证
python -c "
import json
with open('data/memes.json') as f:
    memes = json.load(f)
print(f'表情包数量: {len(memes)}')
"

# 4. 反馈成员2
#    - 如果有问题：立即反馈修正
#    - 如果正常：确认收到，开始评估
```

---

## 📤 输出交付（给其他成员）

### 给成员3（检索系统工程师）

#### 1. 表情包向量文件

**交付时间**：Day 5-6（数据就绪后1-2天）  
**文件清单**：

```
outputs/
├── meme_embeddings.npy    # 向量数据
├── meme_ids.json          # ID映射
├── meme_texts.txt         # 文本列表（调试用）
└── metadata.json          # 元数据
```

**使用说明**：

```python
# 成员3使用示例
import numpy as np
import json

# 加载向量
embeddings = np.load('outputs/meme_embeddings.npy')  # shape: (N, D)
with open('outputs/meme_ids.json') as f:
    meme_ids = json.load(f)

# 检查
print(f"向量数量: {len(embeddings)}")
print(f"向量维度: {embeddings.shape[1]}")
print(f"ID数量: {len(meme_ids)}")
assert len(embeddings) == len(meme_ids), "数量不匹配！"
```

#### 2. 模型信息

**提供给成员3的元数据**：

| 字段 | 值 | 说明 |
|------|---|------|
| 模型名称 | `paraphrase-multilingual-MiniLM-L12-v2` | 或其他选定模型 |
| 向量维度 | 384 / 512 / 768 | 取决于模型 |
| 数据类型 | float32 | NumPy数组类型 |
| 归一化 | 否 | 向量未归一化 |
| 相似度计算 | cosine_similarity | 推荐使用余弦相似度 |

#### 交付流程

```bash
# 1. 打包输出文件
cd outputs
tar -czf member4_outputs.tar.gz *.npy *.json *.txt

# 2. 通知成员3
#    主题：【成员4→成员3】向量文件已就绪
#    内容：
#      - 文件位置：outputs/member4_outputs.tar.gz
#      - 向量维度：384
#      - 模型名称：paraphrase-multilingual-MiniLM-L12-v2
#      - 使用说明：见 outputs/metadata.json

# 3. 协助集成测试
#    如成员3有问题，协助调试
```

---

### 给成员1（项目负责人）

#### 1. 模型评估结果

**交付时间**：Day 6  
**文件清单**：

```
outputs/
├── model_comparison.csv      # 模型对比表
└── evaluation_report.txt     # 详细评估报告
```

#### 2. 模型选型报告（1页）

**内容结构**：

```markdown
# 模型选型报告

## 1. 评估概述
- 测试模型数：4个
- 测试数据：XXX条查询 x XXX个表情包
- 评估指标：Recall@1/3/5, MRR

## 2. 模型对比
| 模型 | Recall@3 | MRR | 速度 |
|------|----------|-----|------|
| ... | ... | ... | ... |

## 3. 推荐模型
- 选择：XXX
- 理由：性能与速度平衡

## 4. 问题与改进
- 当前局限：小数据集
- 改进方向：微调、数据增强
```

---

### 给成员5（全栈与部署工程师）

#### 1. 推理接口

**提供快速推理脚本**：

```python
# inference_api.py
from sentence_transformers import SentenceTransformer
import numpy as np
import json

class MemeRecommender:
    def __init__(self, model_path, embeddings_path, ids_path):
        """
        初始化推荐器
        
        Args:
            model_path: 模型路径
            embeddings_path: 向量文件路径
            ids_path: ID映射文件路径
        """
        self.model = SentenceTransformer(model_path)
        self.meme_embeddings = np.load(embeddings_path)
        with open(ids_path) as f:
            self.meme_ids = json.load(f)
    
    def recommend(self, query_text: str, k: int = 3):
        """
        推荐Top-k表情包
        
        Args:
            query_text: 用户输入的聊天句子
            k: 返回Top-k个结果
            
        Returns:
            [(meme_id, score), ...]
        """
        # 编码查询
        query_emb = self.model.encode([query_text])[0]
        
        # 计算相似度
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity([query_emb], self.meme_embeddings)[0]
        
        # 获取Top-k
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        results = [(self.meme_ids[i], float(similarities[i])) 
                   for i in top_k_indices]
        
        return results

# 使用示例
recommender = MemeRecommender(
    model_path='paraphrase-multilingual-MiniLM-L12-v2',
    embeddings_path='outputs/meme_embeddings.npy',
    ids_path='outputs/meme_ids.json'
)

results = recommender.recommend("哈哈哈太好笑了", k=3)
print(results)
```

---

## 📞 沟通协议

### 日常沟通

| 场景 | 联系对象 | 方式 | 预期响应时间 |
|------|---------|------|------------|
| 数据格式问题 | 成员2 | 消息/邮件 | 4小时内 |
| 向量集成问题 | 成员3 | 消息/邮件 | 当天内 |
| 评估结果汇报 | 成员1 | 邮件 | 48小时内 |
| API接口问题 | 成员5 | 消息/视频 | 当天内 |

### 关键节点同步

#### Checkpoint 1: 数据验收（Day 4）
- **与成员2**：确认数据格式、质量
- **结果**：通过/需修正

#### Checkpoint 2: 模型选型（Day 6）
- **与成员1**：汇报评估结果
- **与成员3**：确认向量交付时间

#### Checkpoint 3: 集成测试（Day 8）
- **与成员3**：协助检索系统集成测试
- **与成员5**：确认推理API正常

---

## 🔧 调试协作

### 问题1：向量维度不匹配

**现象**：成员3报告维度错误  
**排查**：
```python
# 成员4检查
embeddings = np.load('outputs/meme_embeddings.npy')
print(embeddings.shape)  # 应该是 (N, D)

# 成员3检查
model = SentenceTransformer('model_name')
print(model.get_sentence_embedding_dimension())
```

### 问题2：检索效果差

**现象**：成员3或成员5反馈推荐结果不准  
**排查流程**：
1. 确认使用的模型是否正确
2. 确认相似度计算方式（余弦相似度）
3. 提供调试脚本给成员3

```python
# 调试脚本
query = "测试句子"
query_emb = model.encode([query])[0]
similarities = cosine_similarity([query_emb], meme_embeddings)[0]
top_5 = np.argsort(similarities)[-5:][::-1]
for idx in top_5:
    print(f"{meme_ids[idx]}: {similarities[idx]:.4f}")
```

---

## 📋 质量检查清单

### 交付前自检

**向量文件**：
- [ ] 文件存在且可读取
- [ ] 维度正确 (N, D)
- [ ] 数据类型 float32
- [ ] 无NaN或Inf值
- [ ] ID数量与向量数量一致

**评估结果**：
- [ ] 所有模型都成功评估
- [ ] 结果保存为CSV
- [ ] 报告包含消融分析
- [ ] 推荐模型有明确理由

**文档**：
- [ ] metadata.json 完整
- [ ] 使用示例正确
- [ ] 联系方式留存

---

## 🎯 成功标准

### 最低交付标准（必须）
- ✅ 至少评估3个模型
- ✅ Recall@3 ≥ 0.55
- ✅ 向量文件格式正确
- ✅ 推理速度 < 300ms/query（CPU）

### 优秀标准（加分）
- 🌟 评估5+个模型
- 🌟 Recall@3 ≥ 0.65
- 🌟  提供微调版本对比
- 🌟 详细的误差分析

---

**记住：良好的协作是项目成功的关键！** 🤝


