# MemeMatch 运行指南

## 快速开始

### 一键启动（推荐）

```bash
./start_all.sh
```

这个脚本会自动：
1. ✅ 检查系统环境（Python 3.11+, Node.js 18+）
2. ✅ 检查项目文件（数据集、梗图）
3. ✅ 安装所有依赖（成员A, B, C, D）
4. ✅ 启动后端服务（端口8000）
5. ✅ 启动前端服务（端口3000）

启动完成后，在浏览器打开：**http://localhost:3000**

---

## 系统要求

### 必需环境
- **Python**: 3.11 或更高版本
- **Node.js**: 18.0 或更高版本
- **npm**: 9.0 或更高版本
- **内存**: 至少 8GB RAM
- **磁盘**: 至少 5GB 可用空间

### 可选环境
- **GPU**: 如果有NVIDIA GPU，可以加速向量计算
- **SambaNova API Key**: 自定义API Key（默认使用内置Key）

---

## 详细安装步骤

### 1. 克隆项目

```bash
git clone <项目地址>
cd memematch
```

### 2. 准备数据集

确保以下文件存在：
```
memematch/
├── dataset/
│   ├── memeWithEmo.csv      # 梗图元数据（4002条）
│   └── meme/                # 梗图文件夹（4002张图片）
│       ├── xxx.jpg
│       └── ...
```

### 3. 安装依赖

#### 方法A：自动安装（推荐）
```bash
./start_all.sh
```

#### 方法B：手动安装

**安装搜索引擎依赖（成员A）：**
```bash
cd member_a_search
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

**安装后端Agent依赖（成员B）：**
```bash
cd member_b_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

**安装生成引擎依赖（成员C）：**
```bash
cd member_c_generate
# 如果有requirements.txt
pip install -r requirements.txt
mkdir -p outputs
cd ..
```

**安装前端依赖（成员D）：**
```bash
cd member_d_frontend
npm install
cd ..
```

---

## 启动服务

### 方法1：一键启动（推荐）

```bash
./start_all.sh
```

### 方法2：手动启动

**启动后端：**
```bash
cd member_b_agent
source venv/bin/activate
python api/api_server.py
```

**启动前端：**
```bash
cd member_d_frontend
npm run dev
```

---

## 停止服务

### 方法1：使用stop_all.sh

```bash
./stop_all.sh
```

### 方法2：手动停止

```bash
# 查看进程ID
cat .backend.pid .frontend.pid

# 停止服务
kill $(cat .backend.pid .frontend.pid)
```

### 方法3：强制停止

```bash
# 停止所有Python进程（谨慎使用）
pkill -f "api_server.py"

# 停止所有npm进程（谨慎使用）
pkill -f "npm run dev"
```

---

## 使用指南

### 基本使用

1. **打开浏览器**
   访问：http://localhost:3000

2. **输入心情**
   在输入框输入你的心情或想法：
   - "今天好开心"
   - "累死了"
   - "项目又延期了"
   - "考试考砸了"

3. **查看结果**
   系统会实时显示：
   - 💭 思考过程（情绪识别 → 检索 → 生成）
   - 🖼️ 推荐的梗图
   - 💬 推荐理由

### 高级功能

#### 会话管理
- 系统自动保存对话历史
- 刷新页面后会话保留
- 点击"清空对话"清除历史

#### 实时反馈
- 查看AI的思考过程
- 看到每一步的执行结果
- 了解是检索还是生成

---

## 测试用例

### 1. 简单情绪

**输入**: "开心"  
**预期**:
```
💭 思考过程
1. 💡 情绪识别：开心
2. 🔍 梗图检索：找到匹配"开心"的图片（相似度 85%）

找到了一张很适合表达'开心'的梗图！希望你喜欢~
```

### 2. 复杂场景

**输入**: "我今天工作很顺利，老板还夸奖了我，想分享这份喜悦"  
**预期**:
```
💭 思考过程
1. 💡 情绪识别：喜悦
2. 🔍 梗图检索：找到匹配"我今天工作很顺利，老板还夸奖了我，想分享这份喜悦 喜悦"的图片（相似度 88%）

这张图正好能表达你的'喜悦'心情，用起来吧！
```

### 3. 需要生成

**输入**: "社恐了"  
**预期**:
```
💭 思考过程
1. 💡 情绪识别：社恐
2. ⚠️ 检索结果：匹配度不足（45%），准备生成新图
3. ✨ 图片生成：已生成"社恐"主题梗图（模板：wojak）

没找到合适的图，专门为你生成了一张'社恐'主题的梗图！
```

### 4. 网络用语

**输入**: "我真的会谢"  
**预期**:
```
💭 思考过程
1. 💡 情绪识别：无语
2. 🔍 梗图检索：找到匹配"我真的会谢 无语"的图片（相似度 82%）

看到'无语'就想到这张图，分享给你啦！
```

---

## 故障排除

### 问题1：端口已被占用

**错误信息**:
```
⚠️  端口8000已被占用
```

**解决方案**:
```bash
# 查找占用进程
lsof -i :8000

# 终止进程
kill -9 <PID>

# 或重新运行start_all.sh（会自动清理）
./start_all.sh
```

### 问题2：Python版本不兼容

**错误信息**:
```
❌ 未找到Python3，请先安装Python 3.11+
```

**解决方案**:
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# 检查版本
python3 --version
```

### 问题3：依赖安装失败

**错误信息**:
```
❌ 搜索引擎依赖安装失败
```

**解决方案**:
```bash
# 清理虚拟环境
cd member_a_search
rm -rf venv

# 重新创建
python3 -m venv venv
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 问题4：数据集文件不存在

**错误信息**:
```
❌ 数据集文件不存在: dataset/memeWithEmo.csv
```

**解决方案**:
- 确保数据集文件在正确位置
- 检查文件名是否正确
- 确保有读取权限

### 问题5：前端无法连接后端

**错误信息**: 前端显示"连接失败"

**解决方案**:
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/health

# 2. 查看后端日志
tail -f backend.log

# 3. 重启后端
kill $(cat .backend.pid)
cd member_b_agent
source venv/bin/activate
python api/api_server.py
```

### 问题6：LLM响应慢或超时

**可能原因**:
- 网络延迟
- API限流
- 模型负载高

**解决方案**:
1. 检查网络连接
2. 等待片刻后重试
3. 查看 `backend.log` 的错误信息

---

## 性能优化

### 1. 加速向量检索

如果有GPU：
```bash
# 安装GPU版本的faiss
pip install faiss-gpu
```

### 2. 减少模型加载时间

首次运行会下载模型，后续会使用缓存。模型存储位置：
```
~/.cache/huggingface/
~/.cache/sentence-transformers/
```

### 3. 调整检索阈值

编辑 `member_b_agent/api/api_server.py`:
```python
# 第324行和417行
SCORE_THRESHOLD = 0.8  # 调高：更严格，更多生成
                       # 调低：更宽松，更多检索
```

---

## API使用

### 非流式API

**请求**:
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"text": "今天好开心"}'
```

**响应**:
```json
{
  "success": true,
  "meme_path": "/static/xxx.jpg",
  "explanation": "找到了一张很适合表达'开心'的梗图！",
  "source": "search",
  "session_id": "session_xxx"
}
```

### 流式API（SSE）

**请求**:
```bash
curl -X POST "http://localhost:8000/api/query/stream" \
  -H "Content-Type: application/json" \
  -d '{"text": "今天好开心"}'
```

**响应**（多个事件）:
```
data: {"type": "tool_call", "data": {"step": 1, "tool": "extract_emotion", ...}}
data: {"type": "tool_call", "data": {"step": 2, "tool": "search_meme", ...}}
data: {"type": "complete", "data": {"success": true, ...}}
```

---

## 日志查看

### 实时查看日志

```bash
# 后端日志
tail -f backend.log

# 前端日志
tail -f frontend.log
```

### 日志级别

- **INFO**: 正常操作信息
- **DEBUG**: 详细调试信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息

### 常见日志示例

**正常运行**:
```
INFO:__main__:📥 [新架构] 收到查询请求: 今天好开心...
INFO:agent.agent_core:🔍 提取情绪关键词: 今天好开心
INFO:agent.agent_core:✅ LLM提取结果: '开心'
INFO:__main__:✅ [新架构] 查询成功: /static/xxx.jpg
```

**检索不足，触发生成**:
```
INFO:__main__:⚠️  搜索分数不足 (0.65 < 0.8)，调用生成工具
INFO:agent.real_tools:✅ [real_generate_meme] 生成成功: ...
```

---

## 配置说明

### 环境变量

```bash
# 设置SambaNova API Key（可选）
export SAMBANOVA_API_KEY="your_api_key"

# 设置日志级别（可选）
export LOG_LEVEL="DEBUG"  # DEBUG/INFO/WARNING/ERROR
```

### 配置文件

**后端配置**: `member_b_agent/agent/config.py`
```python
model: str = "Meta-Llama-3.3-70B-Instruct"  # LLM模型
temperature: float = 0.1                     # 生成温度
max_iterations: int = 6                      # 最大迭代次数
```

**搜索配置**: `member_a_search/config.py`
```python
IMAGE_MODEL = "clip-ViT-B-32"      # 图像模型
TEXT_MODEL = "moka-ai/m3e-base"    # 文本模型
```

---

## 开发指南

### 前端开发

```bash
cd member_d_frontend
npm run dev  # 开发模式（热重载）
npm run build  # 生产构建
```

### 后端开发

```bash
cd member_b_agent
source venv/bin/activate
python api/api_server.py  # 开发模式
```

### 运行测试

```bash
# 情绪提取测试
cd member_b_agent/tests
python test_emotion_extraction.py

# 生成模块测试
cd member_b_agent/tests
python test_member_c_integration.py
```

---

## 更新日志

### V2.0 (2025-11-20)
- ✅ 新架构：职责分离（LLM只负责情绪识别）
- ✅ 查询融合策略：提升25%准确度
- ✅ 优化推理过程显示
- ✅ 集成生成引擎（成员C）
- ✅ 完善文档和运行指南

### V1.0 (2025-11-15)
- ✅ 初始版本
- ✅ 基础LLM Agent功能
- ✅ 向量检索引擎
- ✅ Vue.js前端

---

## 常见问题（FAQ）

### Q1: 为什么首次启动很慢？
**A**: 首次启动需要：
- 下载LLM模型（~几百MB）
- 下载向量模型（~几百MB）
- 构建Faiss索引（~1-2分钟）

后续启动会使用缓存，速度快很多。

### Q2: 可以自定义API Key吗？
**A**: 可以，设置环境变量：
```bash
export SAMBANOVA_API_KEY="your_key"
./start_all.sh
```

### Q3: 如何添加新的梗图？
**A**: 
1. 将图片放到 `dataset/meme/` 目录
2. 在 `dataset/memeWithEmo.csv` 中添加记录
3. 重新构建索引：
```bash
cd member_a_search
python embedding_builder.py
```

### Q4: 支持哪些情绪？
**A**: 系统支持所有中文情绪表达，常见的有：
- 正面：开心、喜悦、兴奋、自豪
- 负面：难过、沮丧、愤怒、无奈
- 中性：疑问、惊讶、思考

### Q5: 可以部署到生产环境吗？
**A**: 可以，但需要：
1. 使用生产级服务器（如Gunicorn）
2. 配置HTTPS
3. 添加限流和认证
4. 使用Redis缓存
5. 监控和日志管理

---

## 技术支持

### 问题反馈
- GitHub Issues: [项目地址]
- 邮箱: [联系邮箱]

### 文档资源
- `PROJECT_REPORT.md` - 完整项目报告
- `ARCHITECTURE_V2.md` - 技术架构说明
- `QUERY_FUSION_STRATEGY.md` - 查询融合策略
- `REASONING_DISPLAY_OPTIMIZATION.md` - UI优化说明

---

**最后更新**: 2025年11月20日  
**版本**: V2.0  
**维护者**: MemeMatch Team
