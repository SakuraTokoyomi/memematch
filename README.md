# MemeMatch 🎭

<div align="center">

**智能梗图推荐系统 - 让表情包找对你的心情**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.3+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [技术架构](#-技术架构) • [文档](#-文档) • [贡献指南](#-贡献指南)

</div>

---

## 📖 项目简介

**MemeMatch** 是一个基于大语言模型（LLM）和多模态向量检索的智能梗图推荐系统。用户只需简单描述自己的心情，系统就能：

- 🧠 **理解情绪**：智能识别用户的情绪状态
- 🔍 **精准匹配**：从4600+梗图中找到最契合的表情包
- 🎨 **创意生成**：当找不到合适的图时，自动生成个性化梗图
- 💬 **对话交互**：流式响应，实时展示推理过程

### 在线演示

> 🎥 **演示视频**: [观看效果](docs/demo.mp4)  
> 🌐 **在线体验**: [立即试用](http://memematch.demo.com)

---

## ✨ 功能特性

### 1️⃣ 智能情绪识别
基于 **Meta-Llama-3.3-70B** 大模型，准确提取情绪关键词

```
输入: "我今天工作很顺利，老板还夸奖了我！"
识别: ["顺利", "开心"]
```

### 2️⃣ 多模态检索
结合 **CLIP** 图像编码和 **M3E** 中文文本编码，实现图文语义匹配

- 检索速度: < 0.3s (4600张图片)
- Top-2 准确率: ~85%

### 3️⃣ Top-N 推荐
返回多张候选图片，让用户有更多选择

<div align="center">
<img src="docs/screenshots/top2.png" width="600" alt="Top-2推荐示例" />
</div>

### 4️⃣ 创意生成
点击 **🎨 创意生成** 按钮，系统会：
- LLM生成创意文案（如"开心到飞起"）
- 随机选择梗图模板（Drake/Doge/Wojak）
- 生成个性化梗图

<div align="center">
<img src="docs/screenshots/creative.png" width="600" alt="创意生成示例" />
</div>

### 5️⃣ 流式响应
实时展示推理过程，透明可信

```
💭 思考过程
1. 💡 情绪识别：开心
2. 🔍 梗图检索：找到匹配"开心"的图片（相似度 85%）
```

---

## 🏗️ 技术架构

### 系统架构

```
┌─────────────┐
│   Vue 3     │  前端 (对话界面)
└──────┬──────┘
       │ HTTP/SSE
┌──────▼──────┐
│   FastAPI   │  后端 (API服务)
└──────┬──────┘
       │
   ┌───┴───┬───────┬────────┐
   ▼       ▼       ▼        ▼
┌─────┐ ┌────┐ ┌──────┐ ┌────┐
│Agent│ │搜索│ │生成器│ │会话│
│LLaMA│ │CLIP│ │ PIL  │ │管理│
└─────┘ └────┘ └──────┘ └────┘
```

### 技术栈

**后端**:
- **Web框架**: FastAPI
- **LLM**: Meta-Llama-3.3-70B (SambaNova Cloud)
- **文本编码**: M3E-base (中文优化)
- **图像编码**: CLIP ViT-B-32
- **图像处理**: Pillow

**前端**:
- **框架**: Vue 3
- **构建工具**: Vite
- **HTTP客户端**: Axios + EventSource

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 16+
- 8GB+ 内存

### 一键启动

```bash
# 1. 克隆项目
git clone https://github.com/your-org/memematch.git
cd memematch

# 2. 安装依赖
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. 配置API密钥
export SAMBANOVA_API_KEY="your-api-key"

# 4. 启动服务
./scripts/start.sh

# 5. 打开浏览器
# 访问 http://localhost:3000
```

**详细步骤**: 请查看 [快速启动指南](QUICKSTART.md)

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 端到端延迟 | 1-2s | 从输入到返回结果 |
| 情绪提取 | 0.5-1s | LLM推理时间 |
| 向量检索 | 0.1-0.3s | 4600张图片检索 |
| 图片生成 | 0.2-0.5s | PIL图像处理 |
| Top-2准确率 | ~85% | 用户满意度 |

---

## 📁 目录结构

```
memematch/
├── backend/              # 后端服务
│   ├── agent/           # LLM Agent
│   ├── search/          # 检索引擎
│   ├── generator/       # 图片生成
│   └── api/             # FastAPI服务
├── frontend/            # Vue前端
│   └── src/
│       ├── App.vue      # 主组件
│       └── api/         # API封装
├── data/                # 数据集
│   └── dataset/
│       ├── meme/        # 4600+ 梗图
│       └── index/       # 向量索引
├── scripts/             # 启动脚本
│   ├── start.sh
│   └── stop.sh
├── docs/                # 文档
│   ├── screenshots/     # 截图
│   └── demo.mp4         # 演示视频
└── requirements.txt     # Python依赖
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 快速启动指南 |
| [PROJECT_REPORT.md](PROJECT_REPORT.md) | 详细技术报告 |
| [API文档](http://localhost:8000/docs) | FastAPI自动生成 |

---

## 🎯 使用示例

### 基础查询

```bash
# 终端测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"text": "我今天太开心了"}'
```

**响应**:
```json
{
  "success": true,
  "meme_paths": ["/static/001.jpg", "/static/002.jpg"],
  "explanation": "找到了一张很适合表达'开心'的梗图！",
  "source": "search",
  "count": 2
}
```

### 创意生成

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "我今天太开心了", "keywords": ["开心"]}'
```

**响应**:
```json
{
  "success": true,
  "meme_path": "/generated/creative_20251122_123456.png",
  "explanation": "基于'开心'创作的doge风格梗图，文案：开心到飞起",
  "source": "generated"
}
```

---

## 🛠️ 配置说明

### 后端配置

**Agent配置** (`backend/agent/config.py`):
```python
MODEL_NAME = "Meta-Llama-3.3-70B-Instruct"  # LLM模型
TEMPERATURE = 0.1  # 情绪提取温度
```

**检索配置** (`backend/search/config.py`):
```python
TEXT_MODEL_NAME = 'moka-ai/m3e-base'  # 文本编码器
IMAGE_MODEL_NAME = 'clip-ViT-B-32'    # 图像编码器
TOP_K = 2  # 返回Top-2
```

### 前端配置

**API地址** (`frontend/src/api/memeApi.js`):
```javascript
const BASE_URL = 'http://localhost:8000'
```

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献

1. **Fork** 本项目
2. 创建新分支 (`git checkout -b feature/AmazingFeature`)
3. 提交修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 **Pull Request**

### 贡献方向

- 🐛 报告Bug
- 💡 提出新功能
- 📝 完善文档
- 🎨 优化UI设计
- ⚡ 性能优化

---

## 🔒 安全与隐私

- ✅ API密钥使用环境变量存储
- ✅ 用户会话数据仅存在客户端
- ✅ 后端不持久化用户查询历史
- ✅ 生成的图片存储在本地

---

## 📄 许可证

本项目采用 [MIT License](LICENSE)。

---

## 🌟 Star History

如果这个项目对你有帮助，请给我们一个 ⭐️！

[![Star History Chart](https://api.star-history.com/svg?repos=your-org/memematch&type=Date)](https://star-history.com/#your-org/memematch&Date)

---

## 📞 联系我们

- **GitHub Issues**: [提交问题](https://github.com/your-org/memematch/issues)
- **讨论区**: [技术交流](https://github.com/your-org/memematch/discussions)
- **邮件**: contact@memematch.com

---

## 🙏 致谢

感谢以下项目和服务：

- [Meta AI](https://ai.meta.com/) - LLaMA 3.3 模型
- [SambaNova Cloud](https://cloud.sambanova.ai/) - 免费LLM推理
- [OpenAI](https://openai.com/) - CLIP 模型
- [Moka AI](https://github.com/wangyuxinwhy/uniem) - M3E 中文编码器
- [FastAPI](https://fastapi.tiangolo.com/) & [Vue.js](https://vuejs.org/) 社区

---

<div align="center">

**用心做好每一个梗图推荐** ❤️

Made with 💜 by MemeMatch Team

[⬆ 回到顶部](#memematch-)

</div>
