# MemeMatch 🎭

<div align="center">

**Intelligent Meme Recommendation System - Find the Perfect Meme for Your Mood**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.3+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Quick Start](#-quick-start) • [Features](#-features) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Introduction

**MemeMatch** is an intelligent meme recommendation system powered by Large Language Models (LLM) and multimodal vector retrieval. Simply describe your mood, and the system will:

- 🧠 **Understand Emotions**: Intelligently identify your emotional state
- 🔍 **Precise Matching**: Find the perfect meme from 4,600+ images
- 🎨 **Creative Generation**: Automatically generate personalized memes when needed
- 💬 **Conversational UI**: Streaming response with real-time reasoning display

### Live Demo

> 🎥 **Demo Video**: [Watch Demo](docs/demo.mp4)  
> 🌐 **Try Online**: [Live Demo](http://memematch.demo.com)

---

## ✨ Features

### 1️⃣ Intelligent Emotion Recognition

Based on **Meta-Llama-3.3-70B** model for accurate emotion keyword extraction

```
Input: "My work went very well today, and my boss praised me!"
Recognition: ["well", "happy"]
```

### 2️⃣ Multimodal Retrieval

Combines **CLIP** image encoding and **M3E** Chinese text encoding for semantic matching

- Retrieval Speed: < 0.3s (4,600 images)
- Top-2 Accuracy: ~85%

### 3️⃣ Top-N Recommendation

Returns multiple candidate images for more choices

<div align="center">
<img src="docs/screenshots/top2.png" width="600" alt="Top-2 Recommendation" />
</div>

### 4️⃣ Creative Generation

Click **🎨 Creative Generate** button, the system will:
- LLM generates creative text (e.g., "Over the moon")
- Randomly select meme template (Drake/Doge/Wojak)
- Generate personalized meme

<div align="center">
<img src="docs/screenshots/creative.png" width="600" alt="Creative Generation" />
</div>

### 5️⃣ Streaming Response

Real-time reasoning process display, transparent and trustworthy

```
💭 Thinking Process
1. 💡 Emotion Recognition: happy
2. 🔍 Meme Retrieval: Found matching "happy" image (similarity 85%)
```

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────┐
│   Vue 3     │  Frontend (Chat UI)
└──────┬──────┘
       │ HTTP/SSE
┌──────▼──────┐
│   FastAPI   │  Backend (API Service)
└──────┬──────┘
       │
   ┌───┴───┬───────┬────────┐
   ▼       ▼       ▼        ▼
┌─────┐ ┌────┐ ┌──────┐ ┌────┐
│Agent│ │Search│ │Generator│ │Session│
│LLaMA│ │CLIP│ │ PIL  │ │Mgr │
└─────┘ └────┘ └──────┘ └────┘
```

### Technology Stack

**Backend**:
- **Web Framework**: FastAPI
- **LLM**: Meta-Llama-3.3-70B (SambaNova Cloud)
- **Text Encoding**: M3E-base (Chinese optimized)
- **Image Encoding**: CLIP ViT-B-32
- **Image Processing**: Pillow

**Frontend**:
- **Framework**: Vue 3
- **Build Tool**: Vite
- **HTTP Client**: Axios + EventSource

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+
- 8GB+ RAM

### One-Click Launch

```bash
# 1. Clone project
git clone https://github.com/your-org/memematch.git
cd memematch

# 2. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. Configure API key
export SAMBANOVA_API_KEY="your-api-key"

# 4. Start services
./scripts/start.sh

# 5. Open browser
# Visit http://localhost:3000
```

**Detailed Steps**: See [Quick Start Guide](QUICKSTART.md)

---

## 📊 Performance Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| End-to-end Latency | 1-2s | From input to result |
| Emotion Extraction | 0.5-1s | LLM inference time |
| Vector Retrieval | 0.1-0.3s | 4,600 images retrieval |
| Image Generation | 0.2-0.5s | PIL image processing |
| Top-2 Accuracy | ~85% | User satisfaction |

---

## 📁 Directory Structure

```
memematch/
├── backend/              # Backend Service
│   ├── agent/           # LLM Agent
│   ├── search/          # Search Engine
│   ├── generator/       # Image Generator
│   └── api/             # FastAPI Service
├── frontend/            # Vue Frontend
│   └── src/
│       ├── App.vue      # Main Component
│       └── api/         # API Wrapper
├── data/                # Dataset
│   └── dataset/
│       ├── meme/        # 4,600+ Memes
│       └── index/       # Vector Index
├── scripts/             # Start Scripts
│   ├── start.sh
│   └── stop.sh
├── docs/                # Documentation
│   ├── screenshots/     # Screenshots
│   └── demo.mp4         # Demo Video
└── requirements.txt     # Python Dependencies
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Quick Start Guide |
| [PROJECT_REPORT_EN.md](PROJECT_REPORT_EN.md) | Detailed Technical Report |
| [API Documentation](http://localhost:8000/docs) | Auto-generated by FastAPI |

---

## 🎯 Usage Examples

### Basic Query

```bash
# Terminal test
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"text": "I am so happy today"}'
```

**Response**:
```json
{
  "success": true,
  "meme_paths": ["/static/001.jpg", "/static/002.jpg"],
  "explanation": "Found a meme that perfectly expresses 'happy'!",
  "source": "search",
  "count": 2
}
```

### Creative Generation

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "I am so happy today", "keywords": ["happy"]}'
```

**Response**:
```json
{
  "success": true,
  "meme_path": "/generated/creative_20251122_123456.png",
  "explanation": "Created a doge-style meme based on 'happy', text: Over the moon",
  "source": "generated"
}
```

---

## 🛠️ Configuration

### Backend Configuration

**Agent Config** (`backend/agent/config.py`):
```python
MODEL_NAME = "Meta-Llama-3.3-70B-Instruct"  # LLM model
TEMPERATURE = 0.1  # Emotion extraction temperature
```

**Search Config** (`backend/search/config.py`):
```python
TEXT_MODEL_NAME = 'moka-ai/m3e-base'  # Text encoder
IMAGE_MODEL_NAME = 'clip-ViT-B-32'    # Image encoder
TOP_K = 2  # Return Top-2
```

### Frontend Configuration

**API Address** (`frontend/src/api/memeApi.js`):
```javascript
const BASE_URL = 'http://localhost:8000'
```

---

## 🤝 Contributing

We welcome all forms of contributions!

### How to Contribute

1. **Fork** this project
2. Create new branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Submit **Pull Request**

### Contribution Directions

- 🐛 Report bugs
- 💡 Propose new features
- 📝 Improve documentation
- 🎨 Optimize UI design
- ⚡ Performance optimization

---

## 🔒 Security & Privacy

- ✅ API keys stored in environment variables
- ✅ User session data only on client side
- ✅ Backend does not persist user query history
- ✅ Generated images stored locally

---

## 📄 License

This project is licensed under [MIT License](LICENSE).

---

## 🌟 Star History

If this project helps you, please give us a ⭐️!

[![Star History Chart](https://api.star-history.com/svg?repos=your-org/memematch&type=Date)](https://star-history.com/#your-org/memematch&Date)

---

## 📞 Contact Us

- **GitHub Issues**: [Submit Issue](https://github.com/your-org/memematch/issues)
- **Discussions**: [Technical Exchange](https://github.com/your-org/memematch/discussions)
- **Email**: contact@memematch.com

---

## 🙏 Acknowledgments

Thanks to the following projects and services:

- [Meta AI](https://ai.meta.com/) - LLaMA 3.3 Model
- [SambaNova Cloud](https://cloud.sambanova.ai/) - Free LLM Inference
- [OpenAI](https://openai.com/) - CLIP Model
- [Moka AI](https://github.com/wangyuxinwhy/uniem) - M3E Chinese Encoder
- [FastAPI](https://fastapi.tiangolo.com/) & [Vue.js](https://vuejs.org/) Community

---

<div align="center">

**Crafted with care for every meme recommendation** ❤️

Made with 💜 by MemeMatch Team

[⬆ Back to Top](#memematch-)

</div>

