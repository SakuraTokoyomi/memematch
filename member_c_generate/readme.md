# 📝 表情包生成模块 - 使用说明

一个简单的表情包生成功能，支持 Drake、Doge、Wojak 三种经典模板。

------

## ✨ 功能特性

- ✅ 支持三种经典模板（Drake、Doge、Wojak）
- ✅ 完整中文支持，自动换行
- ✅ 可自定义字体大小、颜色
- ✅ 返回标准 JSON 格式
- ✅ 生成速度 < 0.5s

------

## 🚀 快速使用

Python



```python
from meme_generator import generate_meme

# 生成表情包
result = generate_meme(
    text="写文档|写代码",
    template="drake"
)

# 检查结果
if result["success"]:
    print(f"✅ 生成成功: {result['data']['image_path']}")
else:
    print(f"❌ 生成失败: {result['error']}")
```

------

## 📖 API 说明

### 函数签名

Python



```python
def generate_meme(
    text: str,
    template: str = "drake",
    options: dict = None
) -> dict
```

### 参数说明

| 参数       | 类型   | 必填 | 默认值    | 说明           |
| ---------- | ------ | ---- | --------- | -------------- |
| `text`     | `str`  | ✅    | -         | 显示的文字内容 |
| `template` | `str`  | ❌    | `"drake"` | 模板类型       |
| `options`  | `dict` | ❌    | `None`    | 可选配置       |

### Options 配置

Python



```python
{
    "font_size": 32,           # 字体大小 (20-60)
    "font_family": "genshen",  # 字体名称
    "text_color": "#FFFFFF",   # 文字颜色 (Hex)
    "output_format": "png"     # 输出格式 (png/jpg)
}
```

### 返回格式

**成功时：**

Python



```python
{
    "success": True,
    "data": {
        "image_path": "outputs/generated_drake_12345.png",
        "template": "drake",
        "text": "写文档|写代码",
        "dimensions": [600, 600],
        "file_size": 85000,
        "format": "png"
    },
    "metadata": {
        "generation_time": 0.35,
        "template_version": "1.0",
        "parameters_used": {...},
        "timestamp": "2024-01-15T10:30:00"
    }
}
```

**失败时：**

Python



```python
{
    "success": False,
    "error": "Template 'unknown' not found",
    "error_code": "TEMPLATE_NOT_FOUND",
    "metadata": {
        "available_templates": ["drake", "doge", "wojak"]
    }
}
```

------

## 🎭 模板说明

### 1. Drake 模板 (`drake`)

**用途**：对比两种观点或选择

**格式**：使用 `|` 分隔上下两段文字

Python



```python
generate_meme("写文档|写代码", "drake")
```

**效果**：

text



```
┌─────┬──────────┐
│  ×  │  写文档  │  ← 拒绝
├─────┼──────────┤
│  ✓  │  写代码  │  ← 接受
└─────┴──────────┘
```

------

### 2. Doge 模板 (`doge`)

**用途**：幽默、调侃表达

**格式**：单行文本

Python



```python
generate_meme("如此优雅的代码", "doge")
```

**效果**：文字显示在底部，柴犬表情背景

------

### 3. Wojak 模板 (`wojak`)

**用途**：表达悲伤、无奈

**格式**：单行文本

Python



```python
generate_meme("又要加班了", "wojak")
```

**效果**：文字显示在底部，悲伤表情背景

------

## 💡 使用示例

### 基本用法

Python



```python
from meme_generator import generate_meme

# Drake 模板
result = generate_meme("开会|写代码", "drake")

# Doge 模板
result = generate_meme("如此优雅", "doge")

# Wojak 模板
result = generate_meme("又要加班了", "wojak")
```

### 自定义样式

Python



```python
# 自定义字体大小和颜色
result = generate_meme(
    text="Python|Java",
    template="drake",
    options={
        "font_size": 40,
        "text_color": "#FFD700"
    }
)
```

### 批量生成

Python



```python
memes = [
    {"text": "理论|实践", "template": "drake"},
    {"text": "如此优雅", "template": "doge"},
    {"text": "又延期了", "template": "wojak"}
]

for meme in memes:
    result = generate_meme(meme["text"], meme["template"])
    if result["success"]:
        print(f"✅ {result['data']['image_path']}")
```

### 错误处理

Python



```python
result = generate_meme("测试", "drake")

if result["success"]:
    image_path = result["data"]["image_path"]
    print(f"生成成功: {image_path}")
else:
    print(f"错误: {result['error']}")
    print(f"错误代码: {result['error_code']}")
```