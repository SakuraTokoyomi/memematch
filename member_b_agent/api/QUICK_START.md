# ⚡ 快速开始指南

**3 步启动 API 服务，供 Web 前端调用**

---

## 🚀 启动服务

```bash
cd for_frontend
./start.sh
```

服务启动后：
- **API 地址：** http://localhost:8000
- **交互式文档：** http://localhost:8000/docs

---

## 📡 前端调用示例

### JavaScript/Fetch

```javascript
// 查询梗图
const response = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: '我太累了'
  })
});

const data = await response.json();

if (data.success) {
  console.log('Meme:', data.meme_path);
  console.log('理由:', data.explanation);
  console.log('Session ID:', data.session_id);
}
```

### cURL 测试

```bash
# 查询
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"text": "我太累了"}'

# 健康检查
curl http://localhost:8000/health
```

---

## 📋 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/query` | 查询梗图 |
| DELETE | `/api/session/{id}` | 清除会话 |
| GET | `/api/session/{id}` | 获取会话信息 |
| GET | `/health` | 健康检查 |

---

## 🔄 多轮对话

```javascript
// 第一轮
let result1 = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  body: JSON.stringify({text: '我太累了'})
}).then(r => r.json());

const sessionId = result1.session_id;

// 第二轮（继续对话）
let result2 = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  body: JSON.stringify({
    text: '再来一张',
    session_id: sessionId
  })
}).then(r => r.json());
```

---

## 🧪 测试

```bash
# 自动化测试
python test_api.py

# 查看 API 文档
浏览器打开: http://localhost:8000/docs
```

---

## 📖 完整文档

查看 `README.md` 了解：
- React/Vue/JavaScript 集成示例
- CORS 配置
- 错误处理
- 更多 API 详情

---

**就这么简单！** 🎉

