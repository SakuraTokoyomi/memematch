# 对接集成指南

本文档说明如何与成员 B 的 Agent 模块进行对接。

---

## 📋 概述

成员 B 提供的 **Meme Agent** 是项目的"大脑"，负责：
1. 理解用户输入
2. 调度工具（检索/生成）
3. 生成推荐理由

其他成员需要提供具体的工具实现。

---

## 🔌 成员 A：检索模块对接

### 你需要实现的接口

```python
def search_meme(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    从 FAISS 向量数据库检索相关 meme
    
    Args:
        query: 英文检索关键词（由 Agent 自动生成）
        top_k: 返回结果数量
        
    Returns:
        {
            "query": query,
            "results": [
                {
                    "image_path": "dataset/train/001.jpg",
                    "score": 0.92,
                    "tags": ["tired", "exhausted"],
                    "metadata": {...}
                },
                ...
            ],
            "total": len(results)
        }
    """
```

### 集成步骤

1. **导入你的检索模块**

```python
# 假设你的代码在 member_a_search/
from member_a_search.faiss_index import FaissSearcher

# 初始化你的检索器
searcher = FaissSearcher(index_path="path/to/faiss.index")

# 定义适配函数
def search_meme(query: str, top_k: int = 5):
    results = searcher.search(query, k=top_k)
    
    return {
        "query": query,
        "results": [
            {
                "image_path": r["path"],
                "score": r["similarity"],
                "tags": r.get("tags", []),
                "metadata": r.get("metadata", {})
            }
            for r in results
        ],
        "total": len(results)
    }
```

2. **注册到 Agent**

```python
from member_b_agent.agent.agent_core import create_agent

agent = create_agent(api_key="your-key")
agent.register_tool("search_meme", search_meme)
```

### 测试验证

```python
# 测试你的接口
result = search_meme("tired reaction meme", top_k=3)

assert "results" in result
assert len(result["results"]) <= 3
assert all("score" in r for r in result["results"])
print("✓ 接口验证通过")
```

---

## 🎨 成员 C：生成模块对接

### 你需要实现的接口

```python
def generate_meme(text: str, template: str = "drake") -> Dict[str, Any]:
    """
    使用模板生成 meme
    
    Args:
        text: 要显示的文字（由 Agent 提取）
        template: 模板类型
        
    Returns:
        {
            "image_path": "generated/meme_001.png",
            "template": template,
            "text": text,
            "status": "success"
        }
    """
```

### 集成步骤

1. **导入你的生成模块**

```python
# 假设你的代码在 member_c_generate/
from member_c_generate.template_generator import TemplateGenerator

# 初始化生成器
generator = TemplateGenerator(templates_dir="path/to/templates")

# 定义适配函数
def generate_meme(text: str, template: str = "drake"):
    try:
        output_path = generator.generate(
            template=template,
            text=text,
            output_dir="outputs/"
        )
        
        return {
            "image_path": output_path,
            "template": template,
            "text": text,
            "status": "success"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

2. **注册到 Agent**

```python
agent.register_tool("generate_meme", generate_meme)
```

### 测试验证

```python
result = generate_meme("不想努力", template="drake")

assert result["status"] == "success"
assert os.path.exists(result["image_path"])
print("✓ 接口验证通过")
```

---

## 🖥 成员 D：前端 UI 对接

### 使用 Agent 的步骤

1. **初始化 Agent（在 app 启动时）**

```python
# streamlit_app.py
import streamlit as st
from member_b_agent.agent.agent_core import create_agent
from member_b_agent.agent.tools import setup_production_tools

# 导入成员 A 和 C 的工具
from member_a_search import search_meme
from member_c_generate import generate_meme

@st.cache_resource
def init_agent():
    agent = create_agent(
        api_key=os.getenv("SAMBANOVA_API_KEY"),
        model="Meta-Llama-3.1-8B-Instruct"
    )
    setup_production_tools(agent, search_meme, generate_meme)
    return agent

agent = init_agent()
```

2. **在 UI 中调用**

```python
# 用户输入
user_query = st.text_input("输入你的情绪：")

if st.button("找梗图"):
    with st.spinner("AI 正在思考..."):
        result = agent.process_query(user_query)
    
    if result["status"] == "success":
        # 显示主要结果
        st.image(result["meme_path"])
        st.write(result["explanation"])
        
        # 显示候选结果（可折叠）
        with st.expander("查看更多候选"):
            for candidate in result["candidates"][:5]:
                st.image(candidate["image_path"])
                st.write(f"相似度: {candidate['score']:.2f}")
        
        # Debug 面板（可选）
        with st.expander("调试信息"):
            st.json(result["reasoning_steps"])
    else:
        st.error(f"出错了：{result.get('error')}")
```

3. **支持下载**

```python
if result.get("meme_path"):
    with open(result["meme_path"], "rb") as f:
        st.download_button(
            label="下载 Meme",
            data=f,
            file_name="meme.png",
            mime="image/png"
        )
```

---

## 📊 成员 E：数据模块对接

### 你需要提供的数据

1. **Meme 元数据文件**

```json
{
    "memes": [
        {
            "id": "001",
            "path": "dataset/train/001.jpg",
            "tags": ["tired", "exhausted", "sleep"],
            "emotion": "tired",
            "description": "疲惫的表情"
        },
        ...
    ],
    "emotion_tags": ["happy", "sad", "tired", "angry", ...],
    "statistics": {
        "total_memes": 3200,
        "emotions_distribution": {...}
    }
}
```

2. **加载元数据供 Agent 使用**

```python
import json

# Agent 初始化时加载
with open("data/meme_metadata.json") as f:
    metadata = json.load(f)

# 可以注入到配置中
agent.metadata = metadata

# 或在 classify_sentiment 中使用
available_emotions = metadata["emotion_tags"]
```

---

## 🧪 成员 F：测试模块对接

### 你需要测试的接口

1. **Agent 功能测试**

```python
import pytest
from member_b_agent.agent.agent_core import create_agent
from member_b_agent.agent.tools import setup_mock_tools

def test_agent_with_real_tools():
    """测试 Agent 与真实工具的集成"""
    agent = create_agent(api_key="test-key")
    
    # 使用真实工具
    from member_a_search import search_meme
    from member_c_generate import generate_meme
    
    agent.register_tool("search_meme", search_meme)
    agent.register_tool("generate_meme", generate_meme)
    
    result = agent.process_query("我累了")
    
    assert result["status"] == "success"
    assert result["meme_path"] is not None
```

2. **性能测试**

```python
import time

def test_agent_performance():
    """测试 Agent 响应时间"""
    agent = create_agent(api_key="your-key")
    setup_mock_tools(agent)
    
    start = time.time()
    result = agent.process_query("测试")
    duration = time.time() - start
    
    assert duration < 3.0, "Agent 响应时间应 < 3s"
    print(f"响应时间: {duration:.2f}s")
```

3. **准确性测试**

```python
def test_agent_accuracy():
    """测试 Agent 推荐准确性"""
    test_cases = [
        ("我累了", ["tired", "exhausted"]),
        ("太开心了", ["happy", "joy"]),
        ("无语", ["speechless", "facepalm"])
    ]
    
    agent = create_agent(api_key="your-key")
    setup_mock_tools(agent)
    
    for query, expected_tags in test_cases:
        result = agent.process_query(query)
        
        # 检查返回的 meme 标签是否匹配
        if result.get("candidates"):
            tags = result["candidates"][0].get("tags", [])
            assert any(t in tags for t in expected_tags)
```

---

## 🔄 完整集成示例

### 项目主入口

```python
# main.py - 完整集成示例

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 1. 导入所有模块
from member_a_search.faiss_index import FaissSearcher
from member_c_generate.template_generator import TemplateGenerator
from member_b_agent.agent.agent_core import create_agent

# 2. 初始化各模块
searcher = FaissSearcher("data/faiss.index")
generator = TemplateGenerator("templates/")

# 3. 定义适配函数
def search_meme(query: str, top_k: int = 5):
    results = searcher.search(query, k=top_k)
    return {
        "query": query,
        "results": [
            {
                "image_path": r["path"],
                "score": r["similarity"],
                "tags": r["tags"]
            }
            for r in results
        ]
    }

def generate_meme(text: str, template: str = "drake"):
    path = generator.generate(template, text)
    return {
        "image_path": path,
        "template": template,
        "text": text,
        "status": "success"
    }

# 4. 创建 Agent 并注册工具
agent = create_agent(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    model="Meta-Llama-3.1-8B-Instruct"
)

agent.register_tool("search_meme", search_meme)
agent.register_tool("generate_meme", generate_meme)

# 5. 测试
if __name__ == "__main__":
    test_query = "我真的不想努力了"
    
    print(f"测试查询: {test_query}")
    result = agent.process_query(test_query, debug=True)
    
    print(f"\n结果:")
    print(f"  Meme: {result.get('meme_path')}")
    print(f"  理由: {result.get('explanation')}")
    print(f"  来源: {result.get('source')}")
```

---

## ⚠️ 常见问题

### Q1: 工具返回格式不对怎么办？

**A:** 确保返回值是 Dict 类型，包含必需的字段：

```python
def search_meme(query, top_k):
    try:
        # 你的实现
        results = ...
        
        return {
            "query": query,
            "results": results  # 必需
        }
    except Exception as e:
        return {"error": str(e)}
```

### Q2: Agent 不调用我的工具？

**A:** 检查：
1. 工具是否已注册：`agent.tool_functions`
2. 工具名称是否正确（必须是 `search_meme` 或 `generate_meme`）
3. API key 是否有效

### Q3: 如何测试集成？

**A:** 使用 mock 工具先测试 Agent，然后逐步替换：

```python
from member_b_agent.agent.tools import mock_search_meme

# 第一步：用 mock 测试
agent.register_tool("search_meme", mock_search_meme)

# 第二步：用你的真实工具
agent.register_tool("search_meme", my_real_search_meme)
```

---

## 📞 联系对接

| 成员 | 负责内容 | 提供接口 |
|------|---------|---------|
| 成员 A | 检索模块 | `search_meme()` |
| 成员 C | 生成模块 | `generate_meme()` |
| 成员 D | 前端 UI | 集成 Agent |
| 成员 E | 数据集 | 元数据文件 |
| 成员 F | 测试文档 | 测试用例 |

**成员 B 联系方式：**
- 提供：Agent 核心逻辑、工具调用框架
- 接口：`agent.register_tool(name, func)`

---

## ✅ 对接检查清单

### 成员 A
- [ ] `search_meme` 函数实现完成
- [ ] 返回格式符合接口定义
- [ ] FAISS 索引加载正常
- [ ] 响应时间 < 200ms

### 成员 C
- [ ] `generate_meme` 函数实现完成
- [ ] 支持至少 3 种模板
- [ ] 生成时间 < 0.5s
- [ ] 图片保存正常

### 成员 D
- [ ] Agent 初始化成功
- [ ] UI 能调用 `process_query`
- [ ] 结果展示正常
- [ ] 支持下载功能

### 成员 E
- [ ] 元数据文件格式正确
- [ ] 标签系统完整
- [ ] 数据集路径正确

### 成员 F
- [ ] 集成测试通过
- [ ] 性能测试达标
- [ ] 文档更新完成

---

完成所有对接后，整个 Meme Agent 系统就能正常工作了！🎉

