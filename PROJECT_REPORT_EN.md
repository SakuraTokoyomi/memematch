# MemeMatch - Intelligent Meme Recommendation System

## 📋 Project Overview

**MemeMatch** is an intelligent meme recommendation system based on Large Language Models (LLM) and vector retrieval technology. Users simply describe their emotions, and the system can understand, search for matching memes, and generate personalized memes when necessary.

### Core Features

- 🧠 **Intelligent Emotion Recognition**: Based on LLaMA 3.3 70B model for accurate emotion keyword extraction
- 🔍 **Multimodal Retrieval**: Combining CLIP image encoding and M3E Chinese text encoding for precise image-text matching
- 🎨 **Creative Generation**: Automatically generates personalized memes when retrieval results are unsatisfactory
- 💬 **Conversational Interaction**: Streaming response with real-time reasoning process display
- 🎯 **Top-N Recommendation**: Returns multiple candidate images for more choices
- ✨ **Secondary Creation**: Users can perform creative generation based on original queries for different style memes

---

## 🏗️ System Architecture

### Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Chat UI     │  │ Image Display│  │ Creative Gen │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Backend API (FastAPI)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/query/stream  - Streaming Query API           │   │
│  │  /api/generate      - Creative Generation API       │   │
│  │  /static           - Static Image Service            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Agent Core  │  │Search Engine │  │  Generator   │
│   (LLaMA)    │  │  (CLIP+M3E)  │  │   (PIL)      │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Architecture Layers

#### 1. **Frontend Layer**

- **Framework**: Vue 3 + Vite
- **UI Components**: Native HTML/CSS, no third-party UI libraries
- **Communication**: Axios + EventSource (SSE)
- **Features**:
  - Streaming response display
  - Real-time reasoning process visualization
  - Multi-image grid layout
  - Local session persistence

#### 2. **API Layer**

- **Framework**: FastAPI
- **Routes**:
  - `POST /api/query/stream`: Streaming query interface
  - `POST /api/generate`: Creative generation interface
  - `GET /static/*`: Static image service
  - `GET /health`: Health check
- **Features**:
  - Server-Sent Events (SSE) streaming response
  - CORS cross-origin support
  - Static file service

#### 3. **Agent Layer**

- **Model**: Meta-Llama-3.3-70B-Instruct (SambaNova Cloud)
- **Responsibilities**:
  - Emotion keyword extraction
  - Creative text generation
- **Temperature Settings**:
  - Emotion extraction: 0.1 (ensure stability)
  - Creative generation: 0.8 (increase creativity)

#### 4. **Retrieval Layer**

- **Text Encoder**: `moka-ai/m3e-base` (768-dim, Chinese optimized)
- **Image Encoder**: `clip-ViT-B-32` (512-dim, multimodal)
- **Retrieval Algorithm**: Cosine similarity + Top-K ranking
- **Dataset**: 4,600+ Chinese memes + emotion labels

#### 5. **Generation Layer**

- **Tool**: Pillow (PIL)
- **Templates**: Drake, Doge, Wojak (three classic meme templates)
- **Output**: PNG format, stored in `backend/generator/outputs/`

---

## 🔧 Technology Stack

### Backend Technologies

| Technology      | Version  | Purpose          | Selection Rationale                    |
| --------------- | -------- | ---------------- | -------------------------------------- |
| Python          | 3.10+    | Main Language    | Rich AI ecosystem and libraries        |
| FastAPI         | 0.104+   | Web Framework    | High performance, async, auto docs     |
| SambaNova Cloud | -        | LLM Inference    | Free quota, 70B model, strong Chinese  |
| CLIP            | ViT-B-32 | Image Encoding   | Multimodal pretrained, zero-shot       |
| M3E             | base     | Text Encoding    | Chinese optimized, excellent retrieval |
| Pillow          | 10.0+    | Image Processing | Python standard, easy to use           |
| NumPy           | 1.24+    | Computation      | Efficient vector operations            |

### Frontend Technologies

| Technology  | Version | Purpose       | Selection Rationale           |
| ----------- | ------- | ------------- | ----------------------------- |
| Vue 3       | 3.3+    | Framework     | Reactive, component-based     |
| Vite        | 4.4+    | Build Tool    | Fast HMR, modern              |
| Axios       | 1.5+    | HTTP Client   | Clean API, interceptor        |
| EventSource | -       | SSE Client    | Browser native, streaming     |

### Model Selection

#### 1. **LLM: Meta-Llama-3.3-70B-Instruct**

- **Advantages**:
  - 70B parameters, strong Chinese understanding
  - Version 3.3 significantly improved in multilingual tasks
  - SambaNova Cloud provides free inference service
  - Supports low temperature (0.1) for stable output
- **Use Cases**:
  - Emotion keyword extraction: Input "I'm so happy today" → Output "happy"
  - Creative text generation: Input "happy" → Output "Over the moon"

#### 2. **Text Encoder: M3E-base**

- **Advantages**:
  - SOTA on Chinese retrieval tasks
  - 768-dimensional vectors, information-rich
  - Trained on extensive Chinese corpora
- **Performance**: Surpasses OpenAI Embedding on Chinese retrieval tasks

#### 3. **Image Encoder: CLIP ViT-B-32**

- **Advantages**:
  - Pre-trained on 400M image-text pairs
  - Strong zero-shot generalization
  - Image-text semantic alignment
- **Use Cases**: Generate semantic vectors for memes, support cross-modal retrieval

---

## 🎯 Core Features

### 1. **Intelligent Meme Recommendation** (Main Flow)

#### Workflow

```
User Input
   ↓
LLM Extract Emotion Keywords (Step 1)
   ↓
Fused Query = Original Input + Emotion Keywords
   ↓
Vector Retrieval Top-2 (Step 2)
   ↓
Score ≥ 0.8?
   ├─ Yes → Return Retrieval Results
   └─ No → Call Generator (Step 3)
```

#### Technical Details

**Step 1: Emotion Extraction**

```python
# Agent prompt design
system_prompt = """You are an emotion recognition expert.
Rules:
1. Extract only emotion/state words (happy, tired, stressed, etc.)
2. Ignore action words (want, need, share, etc.)
3. Maximum 3 keywords, comma-separated
"""

# Call LLM
keywords = agent.extract_emotion_keywords("My work went very well today")
# Output: ["well", "happy"]
```

**Step 2: Hybrid Retrieval**

```python
# Query fusion strategy
if len(user_input) > len(keywords[0]) * 2:
    query = f"{user_input} {keywords[0]}"  # Preserve full semantics
else:
    query = keywords[0]  # Use keywords directly

# Vector retrieval
results = search_engine.search(
    query=query,
    top_k=2,  # Return top 2
    min_score=0.0
)

# Score judgment
if results[0]['score'] >= 0.8:
    return results  # Retrieval success
else:
    generate_meme()  # Fallback to generation
```

**Step 3: Meme Generation**

```python
# Random template selection
template = random.choice(['drake', 'doge', 'wojak'])

# Generate image
result = generator.generate(
    text=keywords[0],
    template=template
)
```

#### Streaming Response Example

SSE event stream received by frontend:

```json
// Event 1: Start
{"type": "start", "data": {"query": "I'm so happy today"}}

// Event 2: Emotion extraction success
{"type": "tool_call", "data": {
  "step": 1, 
  "tool": "extract_emotion",
  "result": {"keywords": ["happy"]},
  "status": "success"
}}

// Event 3: Search success
{"type": "tool_call", "data": {
  "step": 2,
  "tool": "search_meme",
  "result": {"score": 0.85, "found": true, "count": 2},
  "status": "success"
}}

// Event 4: Complete
{"type": "complete", "data": {
  "success": true,
  "meme_paths": ["/static/001.jpg", "/static/002.jpg"],
  "explanation": "Found a meme that perfectly expresses 'happy'!",
  "source": "search",
  "count": 2
}}
```

---

### 2. **Creative Generation** (Secondary Creation)

#### Use Case

When users are not satisfied with retrieval results, they click the **🎨 Creative Generate** button:

1. Based on original query and emotion keywords, LLM generates creative text
2. Randomly select template (drake/doge/wojak)
3. Generate personalized meme

#### Technical Implementation

**API Interface**

```python
@app.post("/api/generate")
async def generate_creative_meme(request: GenerateRequest):
    # 1. LLM generates creative text
    creative_text = agent._generate_creative_text(
        request.query,      # "I'm so happy today"
        request.keywords    # ["happy"]
    )
    # Output: "Over the moon"
  
    # 2. Random template
    template = random.choice(['doge', 'drake', 'wojak'])
  
    # 3. Generate image
    result = real_generate_meme(
        text=creative_text,
        template=template
    )
  
    return result
```

**Creative Text Generation Prompt**

```python
system_prompt = """You are a meme text creation expert.

Creative Requirements:
1. Concise: Maximum 8 words, preferably 4-6
2. Match emotion: Reflect '{keywords}' emotion
3. Humorous: Use internet slang, wordplay
4. Conversational: Like talking with friends

Example:
Input: "I'm so happy today" + "happy"
Output: "Over the moon"
"""
```

---

### 3. **Multi-Image Display** (Top-N Recommendation)

#### Frontend Implementation

**Grid Layout**

```vue
<!-- Single image: Centered display -->
<div class="meme-images-grid single-image">
  <img src="/static/001.jpg" />
</div>

<!-- Multiple images: Responsive grid -->
<div class="meme-images-grid multiple-images">
  <div class="meme-image-item">
    <img src="/static/001.jpg" />
    <div class="image-index">1</div>
  </div>
  <div class="meme-image-item">
    <img src="/static/002.jpg" />
    <div class="image-index">2</div>
  </div>
</div>
```

**CSS Styles**

```css
/* Single image */
.single-image {
  grid-template-columns: 1fr;
  max-width: 400px;
}

/* Multiple images */
.multiple-images {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  max-width: 600px;
}
```

---

## 📊 Data Flow

### Query Process Data Flow

```
User Input: "I'm so happy today"
    ↓
[Frontend]
    ↓ HTTP POST /api/query/stream
[API Server]
    ↓ extract_emotion_keywords()
[Agent] → LLaMA 3.3 70B
    ↓ return ["happy"]
[API Server]
    ↓ Fused query: "I'm so happy today happy"
    ↓ search(query, top_k=2)
[Search Engine]
    ↓ encode_text() → [0.12, -0.45, ..., 0.78] (768-dim)
    ↓ cosine_similarity() → scores
    ↓ return Top-2 results
[API Server]
    ↓ if score >= 0.8:
    ↓   convert_paths()
    ↓   SSE stream
[Frontend]
    ↓ Render image grid
[User] Sees 2 memes
```

---

## 🗂️ Project Structure

```
memematch/
├── backend/                    # Backend Service
│   ├── agent/                 # Agent Module
│   │   ├── agent_core.py     # LLM Core Logic
│   │   ├── real_tools.py     # Tool Functions
│   │   ├── config.py         # Agent Config
│   │   └── session_manager.py # Session Manager
│   ├── search/                # Retrieval Module
│   │   ├── engine.py         # Search Engine
│   │   └── config.py         # Search Config
│   ├── generator/             # Generation Module
│   │   ├── generator.py      # Image Generator
│   │   ├── templates/        # Meme Templates
│   │   │   ├── drake.png
│   │   │   ├── doge.png
│   │   │   └── wojak.png
│   │   └── outputs/          # Generated Output
│   ├── api/                   # API Service
│   │   └── api_server.py     # FastAPI Main
│   └── improve/               # Optimization Module
│       └── config.py         # Optimization Config
├── frontend/                  # Frontend Application
│   ├── src/
│   │   ├── App.vue           # Main Component
│   │   ├── api/
│   │   │   └── memeApi.js    # API Wrapper
│   │   └── main.js           # Entry Point
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── data/                      # Data Directory
│   └── dataset/
│       ├── meme/             # Meme Images (4600+)
│       ├── memeWithEmo.csv   # Images + Emotion Labels
│       └── index/            # Vector Index
│           ├── image_index.npy
│           └── text_index.npy
├── scripts/                   # Utility Scripts
│   ├── start.sh              # Start Script
│   └── stop.sh               # Stop Script
├── logs/                      # Log Directory
│   ├── backend.log
│   └── frontend.log
├── requirements.txt           # Python Dependencies
└── README.md                  # Project README
```

---

## 🚀 Deployment & Running

### Environment Requirements

- **Python**: 3.10+
- **Node.js**: 16+
- **System**: macOS / Linux / Windows
- **Memory**: 8GB+ recommended
- **Disk**: 5GB+ (including models and dataset)

### Quick Start

```bash
# 1. Clone project
git clone <repository-url>
cd memematch

# 2. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. Configure environment variables
export SAMBANOVA_API_KEY="your-api-key"

# 4. Start services
./scripts/start.sh

# 5. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Service Ports

| Service      | Port        | Purpose      |
| ------------ | ----------- | ------------ |
| Frontend     | 3000        | Vue App      |
| Backend API  | 8000        | FastAPI      |
| Static Files | 8000/static | Image Server |

---

## 📈 Performance Metrics

### Response Time

| Operation        | Average Time   | Note                   |
| ---------------- | -------------- | ---------------------- |
| Emotion Extract  | 0.5-1s         | LLM Inference          |
| Vector Retrieval | 0.1-0.3s       | 4600 images            |
| Meme Generation  | 0.2-0.5s       | PIL Image Processing   |
| Creative Gen     | 1-2s           | LLM Inference + Gen    |
| **Overall**      | **1-2s**       | End-to-end Latency     |

### Retrieval Accuracy

- **Top-1 Accuracy**: ~78%
- **Top-2 Accuracy**: ~85%
- **Threshold Strategy**: score ≥ 0.8 considered successful match

### Dataset Scale

- **Image Count**: 4,650
- **Emotion Labels**: 30+ types (happy, sad, helpless, surprised, etc.)
- **Vector Dimensions**: 768-dim (text) + 512-dim (image)

---

## 🔐 Security & Privacy

### API Key Management

- Use environment variables to store `SAMBANOVA_API_KEY`
- Do not hardcode sensitive information in code

### User Data

- Session data stored only in client-side localStorage
- Backend does not persist user query history
- Generated images stored on local server

### CORS Configuration

```python
# Recommend specific domains in production
allow_origins=["http://localhost:3000"]
```

---

## 🎨 UI/UX Design

### Design Philosophy

- **Simple**: No redundant elements, focus on conversation
- **Smooth**: Streaming response, real-time feedback
- **Friendly**: Reasoning process visualization, transparent and trustworthy

### Visual Style

- **Color Scheme**: Gradient purple-blue, modern tech feel
- **Layout**: Conversational, card-based
- **Animation**: Smooth transitions, micro-interactions

### Responsive Design

- Supports desktop and mobile
- Image grid adaptive layout

---

## 🔮 Future Roadmap

### Short-term Optimization (1-2 months)

- [ ] Add more meme templates (5+ types)
- [ ] Support user-uploaded custom images
- [ ] Optimize retrieval algorithm (introduce re-ranking)
- [ ] Add user feedback mechanism (like/favorite)

### Mid-term Goals (3-6 months)

- [ ] Multimodal retrieval (support image input)
- [ ] Personalized recommendation (based on history)
- [ ] Community features (share memes)
- [ ] Mobile app

### Long-term Vision (6-12 months)

- [ ] Automatic meme generation (Stable Diffusion)
- [ ] Multi-language support (English, Japanese, etc.)
- [ ] Real-time trending meme updates
- [ ] B2B services (API sales)

---

## 🤝 Team Collaboration

### Project Roles

| Role    | Responsibility    | Module        |
| ------- | ----------------- | ------------- |
| Member A | Retrieval Engineer | Search Engine |
| Member B | Agent Engineer     | Agent Core    |
| Member C | Generation Engineer | Generator     |
| Member D | Frontend Engineer  | Frontend UI   |

### Development Process

1. **Requirement Analysis** → Define functional goals
2. **Module Design** → Define interface specifications
3. **Parallel Development** → Independent module development
4. **Integration Testing** → API integration testing
5. **Production Deployment** → Production environment release

---

## 📚 References

### Papers & Technical Blogs

- [CLIP: Connecting Text and Images](https://arxiv.org/abs/2103.00020)
- [M3E: Massive Multi-task Chinese Text Embedding](https://github.com/wangyuxinwhy/uniem)
- [LLaMA 3: Meta's Open Foundation Models](https://ai.meta.com/blog/llama-3/)

### Open Source Projects

- [OpenAI CLIP](https://github.com/openai/CLIP)
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers)
- [FastAPI](https://github.com/tiangolo/fastapi)

---

**Last Updated**: 2025-11-22  
**Version**: v2.0.0  
**Status**: ✅ Production Ready

