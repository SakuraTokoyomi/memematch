# 🚀 快速开始

5 分钟快速上手 Meme Agent！

---

## 📦 安装

```bash
cd member_b_agent
pip install -r requirements.txt
```

---

## 🔑 配置 API Key

### 方法 1：环境变量

```bash
export SAMBANOVA_API_KEY="your-api-key-here"
```

### 方法 2：代码中指定

```python
agent = create_agent(api_key="your-api-key-here")
```

---

## 💻 基础使用

### 示例 1：最简单的用法

```python
from agent.agent_core import create_agent
from agent.tools import setup_mock_tools

# 创建 Agent
agent = create_agent(api_key="your-key")

# 注册工具（开发阶段用 mock）
setup_mock_tools(agent)

# 查询
result = agent.process_query("我真的不想努力了")

print(result["meme_path"])      # Meme 路径
print(result["explanation"])    # 推荐理由
```

### 示例 2：运行交互式 Demo

```bash
python examples/interactive_demo.py
```

输入你的情绪，Agent 会自动帮你找到或生成合适的梗图！

---

## 🔧 与真实工具集成

当成员 A 和 C 的模块准备好后：

```python
from agent.agent_core import create_agent

# 导入真实工具
from member_a_search import search_meme
from member_c_generate import generate_meme

# 创建 Agent
agent = create_agent(api_key="your-key")

# 注册真实工具
agent.register_tool("search_meme", search_meme)
agent.register_tool("generate_meme", generate_meme)

# 使用
result = agent.process_query("我无语了")
```

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_agent.py::TestAgentBasic -v
```

---

## 📖 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 [API_REFERENCE.md](docs/API_REFERENCE.md) 学习 API
- 参考 [INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) 对接其他模块

---

## ❓ 遇到问题？

1. **API key 无效**
   - 检查环境变量是否设置
   - 确认 key 有效期

2. **工具未注册**
   - 确保调用了 `register_tool()` 或 `setup_mock_tools()`

3. **响应慢**
   - 尝试使用更快的模型（Meta-Llama-3.2-3B-Instruct）
   - 减少 `max_iterations`

---

开始体验智能 Meme 推荐吧！🎉

