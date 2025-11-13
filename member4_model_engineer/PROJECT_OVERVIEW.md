# 📊 项目总览

## 成员4：模型工程师 - 完整工作方案

---

## 🎯 核心职责

您负责 **MemeMatch** 项目的文本表示模型，这是整个检索系统的核心：

1. **句向量模型选型**：评估多个预训练模型，选出最适合"聊天句子→表情包"匹配的模型
2. **零样本评估**：在标注数据上测试模型性能
3. **向量导出**：将表情包编码为向量，供检索系统使用
4. **可选微调**：如时间允许，进行对比学习微调

---

## 📁 项目结构

```
member4_model_engineer/
├── 📄 README.md                    # 主要说明文档
├── 📄 QUICKSTART.md                # 快速开始指南（⭐推荐先看）
├── 📄 COLLABORATION.md             # 协作接口文档
├── 📄 PROJECT_OVERVIEW.md          # 本文档
├── 📄 requirements.txt             # Python依赖
├── 📄 .gitignore                   # Git忽略规则
├── 🐍 test_setup.py                # 环境测试脚本
│
├── 📂 config/                      # 配置文件
│   └── models.yaml                 # 模型列表配置
│
├── 📂 data/                        # 数据目录（⚠️需要成员2提供）
│   ├── README.md                   # 数据格式说明
│   ├── memes_sample.json           # 示例：表情包数据
│   ├── queries_sample.json         # 示例：查询数据
│   ├── memes.json                  # [待填充] 完整表情包库
│   ├── queries_train.json          # [待填充] 训练集
│   └── queries_test.json           # [待填充] 测试集
│
├── 📂 src/                         # 源代码
│   ├── __init__.py                 # 包初始化
│   ├── model_evaluator.py          # ⭐核心：模型评估器
│   ├── embedding_exporter.py       # ⭐核心：向量导出器
│   └── utils.py                    # 工具函数
│
├── 📂 scripts/                     # 可执行脚本
│   ├── 01_compare_models.py        # ⭐脚本1：模型对比
│   └── 02_export_embeddings.py     # ⭐脚本2：导出向量
│
├── 📂 outputs/                     # 输出目录
│   ├── .gitkeep                    
│   ├── model_comparison.csv        # [生成] 模型对比结果
│   ├── evaluation_report.txt       # [生成] 评估报告
│   ├── meme_embeddings.npy         # [生成] 向量数据
│   ├── meme_ids.json               # [生成] ID映射
│   └── metadata.json               # [生成] 元数据
│
└── 📂 models/                      # 模型缓存（自动下载）
    └── (HuggingFace自动管理)
```

---

## 🗓️ 工作时间线

### Week 1（当前周）

| 时间 | 任务 | 产出 | 状态 |
|------|------|------|------|
| Day 1 | ✅ 搭建项目环境 | 完整目录结构 | ✅ 完成 |
| Day 1 | 安装依赖、测试环境 | `python test_setup.py` 通过 | ⏳ 待进行 |
| Day 2-3 | ⏳ 等待成员2数据 | - | ⏳ 等待中 |
| Day 4 | 验收数据 | 数据质量确认 | ⏳ 待进行 |
| Day 5-6 | 运行模型评估 | `model_comparison.csv` | ⏳ 待进行 |
| Day 7 | 导出向量 | `meme_embeddings.npy` | ⏳ 待进行 |

### Week 2（可选进阶）

| 时间 | 任务 | 产出 | 状态 |
|------|------|------|------|
| Day 8-10 | 微调脚本开发（可选） | 微调模型 | ⏳ 待定 |
| Day 11-12 | 消融实验 | 对比报告 | ⏳ 待定 |
| Day 13-14 | 协助集成测试 | - | ⏳ 待定 |

---

## ✅ 任务检查清单

### 阶段0：环境准备（今天完成）

- [x] 项目目录已创建
- [ ] 依赖已安装：`pip install -r requirements.txt`
- [ ] 环境测试通过：`python test_setup.py`
- [ ] 阅读完 `QUICKSTART.md`

### 阶段1：数据准备（Day 2-4）

- [ ] 联系成员2确认数据进度
- [ ] 收到 `data/memes.json`（150-200个表情包）
- [ ] 收到 `data/queries_test.json`（测试集）
- [ ] 验证数据格式正确
- [ ] 反馈数据质量给成员2

### 阶段2：模型评估（Day 5-6）

- [ ] 运行 `python scripts/01_compare_models.py`
- [ ] 生成 `outputs/model_comparison.csv`
- [ ] 选出最佳模型（基于Recall@3）
- [ ] 撰写模型选型报告（1页）

### 阶段3：向量导出（Day 7）

- [ ] 运行 `python scripts/02_export_embeddings.py --model <最佳模型>`
- [ ] 生成 `outputs/meme_embeddings.npy`
- [ ] 验证向量文件正确性
- [ ] 打包输出文件
- [ ] 通知成员3：向量已就绪

### 阶段4：协作交付（Day 7-8）

- [ ] 交付向量文件给成员3
- [ ] 交付评估结果给成员1
- [ ] 提供推理接口给成员5
- [ ] 协助集成测试

---

## 🎓 关键知识点

### 1. 句向量模型

**什么是句向量？**
- 将句子映射到固定维度的向量空间
- 语义相似的句子在向量空间中距离近
- 使用余弦相似度衡量相似性

**为什么选这些模型？**
- `paraphrase-multilingual-MiniLM-L12-v2`：多语言、轻量、CPU友好
- `shibing624/text2vec-base-chinese`：中文优化
- `moka-ai/m3e-base`：中文场景效果好

### 2. 评估指标

- **Recall@k**：Top-k预测中有多少正确答案（最重要）
- **MRR**：第一个正确答案的平均排名倒数
- **推理速度**：每秒处理多少句子

**目标**：
- Recall@3 ≥ 0.55（零样本基线）
- 推理速度 > 10句/秒（CPU）

### 3. 向量导出格式

```python
# 向量数组
embeddings.npy     # shape: (N, D), dtype: float32
# N = 表情包数量（150-200）
# D = 向量维度（384/512/768）

# ID映射
meme_ids.json      # ["meme_001", "meme_002", ...]
```

---

## 🤝 协作关系图

```
成员2（数据）
    ↓
  [数据文件]
    ↓
成员4（模型）← 你在这里 ←┐
    ↓                    │
  [向量文件]              │
    ↓                    │
成员3（检索）             │ 协助
    ↓                    │ 调试
成员5（部署）             │
    ↓                    │
成员1（评测）____________↑
```

---

## 📚 文档导航

**根据您的需求选择阅读**：

| 想了解... | 阅读文档 |
|----------|---------|
| 🚀 快速开始、操作步骤 | `QUICKSTART.md` |
| 📖 详细功能说明 | `README.md` |
| 🤝 如何与其他成员协作 | `COLLABORATION.md` |
| 📊 项目全局视图 | `PROJECT_OVERVIEW.md`（本文档） |
| 📦 数据格式要求 | `data/README.md` |
| ⚙️ 模型配置 | `config/models.yaml` |

---

## 🆘 遇到问题？

### 环境问题
```bash
# 重新安装依赖
pip install --upgrade -r requirements.txt

# 测试环境
python test_setup.py
```

### 数据问题
- 查看 `data/README.md` 确认格式
- 联系成员2

### 模型下载慢
```bash
# 设置镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 代码问题
- 查看 `src/` 中的代码注释
- 所有函数都有详细文档字符串

---

## 🎯 成功标准

### 必须完成（80分）
- ✅ 至少评估3个模型
- ✅ 产出模型对比表格
- ✅ 导出正确的向量文件
- ✅ Recall@3 ≥ 0.55

### 优秀标准（100分）
- 🌟 评估5个模型
- 🌟 Recall@3 ≥ 0.65
- 🌟 包含误差分析
- 🌟 提供微调版本

---

## 💡 提示与建议

1. **优先级**：先用示例数据测试流程，确保代码没问题
2. **时间管理**：模型评估可能需要10-30分钟，建议晚上运行
3. **版本控制**：记录每次实验的模型名称、参数、结果
4. **沟通主动**：数据有问题立即反馈，不要等
5. **文档完整**：所有交付物都要有使用说明

---

## 📞 联系方式

- **数据问题** → 成员2
- **检索集成** → 成员3  
- **部署问题** → 成员5
- **评估汇报** → 成员1

---

**准备好了吗？开始您的工作吧！** 🚀

**建议第一步**：
```bash
cd member4_model_engineer
python test_setup.py
```


