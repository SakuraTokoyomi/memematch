"""
Meme Agent API 服务

FastAPI 服务，为 Web 前端提供 HTTP 接口
"""

import os
import sys
from typing import Optional

# 添加项目路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import logging
import json
import asyncio
from typing import AsyncGenerator

from agent.agent_core import create_agent
from agent.real_tools import setup_real_tools  # 使用真实搜索引擎
from agent.session_manager import SessionManager


# ============ 配置 ============

# 设置日志 - 显示详细信息
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Meme Agent API",
    description="智能梗图推荐服务",
    version="2.0.0"
)

# 配置 CORS（允许跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该改为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件服务 - 提供图片访问
# 将 dataset/meme 目录映射到 /static/ 路径
MEME_IMAGE_DIR = os.path.join(os.path.dirname(parent_dir), 'dataset', 'meme')
if os.path.exists(MEME_IMAGE_DIR):
    app.mount("/static", StaticFiles(directory=MEME_IMAGE_DIR), name="static")
    logger.info(f"✅ 静态文件服务已配置: {MEME_IMAGE_DIR} -> /static/")
else:
    logger.warning(f"⚠️  图片目录不存在: {MEME_IMAGE_DIR}")


# ============ 全局变量 ============

# Agent 实例（全局单例）
agent = None
session_manager = None


# ============ 数据模型 ============

class QueryRequest(BaseModel):
    """查询请求"""
    text: str
    session_id: Optional[str] = None
    max_iterations: Optional[int] = 4
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "我太累了",
                "session_id": "optional-session-id"
            }
        }


class QueryResponse(BaseModel):
    """查询响应"""
    success: bool
    meme_path: Optional[str] = None
    explanation: Optional[str] = None
    source: Optional[str] = None
    session_id: Optional[str] = None
    error: Optional[str] = None


class StreamEvent(BaseModel):
    """流式事件"""
    type: str  # status, tool_call, result, complete, error
    data: dict


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    message_count: int
    query_count: int
    created_at: str
    last_active: str
    age_seconds: float


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    agent_ready: bool
    session_enabled: bool


# ============ 启动事件 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global agent, session_manager
    
    logger.info("🚀 初始化 Meme Agent 服务...")
    
    # 创建会话管理器
    session_manager = SessionManager(
        max_history=10,
        session_timeout=3600
    )
    
    # 创建 Agent（使用配置中的默认API key）
    agent = create_agent(
        api_key=os.getenv("SAMBANOVA_API_KEY") or "9a2266c7-a96a-4459-be90-af5dfc58a655",
        model="Meta-Llama-3.1-8B-Instruct"
    )
    agent.session_manager = session_manager
    
    # 注册工具（使用真实搜索引擎）
    setup_real_tools(agent)
    
    # 配置日志级别 - 显示完整的处理流程
    logger.info("🐛 详细日志模式已启用（DEBUG级别）")
    
    # Agent核心模块显示DEBUG级别（包含所有详细日志）
    logging.getLogger("agent.agent_core").setLevel(logging.DEBUG)
    logging.getLogger("agent.real_tools").setLevel(logging.DEBUG)
    logging.getLogger("agent.session_manager").setLevel(logging.DEBUG)
    
    # 隐藏第三方库的详细日志
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    
    logger.info("✅ Agent 服务初始化完成")


# ============ API 路由 ============

@app.get("/", response_model=dict)
async def root():
    """根路径 - API 说明"""
    return {
        "name": "Meme Agent API",
        "version": "2.0.0",
        "endpoints": {
            "POST /api/query": "查询梗图",
            "DELETE /api/session/{session_id}": "清除会话",
            "GET /api/session/{session_id}": "获取会话信息",
            "GET /health": "健康检查"
        },
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "agent_ready": agent is not None,
        "session_enabled": session_manager is not None
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_meme(request: QueryRequest):
    """
    查询梗图接口（非流式）
    
    支持单次查询和多轮对话
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent 服务未就绪")
    
    try:
        # 调用 Agent
        logger.info(f"📥 收到查询请求: {request.text[:50]}...")
        
        result = agent.process_query(
            user_query=request.text,
            max_iterations=request.max_iterations,
            session_id=request.session_id
        )
        
        # 🐛 DEBUG: 打印Agent返回的完整结果
        logger.debug(f"🔍 Agent返回结果: {result}")
        
        # 转换为标准响应格式
        if result.get("status") == "success":
            response = QueryResponse(
                success=True,
                meme_path=result.get("meme_path"),
                explanation=result.get("explanation"),
                source=result.get("source"),
                session_id=result.get("session_id")
            )
            
            # 🐛 DEBUG: 打印API响应
            logger.debug(f"📤 API响应: success={response.success}, meme_path={response.meme_path}")
            logger.info(f"✅ 查询成功: {response.meme_path}")
            
            return response
        else:
            error_msg = result.get("error", "未知错误")
            logger.warning(f"❌ 查询失败: {error_msg}")
            
            return QueryResponse(
                success=False,
                error=error_msg,
                session_id=result.get("session_id")
            )
    
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query/stream")
async def query_meme_stream(request: QueryRequest):
    """
    流式查询梗图接口
    
    实时返回Agent的推理过程
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent 服务未就绪")
    
    async def generate_events() -> AsyncGenerator[str, None]:
        """生成SSE事件流"""
        try:
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'data': {'query': request.text, 'session_id': request.session_id}}, ensure_ascii=False)}\n\n"
            
            logger.info(f"📥 [流式] 收到查询请求: {request.text[:50]}...")
            
            # 这里我们需要修改agent_core.py来支持流式输出
            # 目前先同步执行，然后分步发送结果
            result = await asyncio.to_thread(
                agent.process_query,
                user_query=request.text,
                max_iterations=request.max_iterations,
                session_id=request.session_id
            )
            
            # 发送推理步骤
            if result.get("reasoning_steps"):
                for step in result["reasoning_steps"]:
                    event_data = {
                        'type': 'tool_call',
                        'data': {
                            'step': step['step'],
                            'tool': step['tool'],
                            'arguments': step['arguments'],
                            'result': step['result']
                        }
                    }
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.1)  # 模拟实时感
            
            # 发送最终结果
            if result.get("status") == "success":
                final_data = {
                    'type': 'complete',
                    'data': {
                        'success': True,
                        'meme_path': result.get("meme_path"),
                        'explanation': result.get("explanation"),
                        'source': result.get("source"),
                        'session_id': result.get("session_id")
                    }
                }
                yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
                logger.info(f"✅ [流式] 查询成功: {result.get('meme_path')}")
            else:
                error_data = {
                    'type': 'error',
                    'data': {
                        'success': False,
                        'error': result.get("error", "未知错误"),
                        'session_id': result.get("session_id")
                    }
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                logger.warning(f"❌ [流式] 查询失败: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"[流式] 查询失败: {e}", exc_info=True)
            error_data = {
                'type': 'error',
                'data': {'success': False, 'error': str(e)}
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.delete("/api/session/{session_id}", response_model=dict)
async def clear_session(session_id: str):
    """清除指定会话"""
    if session_manager is None:
        raise HTTPException(status_code=503, detail="会话管理器未启用")
    
    success = session_manager.clear_session(session_id)
    
    if success:
        return {"success": True, "message": f"会话 {session_id} 已清除"}
    else:
        return {"success": False, "message": f"会话 {session_id} 不存在"}


@app.get("/api/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """获取会话信息"""
    if session_manager is None:
        raise HTTPException(status_code=503, detail="会话管理器未启用")
    
    info = session_manager.get_session_info(session_id)
    
    if info is None:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    return SessionInfo(**info)


@app.get("/api/stats", response_model=dict)
async def get_stats():
    """获取服务统计信息"""
    if session_manager is None:
        raise HTTPException(status_code=503, detail="会话管理器未启用")
    
    stats = session_manager.get_stats()
    return {
        "agent_version": "2.0.0",
        "sessions": stats
    }


# ============ 主函数 ============

def main():
    """启动服务"""
    print("\n" + "="*60)
    print("🎭 Meme Agent API 服务")
    print("="*60)
    print("\n启动配置：")
    print(f"  地址: http://0.0.0.0:8000")
    print(f"  文档: http://0.0.0.0:8000/docs")
    print(f"  会话管理: 已启用")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

