# MemeMatch - 智能梗图推荐系统

> 基于情绪识别的智能梗图检索与生成系统

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[快速开始](#快速开始) • [功能特性](#功能特性) • [系统架构](#系统架构) • [文档](#文档)

</div>

---

## 🎯 项目简介

MemeMatch 是一个智能梗图推荐系统，能够：
- 🧠 **智能理解**：基于 LLM 识别用户情绪和意图
- 🔍 **精准检索**：使用向量检索快速匹配相关梗图
- 🎨 **动态生成**：当数据库没有合适的图片时，自动生成新梗图
- 💬 **对话交互**：流式对话，实时展示推理过程

## ⚡ 快速开始

### 一键启动（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/SakuraTokoyomi/memematch.git
cd memematch

# 2. 配置环境变量（可选）
export SAMBANOVA_API_KEY="your_api_key"

# 3. 一键启动
./scripts/start.sh
```

**访问地址**：
- 🌐 前端界面：http://localhost:3000
- 📡 后端 API：http://localhost:8000
- 📚 API 文档：http://localhost:8000/docs

### 停止服务

```bash
./scripts/stop.sh
```

## 🌟 功能特性

### 1. 智能情绪识别
- 基于 Meta-Llama-3.3-70B-Instruct
- 准确提取用户情绪关键词（最多3个）
- 支持复杂语义理解

**示例**：
```
输入："项目延期了，压力好大"
识别：["压力", "焦虑"]
```

### 2. 混合检索引擎
- **向量检索**：融合原始查询 + 情绪关键词
- **双通道检索**：图像特征 + 文本语义
- **智能融合**：加权融合多模态结果

**技术栈**：
- Sentence-BERT（中文语义编码）
- Faiss（高效向量检索）
- CLIP（图像-文本对齐）

### 3. 自适应生成
- 检索失败时自动触发生成
- 支持多种梗图模板（Wojak, Drake, Doge等）
- 中文文本渲染

**触发条件**：
```python
if search_score <= 0.8:  # 相似度阈值
    generate_meme(emotion_keywords)
```

### 4. 实时对话流
- Server-Sent Events (SSE) 流式响应
- 前端实时展示推理步骤
- 友好的用户交互

## 🏗️ 系统架构

### 架构图

```
┌─────────────┐
│   用户输入   │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│  LLM 情绪提取             │  ← Meta-Llama-3.3-70B
│  "压力大" → ["压力"]      │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│  查询融合                 │
│  原始查询 + 情绪关键词    │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│  混合检索                 │
│  - 图像向量检索           │
│  - 文本语义检索           │
│  - 加权融合               │
└──────┬───────────────────┘
       │
       ▼
    score > 0.8?
       │
   YES │          NO
       │           │
       ▼           ▼
┌───────────┐  ┌─────────────┐
│ 返回检索  │  │  生成新梗图  │
│  结果     │  │  (Wojak等)  │
└───────────┘  └─────────────┘
```

### 目录结构

```
memematch/
├── backend/                 # 后端服务
│   ├── api/                 # FastAPI 服务
│   │   └── api_server.py    # 主API入口
│   ├── search/              # 搜索引擎（成员A）
│   │   ├── engine.py        # 检索核心
│   │   └── indexer.py       # 索引构建
│   ├── generator/           # 生成器（成员C）
│   │   ├── generate_meme.py # 生成核心
│   │   ├── templates/       # 梗图模板
│   │   └── fonts/           # 字体文件
│   ├── agent/               # LLM Agent（成员B）
│   │   ├── agent_core.py    # Agent核心
│   │   └── real_tools.py    # 工具集成
│   ├── config/              # 配置文件
│   ├── tests/               # 单元测试
│   └── requirements.txt     # Python依赖
│
├── frontend/                # 前端服务（成员D）
│   ├── src/
│   │   ├── App.vue          # 主组件
│   │   ├── api/             # API调用
│   │   └── main.js          # 入口
│   ├── package.json         # Node依赖
│   └── vite.config.js       # Vite配置
│
├── data/                    # 数据和资源
│   ├── dataset/             # 原始数据集
│   │   ├── memeWithEmo.csv  # 梗图元数据
│   │   └── meme/            # 梗图图片
│   ├── models/              # 模型缓存
│   │   └── search_index/    # Faiss索引
│   └── outputs/             # 生成输出
│       └── generated/       # 生成的梗图
│
├── scripts/                 # 工具脚本
│   ├── start.sh             # 启动脚本
│   └── stop.sh              # 停止脚本
│
├── docs/                    # 项目文档
│   ├── PROJECT_REPORT.md    # 项目报告
│   ├── RUNNING_GUIDE.md     # 运行指南
│   └── ARCHITECTURE_V2.md   # 架构文档
│
├── tests/                   # 集成测试
│
├── logs/                    # 日志文件
│
└── README.md                # 本文件
```

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 平均响应时间 | < 2s |
| 检索准确率 (Top-5) | 85%+ |
| 情绪识别准确率 | 90%+ |
| 系统可用性 | 99%+ |

## 🔧 系统要求

### 必需
- **Python**: 3.11+ （推荐）
- **Node.js**: 18+
- **npm**: 9+
- **磁盘空间**: 5GB+

### 可选
- **GPU**: 用于加速向量检索（可选）
- **SambaNova API Key**: LLM 调用（可使用内置默认值）

## 📖 文档

- 📘 [项目报告](docs/PROJECT_REPORT.md) - 技术细节和挑战
- 📗 [运行指南](docs/RUNNING_GUIDE.md) - 详细部署说明
- 📙 [架构文档](docs/ARCHITECTURE_V2.md) - 系统设计思路

## 🧪 测试

```bash
# 后端测试
cd backend
source venv/bin/activate
pytest tests/

# 情绪识别测试
python tests/test_emotion_extraction.py
```

## 🛠️ 常见问题

### Q1: 端口被占用？
```bash
# 查看占用端口的进程
lsof -i :8000  # 后端
lsof -i :3000  # 前端

# 杀死进程
kill -9 <PID>
```

### Q2: Python 版本不兼容？
使用 Python 3.11：
```bash
brew install python@3.11
python3.11 -m venv venv
```

### Q3: 依赖安装失败？
使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 🤝 团队分工

| 成员 | 职责 | 技术栈 |
|------|------|--------|
| 成员A | 搜索引擎 | Faiss, Sentence-BERT |
| 成员B | LLM Agent | FastAPI, OpenAI API |
| 成员C | 图片生成 | Pillow, Template Engine |
| 成员D | 前端界面 | Vue.js, Vite |

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🎯 未来规划

- [ ] 支持多轮对话上下文
- [ ] 增加更多梗图模板
- [ ] 模型本地化部署
- [ ] 移动端适配
- [ ] 用户个性化推荐

---

<div align="center">

**MemeMatch** - 让情绪表达更有趣 🎭

Made with ❤️ by MemeMatch Team

</div>

