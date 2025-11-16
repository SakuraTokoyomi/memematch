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
 * 查询梗图
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

export default {
  queryMeme,
  healthCheck,
  clearSession
}

