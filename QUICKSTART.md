# MemeMatch 快速启动指南

## 🚀 5分钟快速上手

本指南帮助您快速启动 MemeMatch 智能梗图推荐系统。

---

## 📋 前置要求

### 必需软件

| 软件 | 版本要求 | 检查命令 | 下载链接 |
|------|----------|----------|----------|
| Python | 3.10+ | `python --version` | [python.org](https://www.python.org/) |
| Node.js | 16+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| npm | 8+ | `npm --version` | (随 Node.js 安装) |

### 系统要求

- **操作系统**: macOS / Linux / Windows
- **内存**: 建议 8GB+
- **磁盘空间**: 5GB+ (模型 + 数据集)
- **网络**: 首次启动需下载模型 (~2GB)

---

## 📥 步骤1: 获取项目

### 方式A: Git Clone（推荐）

```bash
git clone https://github.com/your-org/memematch.git
cd memematch
```

### 方式B: 下载ZIP

1. 访问项目主页，点击 "Download ZIP"
2. 解压到本地目录
3. 进入项目根目录

```bash
cd memematch
```

---

## 🔧 步骤2: 安装依赖

### 2.1 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv backend/venv

# 激活虚拟环境
# macOS/Linux:
source backend/venv/bin/activate
# Windows:
# backend\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**预期耗时**: 5-10 分钟（首次安装）

**可能遇到的问题**:

1. **pip安装慢**: 使用国内镜像
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

2. **权限错误**: 使用 `--user` 参数
   ```bash
   pip install --user -r requirements.txt
   ```

### 2.2 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

**预期耗时**: 3-5 分钟

**可能遇到的问题**:

1. **npm安装慢**: 使用国内镜像
   ```bash
   npm install --registry=https://registry.npmmirror.com
   ```

---

## 🔑 步骤3: 配置API密钥

MemeMatch 使用 SambaNova Cloud 提供的免费 LLM 服务。

### 3.1 获取API密钥

1. 访问 [SambaNova Cloud](https://cloud.sambanova.ai/)
2. 注册账号（免费）
3. 创建 API Key
4. 复制 API Key

### 3.2 设置环境变量

**macOS/Linux**:
```bash
export SAMBANOVA_API_KEY="your-api-key-here"
```

**Windows CMD**:
```cmd
set SAMBANOVA_API_KEY=your-api-key-here
```

**Windows PowerShell**:
```powershell
$env:SAMBANOVA_API_KEY="your-api-key-here"
```

**持久化配置（可选）**:

创建 `.env` 文件：
```bash
echo 'SAMBANOVA_API_KEY=your-api-key-here' > .env
```

---

## 🎬 步骤4: 启动服务

### 一键启动（推荐）

```bash
./scripts/start.sh
```

**启动内容**:
- ✅ 后端服务 (http://localhost:8000)
- ✅ 前端服务 (http://localhost:3000)
- ✅ 自动打开浏览器

**日志位置**:
- 后端日志: `logs/backend.log`
- 前端日志: `logs/frontend.log`

### 手动启动（可选）

如果一键启动失败，可手动启动：

**终端1 - 启动后端**:
```bash
cd backend
source venv/bin/activate
python api/api_server.py
```

**终端2 - 启动前端**:
```bash
cd frontend
npm run dev
```

---

## 🎉 步骤5: 开始使用

### 5.1 访问应用

浏览器打开: [http://localhost:3000](http://localhost:3000)

### 5.2 试用示例

在输入框输入以下任意一句，查看效果：

| 输入 | 预期输出 |
|------|----------|
| "我今天太开心了" | 返回2张"开心"主题梗图 |
| "累死了不想上班" | 返回2张"累"主题梗图 |
| "无语了这也行" | 返回2张"无语"主题梗图 |

### 5.3 功能演示

#### 功能1: 智能推荐
1. 输入情绪描述
2. 系统显示推理过程：
   - 💡 情绪识别
   - 🔍 梗图检索
3. 返回2张匹配图片

#### 功能2: 创意生成
1. 在返回的结果下方，点击 **🎨 创意生成**
2. 系统生成创意文案（如"开心到飞起"）
3. 返回个性化梗图

---

## 🛑 停止服务

```bash
./scripts/stop.sh
```

或手动停止：
- **Ctrl + C** 终止正在运行的终端进程
- 查找并杀死进程：
  ```bash
  # macOS/Linux
  pkill -f api_server
  pkill -f vite
  ```

---

## 🔍 验证安装

### 检查后端

访问 [http://localhost:8000/health](http://localhost:8000/health)

**预期响应**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "agent_ready": true,
  "session_enabled": true
}
```

### 检查前端

访问 [http://localhost:3000](http://localhost:3000)

**预期界面**:
- 显示 "MemeMatch" 标题
- 有输入框和发送按钮
- 界面清爽，无报错

### API文档

访问 [http://localhost:8000/docs](http://localhost:8000/docs)

查看完整的 API 文档（FastAPI 自动生成）

---

## ❓ 常见问题

### 1. 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
# macOS/Linux:
lsof -i :8000
lsof -i :3000

# 杀死进程
kill -9 <PID>
```

### 2. 模块导入错误

**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
# 确认虚拟环境已激活
which python  # 应该显示 .../venv/bin/python

# 重新安装依赖
pip install -r requirements.txt
```

### 3. API密钥未设置

**错误**: `SAMBANOVA_API_KEY not found`

**解决**:
```bash
# 检查环境变量
echo $SAMBANOVA_API_KEY

# 如果为空，重新设置
export SAMBANOVA_API_KEY="your-api-key"
```

### 4. 模型下载慢

**现象**: 首次启动时，下载模型很慢

**解决**:
- 使用科学上网工具
- 或等待下载完成（一次性，约2GB）
- 模型缓存位置: `~/.cache/huggingface/`

### 5. 图片无法显示

**现象**: 返回结果显示"图片加载失败"

**排查**:
1. 检查数据集是否存在:
   ```bash
   ls data/dataset/meme/
   ```
2. 检查静态服务是否正常:
   ```bash
   curl http://localhost:8000/static/001.jpg
   ```
3. 检查浏览器控制台错误信息

### 6. 内存不足

**现象**: 服务启动后崩溃

**解决**:
- 关闭其他占用内存的应用
- 使用更小的模型（修改 `backend/search/config.py`）
- 增加系统虚拟内存

---

## 📖 更多资源

### 文档

- [项目报告](PROJECT_REPORT.md) - 详细技术文档
- [API文档](http://localhost:8000/docs) - 接口说明

### 示例视频

- [功能演示视频](docs/demo.mp4)
- [部署教程视频](docs/deployment.mp4)

### 社区支持

- **GitHub Issues**: 报告Bug和功能请求
- **讨论区**: 技术交流和问答
- **邮件**: contact@memematch.com

---

## 🎯 下一步

恭喜！您已经成功启动 MemeMatch。

**探索更多功能**:
- 📚 阅读 [项目报告](PROJECT_REPORT.md) 了解技术细节
- 🔧 自定义配置文件 (`backend/*/config.py`)
- 🎨 修改前端样式 (`frontend/src/App.vue`)
- 📊 添加自己的梗图数据集

**遇到问题？**
- 查看 [常见问题](#❓-常见问题)
- 查看日志文件 (`logs/*.log`)
- 提交 [GitHub Issue](https://github.com/your-org/memematch/issues)

---

**祝您使用愉快！** 🎉

