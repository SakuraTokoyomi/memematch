# API 测试文档

本文档提供 MemeMatch API 的测试用例和示例。

---

## 🌐 API 基础信息

**Base URL**: `http://localhost:8000`  
**API文档**: `http://localhost:8000/docs`

---

## 📡 接口列表

### 1. 健康检查

**端点**: `GET /health`

**请求示例**:
```bash
curl http://localhost:8000/health
```

**响应**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "agent_ready": true,
  "session_enabled": true
}
```

---

### 2. 流式查询梗图

**端点**: `POST /api/query/stream`  
**Content-Type**: `application/json`  
**响应类型**: `text/event-stream` (SSE)

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| text | string | ✅ | 用户输入的情绪描述 |
| session_id | string | ❌ | 会话ID（用于多轮对话） |

#### 请求示例

```bash
curl -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "我今天太开心了"}'
```

#### SSE 事件流

**事件1: 开始**
```json
data: {"type": "start", "data": {"query": "我今天太开心了"}}
```

**事件2: 情绪提取成功**
```json
data: {
  "type": "tool_call",
  "data": {
    "step": 1,
    "tool": "extract_emotion",
    "result": {"keywords": ["开心"]},
    "status": "success"
  }
}
```

**事件3: 搜索成功**
```json
data: {
  "type": "tool_call",
  "data": {
    "step": 2,
    "tool": "search_meme",
    "arguments": {"query": "我今天太开心了 开心"},
    "result": {"score": 0.85, "found": true, "count": 2},
    "status": "success"
  }
}
```

**事件4: 完成**
```json
data: {
  "type": "complete",
  "data": {
    "success": true,
    "meme_paths": ["/static/001.jpg", "/static/002.jpg"],
    "explanation": "找到了一张很适合表达'开心'的梗图！",
    "source": "search",
    "count": 2,
    "session_id": "session_1732262400"
  }
}
```

#### 错误情况

**事件: 错误**
```json
data: {
  "type": "error",
  "data": {
    "error": "无法识别情绪关键词"
  }
}
```

---

### 3. 创意生成

**端点**: `POST /api/generate`  
**Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| query | string | ✅ | 用户原始查询 |
| keywords | array | ✅ | 情绪关键词列表 |

#### 请求示例

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "我今天太开心了",
    "keywords": ["开心"]
  }'
```

#### 响应

**成功**:
```json
{
  "success": true,
  "meme_path": "/generated/creative_20251122_143256.png",
  "explanation": "基于'开心'创作的doge风格梗图，文案：开心到飞起",
  "source": "generated"
}
```

**失败**:
```json
{
  "success": false,
  "error": "生成失败: 模板不存在"
}
```

---

### 4. 会话管理

#### 4.1 获取会话信息

**端点**: `GET /api/session/{session_id}`

**请求示例**:
```bash
curl http://localhost:8000/api/session/session_1732262400
```

**响应**:
```json
{
  "session_id": "session_1732262400",
  "message_count": 10,
  "query_count": 5,
  "created_at": "2025-11-22T14:00:00",
  "last_active": "2025-11-22T14:32:56",
  "age_seconds": 1976.5
}
```

#### 4.2 清除会话

**端点**: `DELETE /api/session/{session_id}`

**请求示例**:
```bash
curl -X DELETE http://localhost:8000/api/session/session_1732262400
```

**响应**:
```json
{
  "success": true,
  "message": "会话 session_1732262400 已清除"
}
```

---

## 🧪 测试用例

### 用例1: 基础情绪识别

**输入**: "我今天太开心了"  
**预期输出**:
- 情绪关键词: `["开心"]`
- 返回2张图片
- 来源: `search`

**测试命令**:
```bash
curl -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "我今天太开心了"}'
```

---

### 用例2: 复杂情绪提取

**输入**: "项目延期了，压力好大，又累又焦虑"  
**预期输出**:
- 情绪关键词: `["压力", "累", "焦虑"]`
- 返回2张图片
- 来源: `search`

**测试命令**:
```bash
curl -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "项目延期了，压力好大，又累又焦虑"}'
```

---

### 用例3: 分数不足触发生成

**输入**: "我有一种非常特殊的情绪"  
**预期输出**:
- 情绪关键词: `["特殊"]`
- 检索分数 < 0.8
- 触发生成器
- 来源: `generated`

**测试命令**:
```bash
curl -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "我有一种非常特殊的情绪"}'
```

---

### 用例4: 创意生成

**前置条件**: 先执行用例1获取关键词

**输入**:
```json
{
  "query": "我今天太开心了",
  "keywords": ["开心"]
}
```

**预期输出**:
- LLM生成创意文案（如"开心到飞起"）
- 随机模板（drake/doge/wojak之一）
- 返回生成的图片路径
- 来源: `generated`

**测试命令**:
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "我今天太开心了",
    "keywords": ["开心"]
  }'
```

---

### 用例5: 会话持久化

**步骤1**: 创建会话
```bash
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "我今天太开心了"}' | grep session_id | tail -1 | jq -r '.data.session_id')
```

**步骤2**: 查询会话信息
```bash
curl http://localhost:8000/api/session/$SESSION_ID
```

**步骤3**: 清除会话
```bash
curl -X DELETE http://localhost:8000/api/session/$SESSION_ID
```

---

## 🔍 性能测试

### 1. 单次请求延迟

```bash
time curl -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "我今天太开心了"}' \
  > /dev/null
```

**预期**: 1-2秒

### 2. 并发测试

使用 `ab` (Apache Bench):

```bash
# 安装 ab
# macOS: brew install httpd
# Ubuntu: apt-get install apache2-utils

# 100个请求，10个并发
ab -n 100 -c 10 -p query.json -T application/json \
  http://localhost:8000/api/query/stream
```

`query.json`:
```json
{"text": "我今天太开心了"}
```

**预期**:
- 成功率: 100%
- 平均响应时间: < 2秒

### 3. 内存占用

```bash
# 监控后端内存
ps aux | grep api_server | awk '{print $4 " " $6}'
```

**预期**: < 2GB

---

## 🐛 错误处理

### 1. API密钥未设置

**错误**:
```json
{
  "detail": "Agent 服务未就绪"
}
```

**HTTP状态码**: 503

**解决**: 设置 `SAMBANOVA_API_KEY` 环境变量

---

### 2. 无效的请求参数

**错误**:
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**HTTP状态码**: 422

**解决**: 检查请求参数是否完整

---

### 3. 会话不存在

**错误**:
```json
{
  "detail": "会话 session_invalid 不存在"
}
```

**HTTP状态码**: 404

**解决**: 使用有效的 session_id

---

## 📊 监控指标

### 关键指标

| 指标 | 目标值 | 监控方法 |
|------|--------|----------|
| 可用性 | > 99% | 健康检查 |
| 响应时间 | < 2s | 性能测试 |
| 错误率 | < 1% | 日志分析 |
| 内存占用 | < 2GB | 系统监控 |

### 日志查看

```bash
# 实时查看后端日志
tail -f logs/backend.log

# 查找错误
grep ERROR logs/backend.log

# 统计请求量
grep "收到查询请求" logs/backend.log | wc -l
```

---

## 🔗 相关资源

- [FastAPI文档](http://localhost:8000/docs) - 交互式API文档
- [项目报告](PROJECT_REPORT.md) - 技术细节
- [快速启动](QUICKSTART.md) - 部署指南

---

**最后更新**: 2025-11-22

