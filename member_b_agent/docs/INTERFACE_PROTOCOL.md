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

### 🌐 HTTP API 方式（推荐）

**适合：React、Vue、Next.js、原生 JavaScript 等所有 Web 前端**

#### 启动 API 服务

```bash
cd member_b_agent/api
./start.sh
```

服务地址：
- **API：** http://localhost:8000
- **文档：** http://localhost:8000/docs （Swagger UI）

---

### 📡 核心 API 接口

#### 1. 查询梗图（POST /api/query）

**请求：**
```javascript
fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: "我太累了",
    session_id: null  // 可选，用于多轮对话
  })
})
```

**响应（成功）：**
```json
{
  "success": true,
  "meme_path": "dataset/train/tired_001.jpg",
  "explanation": "这张图完美表达了累到不想动的感觉~",
  "source": "search",
  "session_id": "6d19d562-b793-4c87-a615-cceac0e43e4f"
}
```

**响应（失败）：**
```json
{
  "success": false,
  "error": "API 服务暂时不可用，请稍后重试",
  "session_id": null
}
```

#### 2. 清除会话（DELETE /api/session/{id}）

```javascript
fetch(`http://localhost:8000/api/session/${sessionId}`, {
  method: 'DELETE'
})
```

#### 3. 健康检查（GET /health）

```javascript
fetch('http://localhost:8000/health')
// 响应: {"status": "healthy", "version": "2.0.0"}
```

---

### 💻 前端集成示例

#### React 完整示例

```jsx
import { useState } from 'react';

function MemeAgent() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const queryMeme = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          text: input,
          session_id: sessionId
        })
      });
      
      const data = await res.json();
      
      if (data.success) {
        setResult(data);
        setSessionId(data.session_id);  // 保存用于下次对话
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('网络请求失败');
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    if (sessionId) {
      await fetch(`http://localhost:8000/api/session/${sessionId}`, {
        method: 'DELETE'
      });
      setSessionId(null);
      setResult(null);
    }
  };

  return (
    <div className="meme-agent">
      <input 
        value={input} 
        onChange={(e) => setInput(e.target.value)}
        placeholder="输入你的情绪..."
        disabled={loading}
      />
      
      <button onClick={queryMeme} disabled={loading || !input}>
        {loading ? '思考中...' : '找梗图'}
      </button>
      
      {sessionId && (
        <button onClick={clearChat}>新对话</button>
      )}
      
      {error && <div className="error">{error}</div>}
      
      {result && (
        <div className="result">
          <img 
            src={`http://localhost:8000/${result.meme_path}`} 
            alt="meme"
          />
          <p>{result.explanation}</p>
          <small>来源: {result.source}</small>
        </div>
      )}
    </div>
  );
}

export default MemeAgent;
```

#### Vue 3 完整示例

```vue
<template>
  <div class="meme-agent">
    <input 
      v-model="input" 
      placeholder="输入你的情绪..."
      :disabled="loading"
      @keyup.enter="queryMeme"
    />
    
    <button @click="queryMeme" :disabled="loading || !input">
      {{ loading ? '思考中...' : '找梗图' }}
    </button>
    
    <button v-if="sessionId" @click="clearChat">新对话</button>
    
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="result" class="result">
      <img :src="`http://localhost:8000/${result.meme_path}`" alt="meme" />
      <p>{{ result.explanation }}</p>
      <small>来源: {{ result.source }}</small>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const input = ref('');
const result = ref(null);
const sessionId = ref(null);
const loading = ref(false);
const error = ref(null);

const queryMeme = async () => {
  if (!input.value) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const res = await fetch('http://localhost:8000/api/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        text: input.value,
        session_id: sessionId.value
      })
    });
    
    const data = await res.json();
    
    if (data.success) {
      result.value = data;
      sessionId.value = data.session_id;
    } else {
      error.value = data.error;
    }
  } catch (err) {
    error.value = '网络请求失败';
  } finally {
    loading.value = false;
  }
};

const clearChat = async () => {
  if (sessionId.value) {
    await fetch(`http://localhost:8000/api/session/${sessionId.value}`, {
      method: 'DELETE'
    });
    sessionId.value = null;
    result.value = null;
  }
};
</script>
```

#### 原生 JavaScript

```javascript
class MemeAgentClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }

  async query(text) {
    try {
      const response = await fetch(`${this.baseUrl}/api/query`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          text: text,
          session_id: this.sessionId
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        this.sessionId = data.session_id;
        return data;
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      console.error('查询失败:', error);
      throw error;
    }
  }

  async clearSession() {
    if (this.sessionId) {
      await fetch(`${this.baseUrl}/api/session/${this.sessionId}`, {
        method: 'DELETE'
      });
      this.sessionId = null;
    }
  }
}

// 使用示例
const agent = new MemeAgentClient();

document.getElementById('query-btn').onclick = async () => {
  const input = document.getElementById('user-input').value;
  
  try {
    const result = await agent.query(input);
    
    // 显示结果
    document.getElementById('meme-img').src = 
      `http://localhost:8000/${result.meme_path}`;
    document.getElementById('explanation').textContent = 
      result.explanation;
  } catch (error) {
    alert(`错误: ${error.message}`);
  }
};
```

---

### 🔄 多轮对话示例

```javascript
// 保持会话 ID 实现连续对话
let currentSessionId = null;

async function chat(userInput) {
  const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      text: userInput,
      session_id: currentSessionId  // 传入之前的 session_id
    })
  });
  
  const data = await response.json();
  currentSessionId = data.session_id;  // 保存新的 session_id
  return data;
}

// 对话流程
const result1 = await chat("我太累了");
// Agent 返回累的梗图

const result2 = await chat("再来一张");
// Agent 记得上下文，返回另一张累的梗图

const result3 = await chat("换个开心的");
// Agent 知道要换主题了
```

---

### 🛠️ 常见问题

#### Q1: CORS 跨域问题？

**A:** API 服务已配置允许跨域。如果仍有问题，检查 `api/api_server.py` 中的 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 改为你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Q2: 图片如何显示？

**A:** 方式 1（推荐）- 直接使用返回的路径：
```html
<img src={`http://localhost:8000/${result.meme_path}`} />
```

方式 2 - 配置静态文件服务（需要后端配置）

#### Q3: 如何处理加载状态？

**A:** 使用 loading 状态：
```javascript
const [loading, setLoading] = useState(false);

const query = async () => {
  setLoading(true);
  try {
    // API 调用
  } finally {
    setLoading(false);
  }
};
```

#### Q4: 需要部署到生产环境怎么办？

**A:** 
1. 修改 `baseUrl` 为生产环境地址
2. 配置 CORS 为具体域名
3. 使用 Nginx/Docker 部署后端服务

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

