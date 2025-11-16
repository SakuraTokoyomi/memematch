# 使用真实搜索引擎指南

## ✅ 集成已完成！

成员A的搜索引擎已成功集成到Agent中。

---

## 🚀 快速开始

### 方法1：在API服务中使用（推荐）

修改 `member_b_agent/api/api_server.py`：

```python
# 原来的代码（使用 mock）
from agent.tools import setup_mock_tools

# 改为（使用真实搜索）
from agent.real_tools import setup_real_tools

# 在创建 agent 后
agent = MemeAgent()
setup_real_tools(agent)  # 使用真实搜索引擎
```

### 方法2：在测试脚本中使用

```python
from agent.agent_core import MemeAgent
from agent.real_tools import setup_real_tools

# 创建 agent
agent = MemeAgent()

# 注册真实工具
setup_real_tools(agent)

# 使用（调用agent的实际方法，如run、chat等）
# response = agent.run(user_input)
```

---

## 🔍 搜索引擎性能

- **索引大小**：4002 个表情包
- **首次加载**：~20秒（加载模型）
- **后续搜索**：< 1秒
- **支持功能**：
  - ✅ 图像语义检索（CLIP）
  - ✅ 文本内容检索（M3E）
  - ✅ 混合检索（RRF融合）
  - ✅ 分数阈值过滤（Top-1需>0.8）

---

## 📊 搜索接口

### 函数签名

```python
from agent.real_tools import real_search_meme

result = real_search_meme(
    query="happy meme",  # 查询关键词
    top_k=5,             # 返回数量
    min_score=0.0        # 最小分数（通常用0.0）
)
```

### 返回格式

```python
{
    "success": True,
    "data": {
        "query": "happy meme",
        "results": [
            {
                "image_path": "dataset/meme/xxx.jpg",
                "score": 0.8560,  # 相似度分数 (0-1)
                "tags": ["happy"],
                "metadata": {
                    "file_size": 102400,
                    "dimensions": [512, 512],
                    "format": "jpg"
                }
            },
            ...
        ],
        "total": 3,
        "filtered": 2  # 被过滤掉的数量
    },
    "metadata": {
        "search_time": 0.842,  # 搜索耗时（秒）
        "index_size": 4002,
        "timestamp": "2024-11-16T21:00:00"
    }
}
```

### 失败时

```python
{
    "success": False,
    "error": "Search failed: Top 1 result score (0.75) is not > 0.8",
    "error_code": "SEARCH_ERROR"
}
```

---

## ⚙️  配置说明

### 搜索阈值

在 `member_a_search/engine.py` 中：

```python
SCORE_THRESHOLD = 0.8  # Top-1 必须>0.8才算搜索成功
```

如果需要调整：
- **提高阈值**（如0.85）：更严格，减少低质量结果
- **降低阈值**（如0.7）：更宽松，增加召回率

### 混合权重

```python
CONTENT_WEIGHT = 0.25  # 文本内容权重
# 图像权重 = 1.0 - 0.25 = 0.75
```

---

## 🧪 测试

### 快速测试搜索引擎

```bash
cd member_a_search
python -c "
from engine import search_meme
result = search_meme('happy', top_k=3)
print(result)
"
```

### 测试Agent集成

```bash
cd member_b_agent
python -c "
from agent.agent_core import MemeAgent
from agent.real_tools import setup_real_tools

agent = MemeAgent()
setup_real_tools(agent)
print('✅ Agent with real search ready!')
"
```

---

## 🔧 故障排查

### 问题1：搜索引擎未加载

**症状**：
```
⚠️  搜索引擎不可用，将使用mock版本
```

**解决**：
1. 检查依赖：
```bash
pip list | grep -E '(faiss|sentence-transformers)'
```

2. 检查索引文件：
```bash
ls -lh member_a_search/output/*.index
```

3. 检查配置路径：
```bash
python -c "from member_a_search import config; print(config.OUTPUT_DIR)"
```

### 问题2：搜索总是失败

**症状**：
```
Search failed: Top 1 result score (0.65) is not > 0.8
```

**原因**：查询词与数据库内容不匹配

**解决**：
- 使用更通用的英文关键词
- 降低 SCORE_THRESHOLD
- 检查数据库内容

### 问题3：搜索很慢

**首次加载慢**：正常，需要加载模型（~20秒）
**后续搜索慢**：检查是否在CPU上运行，考虑使用GPU

---

## 📈 性能优化

### 缓存搜索引擎实例

```python
# ✅ 推荐：全局单例
from agent.real_tools import real_search_meme  # 内部已缓存

# ❌ 不推荐：每次创建
from member_a_search.engine import SearchEngine
engine = SearchEngine()  # 会重新加载模型！
```

### 批量查询

如果需要批量搜索，可以直接调用：

```python
from member_a_search.engine import get_search_engine

engine = get_search_engine()  # 获取单例
results = [engine.search_meme_internal(q, 5, 0.0) for q in queries]
```

---

## 🎯 与Mock版本对比

| 特性 | Mock版本 | 真实搜索 |
|------|---------|---------|
| 数据量 | 5个 | 4002个 |
| 准确性 | 随机 | AI语义匹配 |
| 速度 | 0.001s | 0.5-1s（GPU更快） |
| 依赖 | 无 | faiss, sentence-transformers |
| 用途 | 开发测试 | 生产环境 |

---

## 📝 修改API服务器示例

```python
# member_b_agent/api/api_server.py

from fastapi import FastAPI
from agent.agent_core import MemeAgent
from agent.real_tools import setup_real_tools  # 新增

app = FastAPI()

# 全局 agent 实例
agent = MemeAgent()
setup_real_tools(agent)  # 使用真实搜索！

@app.post("/chat")
async def chat(request: ChatRequest):
    # agent 现在使用真实搜索引擎
    response = agent.run(request.message)
    return response
```

---

## ✅ 验证清单

集成完成后，检查以下项：

- [ ] `from agent.real_tools import real_search_meme` 不报错
- [ ] 测试查询返回 `success: True`
- [ ] 返回的 `image_path` 指向实际文件
- [ ] API服务器使用 `setup_real_tools`
- [ ] 首次查询后，后续查询速度正常（< 1s）

---

## 🎉 完成！

现在您的Agent已经集成了成员A的高性能搜索引擎！

**下一步**：
1. 更新API服务器代码
2. 运行完整测试
3. 部署到生产环境

如有问题，查看 `agent/real_tools.py` 中的详细注释。

