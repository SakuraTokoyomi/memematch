# 🚀 快速开始指南

## 第一步：环境准备（5分钟）

```bash
# 进入项目目录
cd member4_model_engineer

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**注意事项**：
- 如果下载慢，设置镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
- PyTorch可能需要单独安装：`pip install torch --index-url https://download.pytorch.org/whl/cpu`

---

## 第二步：测试示例数据（可选，2分钟）

在等待成员2提供数据期间，可以用示例数据测试：

```bash
# 运行模型对比（使用示例数据）
python scripts/01_compare_models.py
```

**预期输出**：
- 控制台显示评估进度和结果
- 生成 `outputs/model_comparison.csv`
- 生成 `outputs/evaluation_report.txt`

---

## 第三步：等待真实数据（1-2天）

**需要成员2提供**：
- `data/memes.json` - 150-200个表情包
- `data/queries_test.json` - 测试查询句子
- `data/ground_truth.json` - 标注答案

数据格式说明见 `data/README.md`

---

## 第四步：运行正式评估（10-30分钟）

数据准备好后：

```bash
# 运行模型对比
python scripts/01_compare_models.py

# 查看结果
cat outputs/model_comparison.csv
```

**关键指标**：
- **Recall@3**：最重要，目标 ≥ 0.55
- **MRR**：排序质量
- **速度**：推理速度，目标 > 10句/秒

---

## 第五步：导出向量（5分钟）

选择最佳模型，导出向量：

```bash
# 使用评估中表现最好的模型
python scripts/02_export_embeddings.py --model paraphrase-multilingual-MiniLM-L12-v2

# 或使用其他模型
python scripts/02_export_embeddings.py --model shibing624/text2vec-base-chinese
```

**输出文件**（在 `outputs/` 目录）：
- `meme_embeddings.npy` - 向量数据
- `meme_ids.json` - ID映射
- `meme_texts.txt` - 文本列表
- `metadata.json` - 元数据

---

## 第六步：交付成果

### 交付给成员3（检索系统）

```bash
# 打包输出文件
cd outputs
zip member4_outputs.zip meme_embeddings.npy meme_ids.json metadata.json

# 通知成员3
```

**提供给成员3的信息**：
- 向量维度：384/512/768（取决于模型）
- 数据格式：NumPy float32
- 使用示例：见 `metadata.json`

### 交付给成员1（项目负责人）

```bash
# 提交评估结果
outputs/model_comparison.csv
outputs/evaluation_report.txt
```

**撰写1页模型选型报告**：
- 测试了哪些模型
- 各模型性能对比
- 推荐哪个模型及原因
- 存在的问题与改进方向

---

## 常见问题

### Q1: 模型下载很慢

```bash
# 设置HuggingFace镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### Q2: 内存不足

```python
# 修改批处理大小
python scripts/02_export_embeddings.py --batch-size 16
```

### Q3: 想测试单个模型

```python
# 修改 config/models.yaml，只保留想测试的模型
```

### Q4: 如何验证向量正确性

```python
import numpy as np
embeddings = np.load('outputs/meme_embeddings.npy')
print(f"形状: {embeddings.shape}")  # (N, D)
print(f"范围: [{embeddings.min():.3f}, {embeddings.max():.3f}]")
print(f"类型: {embeddings.dtype}")  # float32
```

---

## 时间规划

| 任务 | 预计时间 | 状态 |
|------|---------|------|
| 环境安装 | 5-10分钟 | ⏳ |
| 示例数据测试 | 2分钟 | ⏳ |
| 等待真实数据 | 1-2天 | ⏳ 等待成员2 |
| 正式评估 | 10-30分钟 | ⏳ |
| 导出向量 | 5分钟 | ⏳ |
| 撰写报告 | 1-2小时 | ⏳ |

---

## 需要帮助？

- **数据问题** → 联系成员2
- **检索集成** → 联系成员3
- **技术问题** → 查看 README.md

---

**祝工作顺利！** 🎉


