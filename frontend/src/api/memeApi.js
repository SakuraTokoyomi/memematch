import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 查询梗图（非流式）
 * @param {string} text - 用户输入的文本
 * @param {string} sessionId - 会话ID（可选）
 * @returns {Promise} API响应
 */
export async function queryMeme(text, sessionId = null) {
  try {
    const response = await apiClient.post('/api/query', {
      text: text,
      session_id: sessionId,
      max_iterations: 4
    })
    return response.data
  } catch (error) {
    console.error('查询失败:', error)
    throw error
  }
}

/**
 * 流式查询梗图
 * @param {string} text - 用户输入的文本
 * @param {string} sessionId - 会话ID（可选）
 * @param {Object} callbacks - 回调函数对象
 * @param {Function} callbacks.onStart - 开始回调
 * @param {Function} callbacks.onToolCall - 工具调用回调
 * @param {Function} callbacks.onComplete - 完成回调
 * @param {Function} callbacks.onError - 错误回调
 * @returns {Function} 取消函数
 */
export function queryMemeStream(text, sessionId = null, callbacks = {}) {
  const {onStart, onToolCall, onComplete, onError} = callbacks
  
  // 构建请求URL和参数
  const params = new URLSearchParams({
    text: text,
    max_iterations: 4
  })
  if (sessionId) {
    params.append('session_id', sessionId)
  }
  
  // 使用fetch发送POST请求并读取流
  fetch(`${API_BASE_URL}/api/query/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      session_id: sessionId,
      max_iterations: 4
    })
  })
  .then(response => {
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    function readStream() {
      reader.read().then(({done, value}) => {
        if (done) {
          console.log('流结束')
          return
        }
        
        // 解码数据
        const chunk = decoder.decode(value, {stream: true})
        const lines = chunk.split('\n')
        
        // 处理每一行
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6))
              
              // 根据事件类型调用对应的回调
              switch (data.type) {
                case 'start':
                  onStart && onStart(data.data)
                  break
                case 'tool_call':
                  onToolCall && onToolCall(data.data)
                  break
                case 'complete':
                  onComplete && onComplete(data.data)
                  break
                case 'error':
                  onError && onError(data.data)
                  break
              }
            } catch (e) {
              console.error('解析SSE数据失败:', e, line)
            }
          }
        }
        
        // 继续读取
        readStream()
      })
    }
    
    readStream()
  })
  .catch(error => {
    console.error('流式查询失败:', error)
    onError && onError({error: error.message})
  })
  
  // 返回取消函数
  return () => {
    console.log('取消流式查询')
  }
}

/**
 * 健康检查
 * @returns {Promise} API响应
 */
export async function healthCheck() {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    console.error('健康检查失败:', error)
    throw error
  }
}

/**
 * 清除会话
 * @param {string} sessionId - 会话ID
 * @returns {Promise} API响应
 */
export async function clearSession(sessionId) {
  try {
    const response = await apiClient.delete(`/api/session/${sessionId}`)
    return response.data
  } catch (error) {
    console.error('清除会话失败:', error)
    throw error
  }
}

/**
 * 创意生成 - 基于原始查询和情绪关键词生成创意梗图
 */
export async function generateCreativeMeme(query, keywords) {
  try {
    const response = await apiClient.post('/api/generate', {
      query: query,
      keywords: keywords
    })
    return response.data
  } catch (error) {
    console.error('创意生成失败:', error)
    throw error
  }
}

export default {
  queryMeme,
  queryMemeStream,
  generateCreativeMeme,
  healthCheck,
  clearSession
}

