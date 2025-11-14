# API 参考文档

## Agent 核心 API

### `MemeAgent` 类

#### 构造函数

```python
MemeAgent(config: Optional[AgentConfig] = None)
```

**参数：**
- `config` (AgentConfig, optional): Agent 配置对象，如果为 None 则从环境变量加载

**示例：**

```python
from agent.agent_core import MemeAgent
from agent.config import AgentConfig

config = AgentConfig(
    api_key="your-sambanova-key",
    model="Meta-Llama-3.1-8B-Instruct",
    temperature=0.7
)

agent = MemeAgent(config)
```

---

#### 方法

##### `process_query`

```python
process_query(
    user_query: str, 
    max_iterations: Optional[int] = None,
    debug: bool = False
) -> Dict[str, Any]
```

处理用户查询的主函数。

**参数：**
- `user_query` (str): 用户输入的查询文本
- `max_iterations` (int, optional): 最大迭代次数，默认使用配置值
- `debug` (bool): 是否输出详细调试信息

**返回值：**

```python
{
    "meme_path": str,           # Meme 图片路径
    "explanation": str,         # 推荐理由
    "candidates": List[Dict],   # 候选结果
    "reasoning_steps": List[Dict],  # 推理步骤
    "status": str,              # "success" 或 "error"
    "source": str,              # "search" 或 "generated"
    "search_score": float       # 检索分数（仅 search 时）
}
```

**示例：**

```python
result = agent.process_query("我真的不想努力了")

print(result["meme_path"])      # dataset/train/tired_001.jpg
print(result["explanation"])    # 这张图完美表达了...
print(result["source"])         # search
```

---

##### `register_tool`

```python
register_tool(name: str, func: Callable)
```

注册外部工具函数。

**参数：**
- `name` (str): 工具名称（必须与 tools schema 中的名称一致）
- `func` (Callable): 工具函数

**要求：**
- 工具函数必须返回 Dict 类型
- 建议包含错误处理

**示例：**

```python
def my_search_meme(query: str, top_k: int = 5):
    # 你的实现
    return {
        "results": [...]
    }

agent.register_tool("search_meme", my_search_meme)
```

---

### `AgentConfig` 类

配置类，用于设置 Agent 参数。

#### 属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | str | 必填 | SambaNova API key |
| `base_url` | str | `https://api.sambanova.ai/v1` | API 端点 |
| `model` | str | `Meta-Llama-3.1-8B-Instruct` | 模型名称 |
| `temperature` | float | 0.7 | 生成温度 |
| `max_iterations` | int | 10 | 最大迭代次数 |
| `timeout` | int | 30 | 超时时间（秒） |
| `search_score_threshold` | float | 0.6 | 检索质量阈值 |
| `log_level` | str | `INFO` | 日志级别 |

#### 方法

##### `from_env`

```python
@classmethod
from_env() -> AgentConfig
```

从环境变量加载配置。

**环境变量：**
- `SAMBANOVA_API_KEY`
- `SAMBANOVA_BASE_URL`
- `SAMBANOVA_MODEL`
- `AGENT_TEMPERATURE`
- `AGENT_MAX_ITERATIONS`
- `SEARCH_SCORE_THRESHOLD`

**示例：**

```python
# 设置环境变量后
config = AgentConfig.from_env()
agent = MemeAgent(config)
```

---

## 工具 API

### 外部工具接口定义

#### `search_meme`

由成员 A 实现。

```python
def search_meme(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    从向量数据库检索相关 meme
    
    Args:
        query: 英文检索关键词，例如 "tired reaction meme"
        top_k: 返回结果数量
        
    Returns:
        {
            "query": str,           # 查询关键词
            "results": [            # 检索结果
                {
                    "image_path": str,      # 图片路径
                    "score": float,         # 相似度分数 (0-1)
                    "tags": List[str],      # 标签
                    "metadata": dict        # 其他元数据
                },
                ...
            ],
            "total": int,           # 结果总数
            "search_time": float    # 检索耗时（可选）
        }
    """
```

**要求：**
- `results` 必须按 `score` 降序排序
- `score` 越接近 1 表示越相关
- `image_path` 必须是有效的文件路径

---

#### `generate_meme`

由成员 C 实现。

```python
def generate_meme(text: str, template: str = "drake") -> Dict[str, Any]:
    """
    生成新的 meme 图片
    
    Args:
        text: 要显示在 meme 上的文字
        template: 模板类型
            - "drake": Drake 模板（上下对比）
            - "doge": Doge 模板（柴犬）
            - "wojak": Wojak 模板
            - "distracted_boyfriend": 分心男友
            - "two_buttons": 两个按钮
        
    Returns:
        {
            "image_path": str,      # 生成的图片路径
            "template": str,        # 使用的模板
            "text": str,           # 显示的文字
            "status": str,         # "success" 或 "error"
            "generation_time": float  # 生成耗时（可选）
        }
    """
```

**要求：**
- 生成时间 < 0.5s（模板版）
- 图片保存到指定目录
- 文字自动换行和调整字号

---

### 内部工具

这些工具由 Agent 自己实现，无需外部注册。

#### `refine_query`

```python
_refine_query_internal(user_query: str) -> Dict[str, Any]
```

将中文口语化输入改写成英文检索关键词。

**返回：**
```python
{
    "original": "我无语了",
    "refined": "speechless reaction meme"
}
```

---

#### `classify_sentiment`

```python
_classify_sentiment_internal(text: str) -> Dict[str, Any]
```

分析文本的情绪类型和强度。

**返回：**
```python
{
    "emotion": "tired",        # 情绪类型
    "intensity": 0.8,         # 强度 (0-1)
    "description": "疲惫"      # 描述
}
```

**支持的情绪类型：**
- happy（开心）
- sad（悲伤）
- angry（生气）
- surprised（惊讶）
- disgusted（厌恶）
- fearful（恐惧）
- tired（疲惫）
- confused（困惑）
- excited（兴奋）
- neutral（中性）

---

## 辅助函数

### `create_agent`

```python
create_agent(
    api_key: Optional[str] = None,
    model: str = "Meta-Llama-3.1-8B-Instruct",
    **kwargs
) -> MemeAgent
```

便捷函数：快速创建 Agent 实例。

**示例：**

```python
from agent.agent_core import create_agent

agent = create_agent(
    api_key="your-key",
    model="Meta-Llama-3.1-8B-Instruct",
    temperature=0.8
)
```

---

### `setup_mock_tools`

```python
setup_mock_tools(agent: MemeAgent)
```

为 Agent 注册所有 mock 工具（用于开发测试）。

**示例：**

```python
from agent.tools import setup_mock_tools

setup_mock_tools(agent)
```

---

### `setup_production_tools`

```python
setup_production_tools(
    agent: MemeAgent, 
    search_func: Callable, 
    generate_func: Callable
)
```

为 Agent 注册生产环境的工具。

**参数：**
- `agent`: MemeAgent 实例
- `search_func`: 成员 A 提供的检索函数
- `generate_func`: 成员 C 提供的生成函数

**示例：**

```python
from agent.tools import setup_production_tools
from member_a_module import search_meme
from member_c_module import generate_meme

setup_production_tools(agent, search_meme, generate_meme)
```

---

## 返回数据结构

### Query Result

```python
{
    "meme_path": str,           # Meme 路径
    "explanation": str,         # 推荐理由
    "candidates": [             # 候选列表
        {
            "image_path": str,
            "score": float,
            "tags": List[str]
        }
    ],
    "reasoning_steps": [        # 推理步骤
        {
            "step": int,
            "tool": str,
            "arguments": dict,
            "result": dict
        }
    ],
    "status": str,              # success/error
    "source": str,              # search/generated
    "search_score": float       # 仅 search 时
}
```

---

## 错误处理

### 常见错误

| 错误类型 | 原因 | 解决方案 |
|---------|------|---------|
| `工具未注册` | 调用了未注册的工具 | 调用 `register_tool()` |
| `API key 无效` | API key 错误或过期 | 检查环境变量 |
| `达到最大迭代` | 推理循环超限 | 增加 `max_iterations` |
| `超时` | 请求时间过长 | 调整 `timeout` 参数 |

### 错误返回格式

```python
{
    "error": "错误信息",
    "reasoning_steps": [...],
    "status": "error"
}
```

---

## 示例代码

### 完整使用流程

```python
import os
from agent.agent_core import create_agent
from agent.tools import setup_production_tools

# 1. 创建 Agent
agent = create_agent(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    model="Meta-Llama-3.1-8B-Instruct"
)

# 2. 注册工具（假设已实现）
from member_a_search import search_meme
from member_c_generate import generate_meme

setup_production_tools(agent, search_meme, generate_meme)

# 3. 处理查询
result = agent.process_query("我真的不想努力了", debug=True)

# 4. 使用结果
if result["status"] == "success":
    print(f"Meme: {result['meme_path']}")
    print(f"理由: {result['explanation']}")
    
    # 显示图片（假设在 UI 中）
    display_image(result['meme_path'])
else:
    print(f"错误: {result.get('error')}")
```

---

## 性能优化建议

1. **缓存查询结果**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, top_k: int):
    return search_meme(query, top_k)

agent.register_tool("search_meme", cached_search)
```

2. **调整温度参数**

```python
# 更确定性的输出
config = AgentConfig(temperature=0.3)

# 更多样化的输出
config = AgentConfig(temperature=0.9)
```

3. **减少迭代次数**

```python
# 简单查询
result = agent.process_query("开心", max_iterations=3)
```

---

## 版本历史

- **v1.0.0** (2024-11): 初始版本
  - 基于 SambaNova + Function Calling
  - 支持 4 个核心工具
  - 完整的推理循环

---

## 更多资源

- [README](../README.md) - 项目概述
- [测试指南](../tests/test_agent.py) - 单元测试
- [示例代码](../examples/) - 使用示例

