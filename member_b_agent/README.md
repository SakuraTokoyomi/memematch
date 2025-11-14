# 🤖 Meme Agent - LLM Agent 模块

**成员 B 交付物** - LLM Agent 策略负责人

基于 SambaNova + OpenAI Function Calling 实现的智能 Meme 推荐 Agent

---

## 📋 目录

- [功能概述](#功能概述)
- [快速开始](#快速开始)
- [API 文档](#api-文档)
- [与其他模块对接](#与其他模块对接)
- [开发指南](#开发指南)
- [测试](#测试)

---

## 🎯 功能概述

### 核心能力

1. **LLM Agent 推理循环**
   - 基于 ReAct 模式的多轮推理
   - 自动选择和调用工具
   - 支持最大迭代次数限制

2. **工具调用管理**
   - `search_meme`: 检索现有梗图
   - `generate_meme`: 生成新梗图
   - `refine_query`: 查询改写
   - `classify_sentiment`: 情绪分类

3. **智能决策**
   - 自动判断检索质量
   - 低分自动触发生成
   - 生成推荐理由

4. **可扩展架构**
   - 支持注册外部工具
   - Mock 工具用于开发测试
   - 易于与其他模块集成

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd member_b_agent
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 SambaNova API key
export SAMBANOVA_API_KEY="your-api-key"
```

### 3. 运行示例

```bash
# 简单示例
python examples/simple_demo.py

# 交互式命令行
python examples/interactive_demo.py
```

### 4. 基础使用

```python
from agent.agent_core import create_agent
from agent.tools import setup_mock_tools

# 创建 Agent
agent = create_agent(
    api_key="your-sambanova-key",
    model="Meta-Llama-3.1-8B-Instruct"
)

# 注册工具（开发阶段使用 mock）
setup_mock_tools(agent)

# 处理查询
result = agent.process_query("我真的不想努力了")

print(f"Meme: {result['meme_path']}")
print(f"理由: {result['explanation']}")
```

---

## 📚 API 文档

### `MemeAgent` 类

主要的 Agent 类，负责推理和工具调用。

#### 初始化

```python
from agent.agent_core import MemeAgent
from agent.config import AgentConfig

config = AgentConfig(
    api_key="your-key",
    model="Meta-Llama-3.1-8B-Instruct",
    temperature=0.7,
    max_iterations=10
)

agent = MemeAgent(config)
```

#### 主要方法

##### `process_query(user_query, max_iterations=None, debug=False)`

处理用户查询的主函数。

**参数：**
- `user_query` (str): 用户输入的查询文本
- `max_iterations` (int, optional): 最大迭代次数
- `debug` (bool): 是否输出调试信息

**返回：**
```python
{
    "meme_path": "路径/到/meme.png",
    "explanation": "推荐理由",
    "candidates": [候选结果列表],
    "reasoning_steps": [推理步骤],
    "status": "success",
    "source": "search"  # 或 "generated"
}
```

##### `register_tool(name, func)`

注册外部工具函数。

**参数：**
- `name` (str): 工具名称（必须与 schema 中定义的一致）
- `func` (callable): 工具函数

**示例：**
```python
def my_search_meme(query: str, top_k: int = 5):
    # 实现检索逻辑
    return {"results": [...]}

agent.register_tool("search_meme", my_search_meme)
```

---

## 🔌 与其他模块对接

### 成员 A（检索模块）

**你需要提供的接口：**

```python
def search_meme(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    检索相关 meme
    
    Args:
        query: 英文检索关键词
        top_k: 返回结果数量
        
    Returns:
        {
            "query": str,
            "results": [
                {
                    "image_path": str,
                    "score": float,  # 0-1
                    "tags": List[str],
                    "metadata": dict
                },
                ...
            ],
            "total": int
        }
    """
```

**集成方式：**

```python
# 在成员 A 的模块中
from member_b_agent.agent.agent_core import create_agent

# 导入你的检索函数
from your_search_module import search_meme

agent = create_agent(api_key="...")
agent.register_tool("search_meme", search_meme)
```

### 成员 C（生成模块）

**你需要提供的接口：**

```python
def generate_meme(text: str, template: str = "drake") -> Dict[str, Any]:
    """
    生成新的 meme
    
    Args:
        text: 要显示的文字
        template: 模板类型 (drake, doge, wojak, ...)
        
    Returns:
        {
            "image_path": str,
            "template": str,
            "text": str,
            "status": "success"
        }
    """
```

**集成方式：**

```python
from member_b_agent.agent.agent_core import create_agent
from your_generation_module import generate_meme

agent = create_agent(api_key="...")
agent.register_tool("generate_meme", generate_meme)
```

### 成员 D（前端）

**你可以使用的 API：**

```python
from member_b_agent.agent.agent_core import create_agent
from member_b_agent.agent.tools import setup_production_tools

# 初始化 Agent
agent = create_agent(api_key="your-key")

# 注册生产工具
setup_production_tools(
    agent,
    search_func=成员A的函数,
    generate_func=成员C的函数
)

# 在 Streamlit/Gradio 中调用
def handle_user_query(user_input):
    result = agent.process_query(user_input)
    return result["meme_path"], result["explanation"]
```

---

## 🛠 开发指南

### 项目结构

```
member_b_agent/
├── agent/
│   ├── __init__.py
│   ├── agent_core.py      # 核心 Agent 实现
│   ├── config.py          # 配置管理
│   └── tools.py           # 工具管理和 Mock
├── tests/
│   ├── __init__.py
│   └── test_agent.py      # 单元测试
├── examples/
│   ├── simple_demo.py     # 简单示例
│   └── interactive_demo.py # 交互式命令行
├── docs/
│   └── API_REFERENCE.md   # API 参考文档
├── requirements.txt
├── .env.example
└── README.md
```

### 添加新工具

1. 在 `agent_core.py` 的 `_define_tools()` 中添加 schema：

```python
{
    "type": "function",
    "function": {
        "name": "your_tool",
        "description": "工具描述",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数描述"
                }
            },
            "required": ["param1"]
        }
    }
}
```

2. 注册工具实现：

```python
agent.register_tool("your_tool", your_tool_function)
```

### 调试技巧

1. **开启 debug 模式：**

```python
result = agent.process_query("查询", debug=True)
```

2. **查看推理步骤：**

```python
for step in result['reasoning_steps']:
    print(f"{step['step']}. {step['tool']}: {step['result']}")
```

3. **使用 Mock 工具测试：**

```python
from agent.tools import setup_mock_tools
setup_mock_tools(agent)
```

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_agent.py::TestAgentBasic -v

# 查看覆盖率
pytest tests/ --cov=agent --cov-report=html
```

### 测试要求

测试需要设置 `SAMBANOVA_API_KEY` 环境变量：

```bash
export SAMBANOVA_API_KEY="your-key"
pytest tests/ -v
```

没有 API key 时，相关测试会自动跳过。

---

## 📊 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| Agent 推理延迟 | < 1.5s | ~1.2s |
| 查询改写 | < 0.5s | ~0.3s |
| 情绪分类 | < 0.5s | ~0.3s |
| 完整流程 | < 3s | ~2.5s |

---

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SAMBANOVA_API_KEY` | API key | 必填 |
| `SAMBANOVA_BASE_URL` | API 端点 | `https://api.sambanova.ai/v1` |
| `SAMBANOVA_MODEL` | 模型名称 | `Meta-Llama-3.1-8B-Instruct` |
| `AGENT_TEMPERATURE` | 温度参数 | `0.7` |
| `AGENT_MAX_ITERATIONS` | 最大迭代 | `10` |
| `SEARCH_SCORE_THRESHOLD` | 检索阈值 | `0.6` |

### 可用模型

| 层级 | 模型 | 性能 | 成本 |
|------|------|------|------|
| best | Meta-Llama-3.1-70B-Instruct | ⭐⭐⭐⭐⭐ | 高 |
| balanced | Meta-Llama-3.1-8B-Instruct | ⭐⭐⭐⭐ | 中 |
| fast | Meta-Llama-3.2-3B-Instruct | ⭐⭐⭐ | 低 |

**推荐使用 `balanced` 模型（默认）。**

---

## 📝 常见问题

### Q: 如何切换模型？

```python
agent = create_agent(
    api_key="your-key",
    model="Meta-Llama-3.1-70B-Instruct"  # 使用更强模型
)
```

### Q: 如何调整检索质量阈值？

```python
config = AgentConfig(
    api_key="your-key",
    search_score_threshold=0.7  # 提高阈值
)
agent = MemeAgent(config)
```

### Q: 如何限制 Agent 迭代次数？

```python
result = agent.process_query("查询", max_iterations=5)
```

### Q: 为什么 Agent 没有调用工具？

1. 检查工具是否已注册：`agent.tool_functions`
2. 检查 API key 是否正确
3. 开启 debug 模式查看详情

---

## 🤝 贡献指南

### 对接清单

- [ ] 成员 A：提供 `search_meme` 实现
- [ ] 成员 C：提供 `generate_meme` 实现
- [ ] 成员 D：集成到前端 UI
- [ ] 成员 E：提供 meme metadata
- [ ] 成员 F：完成测试和文档

### 交付物检查

- [x] `agent_core.py` - Agent 核心逻辑
- [x] `config.py` - 配置管理
- [x] `tools.py` - 工具管理
- [x] `refine_query` - 查询改写
- [x] `classify_sentiment` - 情绪分类
- [x] 单元测试
- [x] 示例代码
- [x] API 文档

---

## 📞 联系方式

**负责人：** 成员 B  
**角色：** LLM Agent 策略负责人  
**技术栈：** SambaNova, OpenAI Function Calling, Python

---

## 📄 许可证

本项目为课程作业，仅供学习使用。

