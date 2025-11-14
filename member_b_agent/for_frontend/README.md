# 🎨 前端同学看这里！

**这个文件夹是专门为你准备的，包含了所有你需要的内容。**

---

## 📁 文件说明

```
for_frontend/
├── README.md              ← 你正在看的文件
├── GUIDE.md              ← 5分钟快速上手指南 ⭐
├── agent_service.py      ← 核心文件（导入这个）⭐
└── examples/             ← 完整示例代码
    ├── streamlit_app.py  ← Streamlit 示例
    └── gradio_app.py     ← Gradio 示例
```

---

## 🚀 3步快速开始

### 1️⃣ 阅读文档（5分钟）

```bash
打开 GUIDE.md，里面有详细的使用说明
```

### 2️⃣ 测试 Agent（1分钟）

```bash
cd for_frontend
python agent_service.py
```

会看到简洁的测试输出。

### 3️⃣ 参考示例开发

```python
# 导入（就这一个文件）
from agent_service import MemeAgentService

# 使用
agent = MemeAgentService()
result = agent.query("我太累了")

if result["success"]:
    print(result["meme_path"])      # 图片路径
    print(result["explanation"])    # 推荐理由
```

---

## 📖 返回格式

### ✅ 成功时

```json
{
    "success": true,
    "meme_path": "dataset/train/happy_001.jpg",
    "explanation": "这张图完美表达了开心的心情~",
    "source": "search"
}
```

### ❌ 失败时

```json
{
    "success": false,
    "error": "API 服务暂时不可用，请稍后重试"
}
```

---

## 💡 核心代码（直接复制）

### Streamlit

```python
import streamlit as st
from agent_service import MemeAgentService

@st.cache_resource
def get_agent():
    return MemeAgentService()

agent = get_agent()
st.title("🎭 Meme Agent")

user_input = st.text_input("输入你的情绪：")
if st.button("找梗图") and user_input:
    with st.spinner("AI 正在思考..."):
        result = agent.query(user_input)
    
    if result["success"]:
        st.image(result["meme_path"])
        st.success(result["explanation"])
    else:
        st.error(result["error"])
```

### Gradio

```python
import gradio as gr
from agent_service import MemeAgentService

agent = MemeAgentService()

def process(text):
    result = agent.query(text)
    if result["success"]:
        return result["meme_path"], result["explanation"]
    return None, f"错误: {result['error']}"

demo = gr.Interface(
    fn=process,
    inputs=gr.Textbox(label="输入情绪"),
    outputs=[gr.Image(label="Meme"), gr.Textbox(label="推荐理由")],
    title="🎭 Meme Agent"
)
demo.launch()
```

---

## 🆘 常见问题

### Q: 图片路径怎么使用？

**A:** 直接传给前端框架：

```python
# Streamlit
st.image(result["meme_path"])

# Gradio
return result["meme_path"]

# HTML
<img src="{{ result['meme_path'] }}">
```

### Q: 看到很多技术日志？

**A:** 在初始化时设置 `verbose=False`（默认已是）：

```python
agent = MemeAgentService(verbose=False)
```

### Q: 如何测试？

**A:** 

```bash
python agent_service.py
```

### Q: 出错了怎么办？

**A:** 

1. 检查返回值的 `success` 字段
2. 如果是 `False`，显示 `error` 字段给用户
3. 需要调试时，设置 `verbose=True`

---

## 📋 接下来做什么

1. ✅ 阅读 `GUIDE.md` 了解详细用法
2. ✅ 运行 `python agent_service.py` 测试
3. ✅ 参考 `examples/` 中的完整示例
4. ✅ 开始集成到你的前端应用

---

## 📞 需要帮助？

有问题随时联系成员 B（Agent 负责人）！

这个文件夹里的所有内容都是为前端准备的，简单易懂 😊

