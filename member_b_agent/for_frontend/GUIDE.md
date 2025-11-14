# 🎨 前端对接指南

**给成员 D（前端负责人）：** 这是最简洁的对接说明，5分钟看完就能开始集成！

---

## 🚀 快速开始（3步）

### 1. 导入 Agent 服务

```python
from agent_service import MemeAgentService

# 初始化（verbose=False 隐藏技术日志）
agent = MemeAgentService(use_mock=True, verbose=False)
```

### 2. 调用查询

```python
# 用户输入
user_input = "我太累了"

# 调用 Agent
result = agent.query(user_input)
```

### 3. 使用结果

```python
if result["success"]:
    # 成功 - 显示 meme
    print(f"Meme 图片: {result['meme_path']}")
    print(f"推荐理由: {result['explanation']}")
else:
    # 失败 - 显示错误
    print(f"错误: {result['error']}")
```

**就这么简单！** ✅

---

## 📊 API 返回格式

### ✅ 成功时

```python
{
    "success": True,
    "meme_path": "dataset/train/happy_001.jpg",  # 图片路径
    "explanation": "这张图完美表达了开心的心情~",  # 推荐理由
    "source": "search",  # "search"=检索, "generated"=生成
    "candidates": [...]  # 可选：其他候选（top-k）
}
```

### ❌ 失败时

```python
{
    "success": False,
    "error": "API 服务暂时不可用"  # 错误描述
}
```

---

## 🎯 Streamlit 完整示例

```python
import streamlit as st
from integration_for_frontend import MemeAgentService

# 初始化（缓存，只运行一次）
@st.cache_resource
def get_agent():
    return MemeAgentService(use_mock=True, verbose=False)

agent = get_agent()

# UI
st.title("🎭 Meme Agent")
user_input = st.text_input("输入你的情绪：")

if st.button("找梗图"):
    if user_input:
        with st.spinner("AI 正在思考..."):
            result = agent.query(user_input)
      
        if result["success"]:
            st.image(result["meme_path"])
            st.success(result["explanation"])
        else:
            st.error(result["error"])
```

**运行：** `streamlit run your_app.py`

---

## 🎨 Gradio 完整示例

```python
import gradio as gr
from integration_for_frontend import MemeAgentService

agent = MemeAgentService(use_mock=True, verbose=False)

def process(user_input):
    result = agent.query(user_input)
    if result["success"]:
        return result["meme_path"], result["explanation"]
    else:
        return None, f"错误: {result['error']}"

# 创建界面
demo = gr.Interface(
    fn=process,
    inputs=gr.Textbox(label="输入情绪", placeholder="例如：我太累了"),
    outputs=[
        gr.Image(label="Meme"),
        gr.Textbox(label="推荐理由")
    ],
    title="🎭 Meme Agent",
    description="AI 驱动的智能梗图助手"
)

demo.launch()
```

**运行：** `python your_app.py`

---

## 💡 参数说明

### `MemeAgentService(use_mock, verbose)`

| 参数         | 类型 | 说明                         | 默认值    |
| ------------ | ---- | ---------------------------- | --------- |
| `use_mock` | bool | 是否使用模拟数据（开发时用） | `False` |
| `verbose`  | bool | 是否显示详细日志（建议关闭） | `False` |

**建议：**

- 开发阶段：`use_mock=True, verbose=False`
- 正式上线：`use_mock=False, verbose=False`

### `agent.query(user_input, max_iterations)`

| 参数               | 类型 | 说明                       | 默认值 |
| ------------------ | ---- | -------------------------- | ------ |
| `user_input`     | str  | 用户输入的文本             | 必填   |
| `max_iterations` | int  | 最大推理次数（一般不用改） | `4`  |

---

## 🔧 调试技巧

### 看不到输出？

```python
# 开启详细日志
agent = MemeAgentService(use_mock=True, verbose=True)
```

### 想看完整返回值？

```python
import json
result = agent.query("测试")
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 测试是否工作？

```bash
# 运行测试脚本
cd member_b_agent
python integration_for_frontend.py api
```

应该看到简洁的输出（没有一堆 INFO 日志）：

```
初始化 Agent...
✓ Agent 初始化完成

查询: 我太累了
  ✓ 成功
  Meme: dataset/train/tired_001.jpg
  理由: 这张图完美表达了...
```

---

## 🆘 常见问题

### Q1: 返回的图片路径怎么用？

**A:** 直接传给前端框架：

```python
# Streamlit
st.image(result["meme_path"])

# Gradio
return result["meme_path"]

# HTML
f'<img src="{result["meme_path"]}">'
```

### Q2: 如何显示候选结果（top-k）？

**A:**

```python
result = agent.query("查询")
if result["success"] and "candidates" in result:
    for candidate in result["candidates"][:5]:
        print(f"候选: {candidate['image_path']}")
        print(f"分数: {candidate['score']}")
```

### Q3: 错误怎么处理？

**A:**

```python
result = agent.query("查询")
if not result["success"]:
    error_msg = result["error"]
  
    # 友好提示给用户
    if "API" in error_msg:
        show_message("服务暂时不可用，请稍后重试")
    elif "超时" in error_msg:
        show_message("请求超时，请重试")
    else:
        show_message("出错了，请重试")
```

### Q4: 如何添加加载动画？

**A:**

```python
# Streamlit
with st.spinner("AI 正在思考..."):
    result = agent.query(user_input)

# Gradio（自带加载动画）
# 或在 process 函数开始时显示 loading
```

### Q5: 可以缓存结果吗？

**A:** 可以！

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(user_input):
    return agent.query(user_input)

# 使用
result = cached_query("开心")  # 第二次会很快
```

---

## 📁 文件位置

```
member_b_agent/
├── integration_for_frontend.py  ← 你要导入的文件 ⭐
├── agent/                       ← Agent 核心（不用管）
├── examples/                    ← 示例代码
└── docs/                        ← 详细文档
```

**你只需要关注 `integration_for_frontend.py`！**

---

## 🎯 完整工作流程

```python
# 1. 导入
from integration_for_frontend import MemeAgentService

# 2. 初始化（整个应用只初始化一次）
agent = MemeAgentService(use_mock=True, verbose=False)

# 3. 在用户交互时调用
def handle_user_input(text):
    result = agent.query(text)
  
    if result["success"]:
        # 显示 meme
        display_image(result["meme_path"])
        display_text(result["explanation"])
    else:
        # 显示错误
        display_error(result["error"])
```

---

## 🚀 下一步

1. **现在就试试：**

   ```bash
   python integration_for_frontend.py api
   ```
2. **参考示例：**

   - Streamlit 示例在 `integration_for_frontend.py` 中
   - Gradio 示例也在里面
3. **遇到问题：**

   - 先开启 `verbose=True` 看日志
   - 检查 `result` 的完整内容
   - 联系成员 B

---

## ✅ 检查清单

开始集成前确认：

- [ ] 已安装依赖：`pip install streamlit` 或 `pip install gradio`
- [ ] 已测试 API：`python integration_for_frontend.py api`
- [ ] 理解返回格式：`success`, `meme_path`, `explanation`
- [ ] 知道如何处理错误：检查 `result["success"]`

全部打勾就可以开始了！

---

**有问题随时问成员 B！** 🤝

这个文档就是为你准备的，简单明了，直接上手！
