# 📡 接口协议文档

**版本：** v2.0  
**更新日期：** 2024-11-14  
**阅读对象：** 成员 A（检索）、成员 C（生成）、成员 D（前端）

---

## 📋 文档概述

本文档定义了 Meme Agent 项目中各模块之间的接口协议，确保各成员能够顺利对接。

**模块关系：**
```
前端 (D) ←→ Agent (B) ←→ 检索模块 (A)
                   ↓
              生成模块 (C)
```

---

## 1️⃣ 成员 A：检索模块接口

### 函数签名

```python
def search_meme(
    query: str, 
    top_k: int = 5,
    min_score: float = 0.0
) -> dict
```

### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | str | ✅ | - | 英文检索关键词，如 "tired reaction meme" |
| `top_k` | int | ❌ | 5 | 返回结果数量 |
| `min_score` | float | ❌ | 0.0 | 最小相似度阈值 (0-1) |

### 返回格式

```json
{
    "success": true,
    "data": {
        "query": "tired reaction meme",
        "results": [
            {
                "image_path": "dataset/train/tired_001.jpg",
                "score": 0.92,
                "tags": ["tired", "exhausted", "sleep"],
                "metadata": {
                    "file_size": 102400,
                    "dimensions": [512, 512],
                    "format": "jpg"
                }
            }
        ],
        "total": 3,
        "filtered": 2
    },
    "metadata": {
        "search_time": 0.15,
        "index_size": 3200,
        "timestamp": "2024-11-14T10:30:00"
    }
}
```

### 错误返回

```json
{
    "success": false,
    "error": "FAISS index not found",
    "error_code": "INDEX_NOT_FOUND"
}
```

### 实现示例

```python
def search_meme(query: str, top_k: int = 5, min_score: float = 0.0):
    import time
    start = time.time()
    
    try:
        # 你的 FAISS 检索逻辑
        results = your_faiss_search(query, top_k)
        
        # 过滤低分结果
        filtered = [r for r in results if r['score'] >= min_score]
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results": filtered,
                "total": len(filtered),
                "filtered": len(results) - len(filtered)
            },
            "metadata": {
                "search_time": time.time() - start,
                "index_size": len(your_index),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "SEARCH_ERROR"
        }
```

### 注意事项

- ✅ `results` 必须按 `score` 从高到低排序
- ✅ `image_path` 必须是项目根目录的相对路径
- ✅ `score` 范围为 0-1，越接近 1 越相关
- ✅ 必须有 `success` 字段标识成功/失败

---

## 2️⃣ 成员 C：生成模块接口

### 函数签名

```python
def generate_meme(
    text: str,
    template: str = "drake",
    options: dict = None
) -> dict
```

### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | str | ✅ | - | 要显示在 meme 上的文字 |
| `template` | str | ❌ | "drake" | 模板类型 |
| `options` | dict | ❌ | None | 生成选项（字体、颜色等） |

### 支持的模板

- `"drake"` - Drake 模板（上下对比）
- `"doge"` - Doge 模板（柴犬）
- `"wojak"` - Wojak 模板
- `"distracted_boyfriend"` - 分心男友
- `"two_buttons"` - 两个按钮

### options 参数（可选）

```python
{
    "font_size": 32,           # 字体大小
    "font_family": "Arial",    # 字体名称
    "text_color": "#FFFFFF",   # 文字颜色（hex）
    "output_format": "png"     # 输出格式
}
```

### 返回格式

```json
{
    "success": true,
    "data": {
        "image_path": "outputs/generated_drake_12345.png",
        "template": "drake",
        "text": "不想努力了",
        "dimensions": [600, 600],
        "file_size": 85000,
        "format": "png"
    },
    "metadata": {
        "generation_time": 0.35,
        "template_version": "1.0",
        "parameters_used": {
            "font_size": 32,
            "font_family": "Arial"
        },
        "timestamp": "2024-11-14T10:30:00"
    }
}
```

### 错误返回

```json
{
    "success": false,
    "error": "Template 'unknown' not found",
    "error_code": "TEMPLATE_NOT_FOUND",
    "metadata": {
        "available_templates": ["drake", "doge", "wojak"]
    }
}
```

### 实现示例

```python
def generate_meme(text: str, template: str = "drake", options: dict = None):
    import time
    start = time.time()
    
    valid_templates = ["drake", "doge", "wojak", "distracted_boyfriend", "two_buttons"]
    
    try:
        if template not in valid_templates:
            return {
                "success": False,
                "error": f"Template '{template}' not found",
                "error_code": "TEMPLATE_NOT_FOUND",
                "metadata": {"available_templates": valid_templates}
            }
        
        # 你的生成逻辑
        output_path = your_template_engine(text, template, options)
        
        return {
            "success": True,
            "data": {
                "image_path": output_path,
                "template": template,
                "text": text,
                "dimensions": [600, 600],
                "file_size": os.path.getsize(output_path),
                "format": "png"
            },
            "metadata": {
                "generation_time": time.time() - start,
                "template_version": "1.0",
                "parameters_used": options or {},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "GENERATION_ERROR"
        }
```

### 注意事项

- ✅ 生成的图片保存到 `outputs/` 目录
- ✅ 文件名建议格式：`generated_{template}_{hash}.png`
- ✅ 文字应自动换行，避免超出边界
- ✅ 生成时间尽量控制在 0.5s 以内

---

## 3️⃣ 成员 D：前端集成接口

### 导入 Agent 服务

```python
from agent_service import MemeAgentService

# 初始化（启用会话管理）
agent = MemeAgentService(enable_session=True)
```

### 单次查询

```python
result = agent.query("我太累了")

# 返回格式
{
    "success": True,
    "meme_path": "dataset/train/tired_001.jpg",
    "explanation": "这张图完美表达了累到不想动的感觉~",
    "source": "search",          # "search" 或 "generated"
    "session_id": "uuid-string"  # 会话 ID
}
```

### 多轮对话

```python
# 第一轮
result1 = agent.query("我太累了")
session_id = result1["session_id"]

# 第二轮（继续对话）
result2 = agent.query("再来一张", session_id=session_id)

# 第三轮
result3 = agent.query("换个开心的", session_id=session_id)

# 结束对话
agent.clear_session(session_id)
```

### API 返回格式

#### 成功响应

```json
{
    "success": true,
    "meme_path": "dataset/train/happy_001.jpg",
    "explanation": "这张图完美表达了你的心情！",
    "source": "search",
    "session_id": "6d19d562-b793-4c87-a615-cceac0e43e4f",
    "candidates": [...]
}
```

#### 失败响应

```json
{
    "success": false,
    "error": "API 服务暂时不可用，请稍后重试",
    "session_id": "6d19d562-b793-4c87-a615-cceac0e43e4f"
}
```

### Web API 封装（Flask）

```python
from flask import Flask, request, jsonify
from agent_service import MemeAgentService

app = Flask(__name__)
agent = MemeAgentService(enable_session=True)

@app.route('/api/meme', methods=['POST'])
def get_meme():
    data = request.get_json()
    user_input = data.get('text')
    session_id = data.get('session_id')  # 可选
    
    result = agent.query(user_input, session_id=session_id)
    return jsonify(result)

@app.route('/api/session/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    success = agent.clear_session(session_id)
    return jsonify({"success": success})
```

### 使用场景

#### 场景 1: 单次查询（不需要上下文）

```python
agent = MemeAgentService(enable_session=False)
result = agent.query("开心")
# 每次都是独立查询
```

#### 场景 2: 连续对话（需要上下文）

```python
agent = MemeAgentService(enable_session=True)

# 用户对话流程
result1 = agent.query("我太累了")
session_id = result1["session_id"]

result2 = agent.query("再来一张", session_id=session_id)
# Agent 知道之前说的是"我太累了"

result3 = agent.query("换个开心的", session_id=session_id)
# Agent 知道要换主题了
```

---

## 🔧 错误码说明

### 检索模块（成员 A）

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| `INDEX_NOT_FOUND` | 索引文件不存在 | 检查 FAISS 索引是否已加载 |
| `SEARCH_ERROR` | 检索失败 | 查看详细错误信息 |

### 生成模块（成员 C）

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| `TEMPLATE_NOT_FOUND` | 模板不存在 | 使用支持的模板名称 |
| `GENERATION_ERROR` | 生成失败 | 查看详细错误信息 |

---

## 📊 数据流说明

### 用户查询流程

```
1. 前端 → Agent
   POST {"text": "我太累了", "session_id": "..."}

2. Agent → 成员 A（检索）
   search_meme("tired reaction meme", top_k=5)

3. 成员 A → Agent
   返回检索结果（带 score）

4. Agent 判断：
   - score >= 0.6: 使用检索结果
   - score < 0.6: 调用成员 C 生成

5. Agent → 成员 C（如果需要）
   generate_meme("累", template="drake")

6. 成员 C → Agent
   返回生成的图片路径

7. Agent → 前端
   {"success": true, "meme_path": "...", "explanation": "..."}
```

---

## ✅ 对接检查清单

### 成员 A（检索）
- [ ] 返回格式包含 `success` 字段
- [ ] `results` 包含 `score`、`image_path`、`tags`
- [ ] `results` 按 `score` 降序排列
- [ ] 支持 `min_score` 参数过滤
- [ ] 错误时返回 `success: false` 和 `error`

### 成员 C（生成）
- [ ] 返回格式包含 `success` 字段
- [ ] `data` 包含 `image_path`、`template`、`text`
- [ ] 支持至少 3 种模板（drake, doge, wojak）
- [ ] 图片保存到 `outputs/` 目录
- [ ] 错误时返回 `success: false` 和 `error`

### 成员 D（前端）
- [ ] 使用 `agent_service.py` 调用 Agent
- [ ] 检查 `result["success"]` 判断成功/失败
- [ ] 保存 `session_id` 用于多轮对话
- [ ] 显示 `meme_path` 图片
- [ ] 显示 `explanation` 推荐理由
- [ ] 错误时显示 `error` 信息

---

## 📞 联系方式

**有问题随时联系成员 B（Agent 负责人）！**

---

## 📝 版本历史

- **v2.0** (2024-11-14)
  - 统一返回格式 `{success, data, metadata}`
  - 增加会话管理接口
  - 增加错误码系统

- **v1.0** (2024-11-13)
  - 初始版本

