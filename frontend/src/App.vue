<template>
  <div id="app">
    <!-- 头部 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo-icon">🎭</div>
          <div class="logo-text">
            <h1 class="title">Meme Match</h1>
            <p class="subtitle">智能梗图推荐助手</p>
          </div>
        </div>
        
        <!-- Session 控制 -->
        <div class="session-controls">
          <div class="session-info">
            <span class="session-label">Session:</span>
            <span class="session-id">{{ sessionId ? sessionId.substring(8, 16) : '单次' }}</span>
          </div>
          <button 
            v-if="sessionId" 
            @click="clearSessionData"
            class="btn btn-danger"
          >
            清除对话
          </button>
          <button 
            v-else
            @click="createSession"
            class="btn btn-success"
          >
            启用会话
          </button>
        </div>
      </div>
    </header>

    <!-- 对话区域 -->
    <main class="chat-container">
      <div class="chat-messages" ref="chatMessages">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-icon">👋</div>
          <h2>你好！我是 Meme Agent</h2>
          <p>告诉我你的心情，我会为你推荐最合适的梗图～</p>
          <div class="example-queries">
            <button @click="exampleQuery('累了')" class="example-btn">累了</button>
            <button @click="exampleQuery('开心')" class="example-btn">开心</button>
            <button @click="exampleQuery('无语')" class="example-btn">无语</button>
            <button @click="exampleQuery('服了')" class="example-btn">服了</button>
          </div>
        </div>

        <!-- 对话消息 -->
        <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
          <!-- 用户消息 -->
          <div v-if="message.type === 'user'" class="message message-user">
            <div class="message-bubble user-bubble">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
            <div class="message-avatar user-avatar">👤</div>
          </div>

          <!-- AI消息 -->
          <div v-else-if="message.type === 'assistant'" class="message message-assistant">
            <div class="message-avatar ai-avatar">🤖</div>
            <div class="message-bubble ai-bubble">
              <!-- 推理过程 -->
              <div v-if="message.reasoning && message.reasoning.length > 0" class="reasoning-process">
                <div class="reasoning-header">💭 思考过程</div>
                <div v-for="(step, idx) in message.reasoning" :key="idx" class="reasoning-step">
                  <span class="step-number">{{ idx + 1 }}.</span>
                  <span class="step-text">{{ formatStepText(step) }}</span>
                </div>
              </div>

              <!-- 梗图结果 -->
              <div v-if="message.meme" class="meme-result">
                <img 
                  :src="`http://localhost:8000${message.meme.path}`" 
                  :alt="message.meme.explanation"
                  class="meme-image"
                  @error="handleImageError"
                />
                <div class="meme-explanation">
                  {{ message.meme.explanation }}
                </div>
                <div class="meme-source">
                  <span class="source-badge">{{ message.meme.source === 'search' ? '📚 检索' : '✨ 生成' }}</span>
                </div>
              </div>

              <!-- 错误消息 -->
              <div v-if="message.error" class="error-message">
                <span class="error-icon">❌</span>
                <span>{{ message.error }}</span>
              </div>

              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>

          <!-- 加载中状态 -->
          <div v-else-if="message.type === 'loading'" class="message message-assistant">
            <div class="message-avatar ai-avatar">🤖</div>
            <div class="message-bubble ai-bubble">
              <!-- 推理过程（实时更新） -->
              <div v-if="message.reasoning && message.reasoning.length > 0" class="reasoning-process">
                <div class="reasoning-header">💭 思考过程</div>
                <div v-for="(step, idx) in message.reasoning" :key="idx" class="reasoning-step">
                  <span class="step-number">{{ idx + 1 }}.</span>
                  <span class="step-text">{{ formatStepText(step) }}</span>
                </div>
              </div>
              
              <!-- 加载指示器 -->
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-container">
          <input
            v-model="userInput"
            @keyup.enter="submitQuery"
            type="text"
            placeholder="输入你的心情..."
            class="chat-input"
            :disabled="loading"
          />
          <button
            @click="submitQuery"
            :disabled="loading || !userInput.trim()"
            class="send-btn"
          >
            <span v-if="!loading">📤</span>
            <span v-else class="spinner">⏳</span>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { queryMemeStream, clearSession } from './api/memeApi'

export default {
  name: 'App',
  data() {
    return {
      userInput: '',
      loading: false,
      sessionId: null,
      messages: [], // 所有对话消息
      currentReasoning: [], // 当前正在推理的步骤
    }
  },
  mounted() {
    // 从localStorage恢复session
    const savedSession = localStorage.getItem('meme_session_id')
    if (savedSession) {
      this.sessionId = savedSession
    }
    
    // 从localStorage恢复对话历史
    const savedMessages = localStorage.getItem('meme_messages')
    if (savedMessages) {
      this.messages = JSON.parse(savedMessages)
    }
  },
  methods: {
    createSession() {
      this.sessionId = `session_${Date.now()}`
      localStorage.setItem('meme_session_id', this.sessionId)
    },
    
    async clearSessionData() {
      if (this.sessionId) {
        try {
          await clearSession(this.sessionId)
        } catch (e) {
          console.error('清除session失败:', e)
        }
      }
      this.sessionId = null
      this.messages = []
      localStorage.removeItem('meme_session_id')
      localStorage.removeItem('meme_messages')
    },
    
    exampleQuery(text) {
      this.userInput = text
      this.submitQuery()
    },
    
    submitQuery() {
      if (!this.userInput.trim() || this.loading) return
      
      const query = this.userInput.trim()
      this.userInput = ''
      
      // 添加用户消息
      this.messages.push({
        type: 'user',
        content: query,
        timestamp: Date.now()
      })
      
      // 添加加载状态
      this.messages.push({
        type: 'loading',
        timestamp: Date.now()
      })
      
      this.loading = true
      this.currentReasoning = []
      
      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom()
      })
      
      // 使用流式API
      queryMemeStream(query, this.sessionId, {
        onStart: (data) => {
          console.log('查询开始:', data)
        },
        onToolCall: (data) => {
          console.log('工具调用:', data)
          
          // 只保留最终结果（status为success/failed/low_score），过滤掉running状态
          if (data.status !== 'running') {
            this.currentReasoning.push(data)
            // 实时更新推理过程（但不改变消息类型）
            const lastMessage = this.messages[this.messages.length - 1]
            if (lastMessage && (lastMessage.type === 'loading' || lastMessage.type === 'assistant')) {
              lastMessage.reasoning = [...this.currentReasoning]
            }
            this.$nextTick(() => {
              this.scrollToBottom()
            })
          }
        },
        onComplete: (data) => {
          console.log('查询完成:', data)
          this.loading = false
          
          // 查找loading消息或已转换的assistant消息
          const lastMessage = this.messages[this.messages.length - 1]
          
          if (data.success) {
            // 更新现有消息，而不是创建新消息
            if (lastMessage && (lastMessage.type === 'loading' || lastMessage.type === 'assistant')) {
              lastMessage.type = 'assistant'
              lastMessage.reasoning = this.currentReasoning
              lastMessage.meme = {
                path: data.meme_path,
                explanation: data.explanation,
                source: data.source
              }
              lastMessage.timestamp = Date.now()
            } else {
              // 降级：如果找不到消息，创建新的
              this.messages.push({
                type: 'assistant',
                reasoning: this.currentReasoning,
                meme: {
                  path: data.meme_path,
                  explanation: data.explanation,
                  source: data.source
                },
                timestamp: Date.now()
              })
            }
            
            this.sessionId = data.session_id || this.sessionId
            if (data.session_id) {
              localStorage.setItem('meme_session_id', data.session_id)
            }
          } else {
            // 错误情况：更新或创建错误消息
            if (lastMessage && (lastMessage.type === 'loading' || lastMessage.type === 'assistant')) {
              lastMessage.type = 'assistant'
              lastMessage.error = data.error || '查询失败'
              lastMessage.timestamp = Date.now()
            } else {
              this.messages.push({
                type: 'assistant',
                error: data.error || '查询失败',
                timestamp: Date.now()
              })
            }
          }
          
          // 保存消息到localStorage
          localStorage.setItem('meme_messages', JSON.stringify(this.messages))
          
          this.$nextTick(() => {
            this.scrollToBottom()
          })
        },
        onError: (data) => {
          console.error('查询错误:', data)
          this.loading = false
          
          // 移除loading消息
          const loadingIndex = this.messages.findIndex(m => m.type === 'loading')
          if (loadingIndex !== -1) {
            this.messages.splice(loadingIndex, 1)
          }
          
          this.messages.push({
            type: 'assistant',
            error: data.error || '发生未知错误',
            timestamp: Date.now()
          })
          
          this.$nextTick(() => {
            this.scrollToBottom()
          })
        }
      })
    },
    
    scrollToBottom() {
      const container = this.$refs.chatMessages
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    formatTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    },
    
    formatStepText(step) {
      // 新架构的格式化逻辑
      if (step.tool === 'extract_emotion') {
        const keywords = step.result?.keywords || []
        return `💡 情绪识别：${keywords.join('、')}`
      } else if (step.tool === 'search_meme') {
        const query = step.arguments?.query || ''
        if (step.status === 'success') {
          const score = step.result?.score || 0
          return `🔍 梗图检索：找到匹配"${query}"的图片（相似度 ${(score * 100).toFixed(0)}%）`
        } else if (step.status === 'low_score') {
          const score = step.result?.score || 0
          return `⚠️ 检索结果：匹配度不足（${(score * 100).toFixed(0)}%），准备生成新图`
        } else if (step.status === 'failed') {
          return `❌ 检索失败：未找到"${query}"相关图片，准备生成新图`
        }
      } else if (step.tool === 'generate_meme') {
        const text = step.arguments?.text || ''
        const template = step.arguments?.template || 'wojak'
        if (step.status === 'success') {
          return `✨ 图片生成：已生成"${text}"主题梗图（模板：${template}）`
        }
      }
      
      // 降级：返回工具名
      return `${step.tool} (${step.status})`
    },
    
    
    handleImageError(event) {
      console.error('图片加载失败:', event.target.src)
      event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23ddd" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3E图片加载失败%3C/text%3E%3C/svg%3E'
    }
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
}

/* 头部 */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 36px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.subtitle {
  font-size: 12px;
  opacity: 0.9;
  margin: 2px 0 0 0;
}

.session-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.session-id {
  padding: 4px 10px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  font-family: 'Courier New', monospace;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger {
  background: rgba(239, 68, 68, 0.9);
  color: white;
}

.btn-danger:hover {
  background: rgba(220, 38, 38, 0.9);
}

.btn-success {
  background: rgba(16, 185, 129, 0.9);
  color: white;
}

.btn-success:hover {
  background: rgba(5, 150, 105, 0.9);
}

/* 对话容器 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.welcome-message h2 {
  font-size: 28px;
  color: #333;
  margin: 0 0 10px 0;
}

.welcome-message p {
  font-size: 16px;
  margin: 0 0 30px 0;
}

.example-queries {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.example-btn {
  padding: 10px 20px;
  background: white;
  border: 2px solid #667eea;
  color: #667eea;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.example-btn:hover {
  background: #667eea;
  color: white;
}

/* 消息样式 */
.message-wrapper {
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.ai-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
}

.user-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-bubble {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.message-text {
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 6px;
  text-align: right;
}

/* 推理过程 */
.reasoning-process {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.reasoning-header {
  font-size: 13px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 8px;
}

.reasoning-step {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 6px 0;
  font-size: 13px;
}

.step-number {
  min-width: 20px;
  font-weight: 700;
  color: #667eea;
  font-size: 13px;
}

.step-text {
  color: #374151;
  flex: 1;
  line-height: 1.6;
}

/* 梗图结果 */
.meme-result {
  margin-top: 8px;
}

.meme-image {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  margin-bottom: 12px;
}

.meme-explanation {
  font-size: 15px;
  line-height: 1.6;
  color: #333;
  padding: 12px;
  background: linear-gradient(135deg, #f3e7ff 0%, #fce7f3 100%);
  border-radius: 8px;
  margin-bottom: 8px;
}

.meme-source {
  text-align: right;
}

.source-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 12px;
  font-size: 12px;
}

/* 错误消息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fef2f2;
  border-radius: 8px;
  color: #dc2626;
}

.error-icon {
  font-size: 20px;
}

/* 加载动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* 输入区域 */
.chat-input-area {
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 15px 20px;
}

.input-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 10px;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 24px;
  font-size: 15px;
  transition: border-color 0.2s;
}

.chat-input:focus {
  outline: none;
  border-color: #667eea;
}

.chat-input:disabled {
  background: #f9fafb;
  cursor: not-allowed;
}

.send-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .message-bubble {
    max-width: 85%;
  }
  
  .meme-image {
    max-width: 100%;
  }
}
</style>
