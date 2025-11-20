# 📂 MemeMatch 最终目录结构

## ✅ 当前配置（已确认）

### 核心目录

memematch/
├── backend/                          # 后端服务（重构后）
│   ├── __init__.py
│   ├── requirements.txt              # 统一依赖
│   ├── api/                          # FastAPI服务
│   │   ├── __init__.py
│   │   └── api_server.py
│   ├── search/                       # 搜索引擎（成员A）
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── config.py                 # ✅ 使用 data/dataset/
│   ├── generator/                    # 图片生成（成员C）
│   │   ├── __init__.py
│   │   ├── generate_meme.py
│   │   ├── templates/
│   │   ├── fonts/
│   │   └── outputs/                  # 生成的图片
│   └── agent/                        # LLM Agent（成员B）
│       ├── __init__.py
│       ├── agent_core.py
│       ├── config.py
│       ├── real_tools.py
│       └── session_manager.py
│
├── frontend/                         # 前端服务（成员D）
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── api/
│   ├── package.json
│   ├── vite.config.js
│   └── node_modules/
│
├── data/                             # 数据和资源（统一）
│   ├── dataset/                      # ✅ 数据集
│   │   ├── memeWithEmo.csv          # 元数据（2.6MB）
│   │   └── meme/                    # 梗图图片（4002张）
│   └── models/                       # 模型和索引
│       └── search_index/            # ✅ Faiss索引
│           ├── image.index          # 图像索引
│           ├── text.index           # 文本索引
│           └── metadata.json        # 元数据
├── scripts/                          # 启动脚本
│   ├── start.sh                     # 一键启动
│   └── stop.sh                      # 一键停止
│
├── docs/                            # 文档
│   ├── PROJECT_REPORT.md
│   ├── RUNNING_GUIDE.md
│   └── ARCHITECTURE_V2.md
│
├── logs/                            # 日志文件
│   ├── backend.log
│   └── frontend.log
│
└── README.md

### 旧目录（已迁移，可删除）

```
❌ member_a_search/         # 已移到 backend/search/
❌ member_b_agent/          # 已移到 backend/agent/
❌ member_c_generate/       # 已移到 backend/generator/
❌ member_d_frontend/       # 已移到 frontend/
❌ dataset/                 # 冗余（data/dataset/ 已有）
```

## 🔧 路径配置

### 搜索引擎 (backend/search/config.py)

```python
DATA_DIR = PROJECT_ROOT/data/dataset/          # ✅ 数据目录
OUTPUT_DIR = PROJECT_ROOT/data/models/search_index/  # ✅ 索引目录
```

### 图片生成器 (backend/generator/)

```python
OUTPUT_DIR = backend/generator/outputs/        # ✅ 生成图片
```

### API服务 (backend/api/api_server.py)

```python
MEME_IMAGE_DIR = PROJECT_ROOT/data/dataset/meme/        # ✅ 静态图片
GENERATED_IMAGE_DIR = backend/generator/outputs/        # ✅ 生成图片
```

## 📊 磁盘使用

| 目录                           | 大小              | 说明                    |
| ------------------------------ | ----------------- | ----------------------- |
| `data/dataset/`              | ~700 MB           | 数据集（4002张图片）    |
| `data/models/`               | ~80 MB            | Faiss索引               |
| `backend/`                   | ~50 MB            | 后端代码 + venv         |
| `frontend/`                  | ~150 MB           | 前端代码 + node_modules |
| `backend/generator/outputs/` | ~1-10 MB          | 生成的图片              |
| `logs/`                      | ~1 MB             | 日志文件                |
| **总计（必需）**         | **~980 MB** |                         |

| 可删除                   | 节省空间          |
| ------------------------ | ----------------- |
| `dataset/`             | ~700 MB           |
| `member_*`             | ~210 MB           |
| **总计（可删除）** | **~910 MB** |

## 🧹 清理建议

### 方案：删除冗余目录

```bash
# 确认系统运行正常后执行
rm -rf dataset/                # 冗余数据（已在data/dataset/）
rm -rf member_a_search/        # 旧代码（已移到backend/search/）
rm -rf member_b_agent/         # 旧代码（已移到backend/agent/）
rm -rf member_c_generate/      # 旧代码（已移到backend/generator/）
rm -rf member_d_frontend/      # 旧代码（已移到frontend/）
```

**节省空间**: ~910 MB

## ✅ 验证清单

清理前请确认：

- [ ] 系统启动成功 (`./scripts/start.sh`)
- [ ] 前端可访问 (http://localhost:3000)
- [ ] 搜索功能正常（能看到梗图）
- [ ] 图片生成正常
- [ ] 路径显示 `data/dataset/`

## 📋 测试结果（2025-11-20）

### ✅ 搜索功能

- 数据目录: `/data/dataset/` ✓
- 索引目录: `/data/models/search_index/` ✓
- 图片数量: 4002 张 ✓
- 搜索耗时: 15秒（首次）/ 0.3秒（后续）✓

### ✅ 图片生成

- Wojak: 76.4 KB ✓
- Drake: 224.1 KB ✓
- Doge: 295.8 KB ✓
- 输出目录: `backend/generator/outputs/` ✓

## 🎯 最终结论

**推荐配置**：

- ✅ 使用 `data/` 目录（统一数据管理）
- ✅ 使用 `backend/` 目录（统一代码结构）
- ✅ 删除 `dataset/` 和 `member_*`（节省空间）

**优势**：

1. 目录结构清晰
2. 前后端分离明确
3. 数据统一管理
4. 节省约 910MB 空间

---

**更新时间**: 2025-11-20
**配置状态**: ✅ 已切换到 data/ 目录
