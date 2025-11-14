"""
会话管理模块

负责管理多用户的对话历史，支持：
1. 会话创建和销毁
2. 历史消息管理
3. 会话过期清理
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器"""
    
    def __init__(self, max_history: int = 10, session_timeout: int = 3600):
        """
        初始化会话管理器
        
        Args:
            max_history: 每个会话保留的最大消息数
            session_timeout: 会话超时时间（秒），默认 1 小时
        """
        self.sessions: Dict[str, Dict] = {}
        self.max_history = max_history
        self.session_timeout = session_timeout
        
        logger.info(f"会话管理器初始化: max_history={max_history}, timeout={session_timeout}s")
    
    def create_session(self, session_id: str, system_prompt: str) -> None:
        """
        创建新会话
        
        Args:
            session_id: 会话 ID
            system_prompt: 系统提示词
        """
        self.sessions[session_id] = {
            "messages": [{"role": "system", "content": system_prompt}],
            "created_at": time.time(),
            "last_active": time.time(),
            "query_count": 0
        }
        logger.info(f"创建新会话: {session_id}")
    
    def get_messages(self, session_id: str, system_prompt: str) -> List[Dict]:
        """
        获取会话的消息历史
        
        Args:
            session_id: 会话 ID
            system_prompt: 系统提示词（用于新会话）
            
        Returns:
            消息列表
        """
        # 清理过期会话
        self._cleanup_expired_sessions()
        
        # 如果会话不存在，创建新会话
        if session_id not in self.sessions:
            self.create_session(session_id, system_prompt)
        
        # 更新最后活跃时间
        self.sessions[session_id]["last_active"] = time.time()
        
        return self.sessions[session_id]["messages"].copy()
    
    def add_message(self, session_id: str, message: Dict) -> None:
        """
        添加消息到会话
        
        Args:
            session_id: 会话 ID
            message: 消息对象 {"role": "user/assistant/tool", "content": "..."}
        """
        if session_id not in self.sessions:
            logger.warning(f"会话不存在: {session_id}")
            return
        
        self.sessions[session_id]["messages"].append(message)
        self.sessions[session_id]["last_active"] = time.time()
        
        # 限制历史长度（保留 system prompt）
        messages = self.sessions[session_id]["messages"]
        if len(messages) > self.max_history + 1:  # +1 for system prompt
            # 保留第一条（system）和最近的 max_history 条
            self.sessions[session_id]["messages"] = [messages[0]] + messages[-(self.max_history):]
            logger.debug(f"会话 {session_id} 历史已裁剪到 {self.max_history} 条")
    
    def update_messages(self, session_id: str, messages: List[Dict]) -> None:
        """
        更新会话的完整消息列表
        
        Args:
            session_id: 会话 ID
            messages: 新的消息列表
        """
        if session_id not in self.sessions:
            logger.warning(f"会话不存在: {session_id}")
            return
        
        self.sessions[session_id]["messages"] = messages
        self.sessions[session_id]["last_active"] = time.time()
        self.sessions[session_id]["query_count"] += 1
    
    def clear_session(self, session_id: str) -> bool:
        """
        清除指定会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            是否成功清除
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"清除会话: {session_id}")
            return True
        return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        获取会话信息
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话信息或 None
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "message_count": len(session["messages"]),
            "query_count": session.get("query_count", 0),
            "created_at": datetime.fromtimestamp(session["created_at"]).isoformat(),
            "last_active": datetime.fromtimestamp(session["last_active"]).isoformat(),
            "age_seconds": time.time() - session["created_at"]
        }
    
    def list_sessions(self) -> List[str]:
        """
        列出所有活跃会话
        
        Returns:
            会话 ID 列表
        """
        return list(self.sessions.keys())
    
    def _cleanup_expired_sessions(self) -> None:
        """清理过期的会话"""
        now = time.time()
        expired = []
        
        for session_id, session in self.sessions.items():
            if now - session["last_active"] > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
            logger.info(f"清理过期会话: {session_id}")
        
        if expired:
            logger.info(f"清理了 {len(expired)} 个过期会话")
    
    def get_stats(self) -> Dict:
        """
        获取会话统计信息
        
        Returns:
            统计信息
        """
        if not self.sessions:
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "total_messages": 0,
                "avg_messages_per_session": 0
            }
        
        total_messages = sum(len(s["messages"]) for s in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len(self.sessions),
            "total_messages": total_messages,
            "avg_messages_per_session": total_messages / len(self.sessions) if self.sessions else 0
        }

