<template>
  <div class="app-container">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <h1 class="title">
          <span class="emoji">🎭</span>
          MemeMatch
        </h1>
        <p class="subtitle">AI驱动的智能梗图推荐</p>
        <div class="status-badge" :class="{ 'online': isOnline, 'offline': !isOnline }">
          <span class="dot"></span>
          {{ isOnline ? '服务在线' : '服务离线' }}
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="container">
        
        <!-- Search Box -->
        <div class="search-section">
          <div class="search-box">
            <textarea 
              v-model="userInput"
              @keydown.enter.exact.prevent="handleSearch"
              placeholder="告诉我你现在的心情或想法... 🤔&#10;例如：我太累了 / I'm so tired / 今天好开心"
              class="search-input"
              :disabled="isLoading"
            ></textarea>
            <button 
              @click="handleSearch" 
              class="search-button"
              :disabled="isLoading || !userInput.trim()"
            >
              <span v-if="!isLoading">🔍 寻找梗图</span>
              <span v-else class="loading-text">
                <span class="spinner"></span>
                思考中...
              </span>
            </button>
          </div>
          
          <!-- Quick Examples -->
          <div class="examples">
            <span class="examples-label">试试这些：</span>
            <button 
              v-for="example in examples" 
              :key="example"
              @click="userInput = example; handleSearch()"
              class="example-btn"
              :disabled="isLoading"
            >
              {{ example }}
            </button>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-message">
          <span class="error-icon">⚠️</span>
          <div>
            <div class="error-title">哎呀，出错了</div>
            <div class="error-detail">{{ error }}</div>
          </div>
          <button @click="error = null" class="close-btn">✕</button>
        </div>

        <!-- Results -->
        <div v-if="result" class="results-section">
          
          <!-- AI Explanation -->
          <div class="explanation-card">
            <h3 class="card-title">
              <span class="icon">💡</span>
              AI 分析
            </h3>
            <p class="explanation-text">{{ result.explanation || '找到了适合你的梗图！' }}</p>
            <div class="meta-info">
              <span class="meta-item">
                <span class="meta-icon">🎯</span>
                来源: {{ result.source || '搜索引擎' }}
              </span>
              <span class="meta-item" v-if="result.session_id">
                <span class="meta-icon">💬</span>
                会话: {{ result.session_id.slice(0, 8) }}...
              </span>
            </div>
          </div>

          <!-- Main Meme Display -->
          <div class="meme-display">
            <h3 class="card-title">
              <span class="icon">🖼️</span>
              推荐梗图
            </h3>
            <div v-if="result.meme_path" class="meme-card main-meme">
              <div class="meme-image-container">
                <img 
                  :src="getMemeUrl(result.meme_path)" 
                  :alt="result.explanation"
                  class="meme-image"
                  @error="handleImageError"
                />
              </div>
              <div class="meme-actions">
                <button @click="downloadMeme(result.meme_path)" class="action-btn download">
                  <span>⬇️</span> 下载
                </button>
                <button @click="shareMeme(result.meme_path)" class="action-btn share">
                  <span>📤</span> 分享
                </button>
                <button @click="copyPath(result.meme_path)" class="action-btn copy">
                  <span>📋</span> 复制路径
                </button>
              </div>
            </div>
            <div v-else class="no-meme">
              <span class="no-meme-icon">🤷</span>
              <p>未找到合适的梗图</p>
            </div>
          </div>

        </div>

        <!-- History (Optional) -->
        <div v-if="history.length > 0" class="history-section">
          <h3 class="card-title">
            <span class="icon">📜</span>
            历史记录
          </h3>
          <div class="history-list">
            <div 
              v-for="(item, index) in history.slice().reverse()" 
              :key="index"
              class="history-item"
              @click="userInput = item.query; handleSearch()"
            >
              <span class="history-query">{{ item.query }}</span>
              <span class="history-time">{{ formatTime(item.time) }}</span>
            </div>
          </div>
        </div>

      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>MemeMatch © 2024 | Powered by AI</p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { queryMeme, healthCheck } from './api/memeApi'

export default {
  name: 'App',
  setup() {
    const userInput = ref('')
    const result = ref(null)
    const isLoading = ref(false)
    const error = ref(null)
    const isOnline = ref(false)
    const history = ref([])
    
    const examples = [
      '我太累了',
      '今天好开心',
      'I\'m confused',
      '无语了',
      '震惊'
    ]

    // 健康检查
    const checkHealth = async () => {
      try {
        await healthCheck()
        isOnline.value = true
      } catch (err) {
        isOnline.value = false
      }
    }

    // 处理搜索
    const handleSearch = async () => {
      if (!userInput.value.trim() || isLoading.value) return
      
      isLoading.value = true
      error.value = null
      result.value = null
      
      try {
        const response = await queryMeme(userInput.value.trim())
        
        if (response.success) {
          result.value = response
          
          // 添加到历史
          history.value.push({
            query: userInput.value.trim(),
            time: new Date()
          })
          
          // 限制历史记录数量
          if (history.value.length > 10) {
            history.value.shift()
          }
        } else {
          error.value = response.error || '查询失败，请重试'
        }
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || '网络错误，请检查后端服务是否运行'
        console.error('Search error:', err)
      } finally {
        isLoading.value = false
      }
    }

    // 获取图片URL
    const getMemeUrl = (path) => {
      if (!path) return ''
      // 假设后端提供了静态文件服务
      if (path.startsWith('http')) {
        return path
      }
      return `http://localhost:8000/static/${path.replace(/^.*\/meme\//, '')}`
    }

    // 图片加载错误处理
    const handleImageError = (e) => {
      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect fill="%23f0f0f0" width="400" height="400"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-family="sans-serif" font-size="20"%3E图片加载失败%3C/text%3E%3C/svg%3E'
    }

    // 下载梗图
    const downloadMeme = (path) => {
      const url = getMemeUrl(path)
      const a = document.createElement('a')
      a.href = url
      a.download = path.split('/').pop()
      a.click()
    }

    // 分享梗图
    const shareMeme = (path) => {
      if (navigator.share) {
        navigator.share({
          title: 'MemeMatch 推荐',
          text: `看看这个梗图：${result.value.explanation}`,
          url: window.location.href
        })
      } else {
        alert('您的浏览器不支持分享功能')
      }
    }

    // 复制路径
    const copyPath = (path) => {
      navigator.clipboard.writeText(path).then(() => {
        alert('路径已复制到剪贴板')
      })
    }

    // 格式化时间
    const formatTime = (time) => {
      const now = new Date()
      const diff = (now - time) / 1000 // 秒
      
      if (diff < 60) return '刚刚'
      if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
      if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
      return time.toLocaleDateString()
    }

    onMounted(() => {
      checkHealth()
      // 定期检查健康状态
      setInterval(checkHealth, 30000)
    })

    return {
      userInput,
      result,
      isLoading,
      error,
      isOnline,
      history,
      examples,
      handleSearch,
      getMemeUrl,
      handleImageError,
      downloadMeme,
      shareMeme,
      copyPath,
      formatTime
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  padding: 2rem 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
}

.title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.emoji {
  font-size: 3.5rem;
  margin-right: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.status-badge.online {
  background: #d4edda;
  color: #155724;
}

.status-badge.offline {
  background: #f8d7da;
  color: #721c24;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 3rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Search Section */
.search-section {
  margin-bottom: 2rem;
}

.search-box {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  min-height: 120px;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s;
  margin-bottom: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.search-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.search-button {
  width: 100%;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.search-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Examples */
.examples {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.examples-label {
  color: #666;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.example-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.example-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #667eea;
  color: #667eea;
}

.example-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Error Message */
.error-message {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.error-icon {
  font-size: 1.5rem;
}

.error-title {
  font-weight: 600;
  color: #856404;
  margin-bottom: 0.25rem;
}

.error-detail {
  color: #856404;
  font-size: 0.9rem;
}

.close-btn {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #856404;
}

/* Results Section */
.results-section {
  display: grid;
  gap: 2rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: #333;
}

.icon {
  font-size: 1.5rem;
}

/* Explanation Card */
.explanation-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.explanation-text {
  color: #555;
  line-height: 1.6;
  font-size: 1.05rem;
  margin-bottom: 1rem;
}

.meta-info {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #888;
  font-size: 0.9rem;
}

.meta-icon {
  font-size: 1rem;
}

/* Meme Display */
.meme-display {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.meme-card {
  border: 2px solid #f0f0f0;
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.meme-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.meme-image-container {
  background: #f8f8f8;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.meme-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  border-radius: 8px;
}

.meme-actions {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
}

.action-btn:hover {
  background: #f0f0f0;
  border-color: #667eea;
  color: #667eea;
}

.action-btn span {
  font-size: 1.1rem;
}

.no-meme {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.no-meme-icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 1rem;
}

/* History Section */
.history-section {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f8f8;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: #f0f0f0;
}

.history-query {
  color: #333;
  font-weight: 500;
}

.history-time {
  color: #999;
  font-size: 0.85rem;
}

/* Footer */
.footer {
  background: rgba(255, 255, 255, 0.9);
  padding: 1.5rem;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
  .title {
    font-size: 2rem;
  }
  
  .emoji {
    font-size: 2.5rem;
  }
  
  .container {
    padding: 0 1rem;
  }
  
  .meta-info {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .meme-actions {
    flex-direction: column;
  }
}
</style>

