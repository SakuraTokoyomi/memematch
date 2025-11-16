# 🎭 MemeMatch 前端

智能梗图推荐系统的Vue 3前端界面

## ✨ 功能特性

- 🔍 **智能搜索**：输入心情或想法，AI帮你找梗图
- 🎨 **精美UI**：现代化设计，流畅动画
- 📱 **响应式**：完美适配桌面和移动设备
- 💬 **多语言**：支持中英文混合输入
- 📜 **历史记录**：查看最近的搜索记录
- ⬇️ **快速下载**：一键下载推荐的梗图
- 🔄 **实时状态**：显示后端服务连接状态

## 🚀 快速开始

### 前置条件

- Node.js >= 16
- npm 或 yarn
- 后端API服务运行在 `http://localhost:8000`

### 安装依赖

```bash
cd member_d_frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:3000

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录

## 📁 项目结构

```
member_d_frontend/
├── index.html              # HTML入口
├── vite.config.js          # Vite配置
├── package.json            # 依赖配置
├── src/
│   ├── main.js            # 应用入口
│   ├── App.vue            # 主组件
│   └── api/
│       └── memeApi.js     # API调用封装
└── public/                # 静态资源
```

## 🔌 API接口

### 后端API地址

默认：`http://localhost:8000`

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/query` | POST | 查询梗图 |
| `/health` | GET | 健康检查 |
| `/api/session/{id}` | DELETE | 清除会话 |

## 🎨 界面预览

### 主界面
- 渐变背景
- 搜索框
- 状态指示器
- 快速示例按钮

### 结果展示
- AI分析说明
- 梗图大图展示
- 操作按钮（下载/分享/复制）
- 元数据信息

### 历史记录
- 最近10条搜索
- 点击快速重新搜索

## 🛠️ 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具
- **Axios** - HTTP客户端
- **CSS3** - 现代样式（渐变、动画、响应式）

## 📝 使用说明

### 基本使用

1. 在搜索框输入你的心情或想法
2. 点击"寻找梗图"或按Enter
3. 查看AI推荐的梗图
4. 可以下载、分享或复制路径

### 示例查询

- "我太累了" - 找疲惫相关的梗图
- "今天好开心" - 找开心的表情包
- "I'm confused" - 英文也支持
- "无语了" - 找无语的梗图

### 快速示例

界面提供了几个快速示例按钮，点击即可快速体验

## 🔧 配置

### 修改API地址

编辑 `src/api/memeApi.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url:port'
```

### 修改前端端口

编辑 `vite.config.js`:

```javascript
server: {
  port: 3000  // 改为你想要的端口
}
```

## 🐛 故障排查

### 问题1：无法连接后端

**症状**：状态显示"服务离线"

**解决**：
1. 确保后端服务运行在 `localhost:8000`
2. 检查CORS配置
3. 查看浏览器控制台错误

### 问题2：图片无法显示

**症状**：显示"图片加载失败"

**解决**：
1. 检查后端是否提供静态文件服务
2. 确认图片路径正确
3. 检查网络请求

### 问题3：依赖安装失败

**解决**：
```bash
# 清除缓存
rm -rf node_modules package-lock.json
npm cache clean --force

# 重新安装
npm install
```

## 🎯 开发计划

- [x] 基础UI界面
- [x] API集成
- [x] 响应式设计
- [x] 历史记录
- [ ] 图片上传（反向搜索）
- [ ] Debug面板（显示Agent调用流程）
- [ ] 多梗图对比
- [ ] 收藏功能
- [ ] 主题切换

## 📄 许可证

MIT License

## 👥 贡献

欢迎提Issue和PR！

---

**Enjoy MemeMatch! 🎉**

