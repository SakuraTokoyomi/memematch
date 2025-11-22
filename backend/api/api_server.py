"""
Meme Agent API 服务

FastAPI 服务，为 Web 前端提供 HTTP 接口
"""

import os
import sys
from typing import Optional

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

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

# 使用新的导入路径
from backend.agent.agent_core import MemeAgent
from backend.agent.real_tools import real_search_meme, real_generate_meme
from backend.agent.session_manager import SessionManager


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

# 1. 数据集图片（搜索引擎的结果）
MEME_IMAGE_DIR = os.path.join(project_root, 'data', 'dataset', 'meme')
if not os.path.exists(MEME_IMAGE_DIR):
    # 兼容旧路径
    MEME_IMAGE_DIR = os.path.join(project_root, 'dataset', 'meme')

if os.path.exists(MEME_IMAGE_DIR):
    app.mount("/static", StaticFiles(directory=MEME_IMAGE_DIR), name="static")
    logger.info(f"✅ 静态文件服务已配置: {MEME_IMAGE_DIR} -> /static/")
else:
    logger.warning(f"⚠️  图片目录不存在: {MEME_IMAGE_DIR}")

# 2. 生成的图片（生成器的结果）
GENERATED_IMAGE_DIR = os.path.join(project_root, 'backend', 'generator', 'outputs')
if not os.path.exists(GENERATED_IMAGE_DIR):
    # 兼容旧路径
    old_generated_dir = os.path.join(project_root, 'member_c_generate', 'outputs')
    if os.path.exists(old_generated_dir):
        GENERATED_IMAGE_DIR = old_generated_dir
    else:
        os.makedirs(GENERATED_IMAGE_DIR, exist_ok=True)

if os.path.exists(GENERATED_IMAGE_DIR):
    app.mount("/generated", StaticFiles(directory=GENERATED_IMAGE_DIR), name="generated")
    logger.info(f"✅ 生成图片服务已配置: {GENERATED_IMAGE_DIR} -> /generated/")
else:
    logger.warning(f"⚠️  生成图片目录不存在: {GENERATED_IMAGE_DIR}")


# ============ 辅助函数 ============

def generate_explanation(keywords: list, source: str) -> str:
    """
    生成友好的推荐理由
    
    Args:
        keywords: 情绪关键词列表
        source: 来源 ("search" 或 "generated")
        
    Returns:
        推荐理由文本
    """
    keywords_text = "、".join(keywords)
    
    if source == "search":
        templates = [
            f"找到了一张很适合表达'{keywords_text}'的梗图！希望你喜欢~",
            f"这张图正好能表达你的'{keywords_text}'心情，用起来吧！",
            f"看到'{keywords_text}'就想到这张图，分享给你啦！"
        ]
    else:  # generated
        templates = [
            f"没找到合适的图，专门为你生成了一张'{keywords_text}'主题的梗图！",
            f"为'{keywords_text}'这个心情特制了一张梗图，希望能让你会心一笑~",
            f"给你定制了一张'{keywords_text}'主题的图，拿去用吧！"
        ]
    
    # 简单轮换
    import random
    return random.choice(templates)

def convert_meme_path_to_url(meme_path: str, source: str = None) -> str:
    """
    将文件系统路径转换为前端可访问的URL路径
    
    Args:
        meme_path: 文件系统路径
        source: 来源 ("search" 或 "generated")
        
    Returns:
        前端可访问的URL路径
    """
    if not meme_path:
        return meme_path
    
    # 规范化路径分隔符
    meme_path = meme_path.replace('\\', '/')
    
    # 根据来源转换路径
    if source == "generated" or "member_c_generate" in meme_path:
        # 生成的图片：member_c_generate/outputs/xxx.png -> /generated/xxx.png
        if "outputs/" in meme_path:
            filename = meme_path.split("outputs/")[-1]
            return f"/generated/{filename}"
        elif "member_c_generate/" in meme_path:
            filename = meme_path.split("member_c_generate/")[-1]
            if filename.startswith("outputs/"):
                filename = filename[8:]  # 去掉 "outputs/"
            return f"/generated/{filename}"
    
    # 搜索的图片：dataset/meme/xxx.jpg -> /static/xxx.jpg
    if "dataset/meme/" in meme_path:
        filename = meme_path.split("dataset/meme/")[-1]
        return f"/static/{filename}"
    elif meme_path.startswith("meme/"):
        filename = meme_path[5:]  # 去掉 "meme/"
        return f"/static/{filename}"
    
    # 兜底：如果只是文件名，根据来源推断
    if "/" not in meme_path:
        if source == "generated":
            return f"/generated/{meme_path}"
        else:
            return f"/static/{meme_path}"
    
    # 其他情况：保持原样
    return meme_path


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
    
    # 创建 Agent（使用LLaMA 3.3 70B - 情绪提取专用）
    from backend.agent.config import AgentConfig
    
    agent_config = AgentConfig(
        api_key=os.getenv("SAMBANOVA_API_KEY") or "9a2266c7-a96a-4459-be90-af5dfc58a655",
        model="Meta-Llama-3.3-70B-Instruct",  # 3.3版本，中文理解更好
        temperature=0.1
    )
    agent = MemeAgent(config=agent_config, session_manager=session_manager)
    
    # 注意：新架构中不再注册工具，Server直接调用real_tools
    
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
    查询梗图接口（非流式）- 新架构：Server控制流程
    
    流程：
    1. LLM提取情绪关键词
    2. Server调用search_meme
    3. Server判断结果，决定是否调用generate_meme
    4. Server生成explanation并返回
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent 服务未就绪")
    
    try:
        logger.info(f"📥 [新架构] 收到查询请求: {request.text[:50]}...")
        
        # 步骤1: LLM提取情绪关键词
        logger.info("🔍 步骤1: 提取情绪关键词")
        keywords = agent.extract_emotion_keywords(request.text)
        if not keywords:
            raise HTTPException(status_code=400, detail="无法识别情绪关键词")
        
        logger.info(f"✅ 提取关键词: {keywords}")
        
        # 步骤2: 调用search_meme搜索（融合原始query和情绪关键词）
        # 融合策略：原始query包含更完整的语义，情绪关键词提供核心焦点
        search_query = f"{request.text} {keywords[0]}" if len(request.text) > len(keywords[0]) * 2 else keywords[0]
        logger.info(f"🔍 步骤2: 搜索梗图")
        logger.debug(f"   原始输入: '{request.text}'")
        logger.debug(f"   情绪关键词: '{keywords[0]}'")
        logger.debug(f"   融合查询: '{search_query}'")
        search_result = real_search_meme(query=search_query, top_k=5, min_score=0.0)
        
        meme_path = None
        source = None
        score = 0.0
        
        # 步骤3: 判断搜索结果
        if search_result.get("success") and search_result.get("data", {}).get("results"):
            top_result = search_result["data"]["results"][0]
            score = top_result["score"]
            logger.info(f"📊 搜索结果: score={score:.4f}")
            
            SCORE_THRESHOLD = 0.8  # 匹配度阈值
            if score > SCORE_THRESHOLD:
                # 搜索成功
                meme_path = top_result["image_path"]
                source = "search"
                logger.info(f"✅ 搜索成功，使用搜索结果")
            else:
                logger.info(f"⚠️  搜索分数不足 ({score:.4f} < {SCORE_THRESHOLD})，调用生成工具")
                # 调用generate_meme
                gen_result = real_generate_meme(text=keywords[0], template="wojak")
                if gen_result.get("success"):
                    meme_path = gen_result["data"]["image_path"]
                    source = "generated"
                    logger.info(f"✅ 生成成功: {meme_path}")
                else:
                    raise HTTPException(status_code=500, detail=gen_result.get("error", "生成失败"))
        else:
            # 搜索失败，直接生成
            logger.info(f"⚠️  搜索失败，调用生成工具")
            gen_result = real_generate_meme(text=keywords[0], template="wojak")
            if gen_result.get("success"):
                meme_path = gen_result["data"]["image_path"]
                source = "generated"
                logger.info(f"✅ 生成成功: {meme_path}")
            else:
                raise HTTPException(status_code=500, detail=gen_result.get("error", "生成失败"))
        
        # 步骤4: 生成explanation
        explanation = generate_explanation(keywords, source)
        
        # 转换路径
        url_path = convert_meme_path_to_url(meme_path, source)
        
        logger.info(f"✅ [新架构] 查询成功: {meme_path} -> {url_path}")
        
        return QueryResponse(
            success=True,
            meme_path=url_path,
            explanation=explanation,
            source=source,
            session_id=request.session_id or "no_session"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 请求处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query/stream")
async def query_meme_stream(request: QueryRequest):
    """
    流式查询梗图接口 - 新架构：Server控制流程
    
    实时返回处理步骤
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent 服务未就绪")
    
    async def generate_events() -> AsyncGenerator[str, None]:
        """生成SSE事件流"""
        try:
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'data': {'query': request.text}}, ensure_ascii=False)}\n\n"
            
            logger.info(f"📥 [流式] 收到查询请求: {request.text[:50]}...")
            
            # 步骤1: 提取情绪关键词
            yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 1, 'tool': 'extract_emotion', 'status': 'running'}}, ensure_ascii=False)}\n\n"
            
            keywords = await asyncio.to_thread(agent.extract_emotion_keywords, request.text)
            if not keywords:
                error_data = {'type': 'error', 'data': {'error': '无法识别情绪关键词'}}
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                return
            
            yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 1, 'tool': 'extract_emotion', 'result': {'keywords': keywords}, 'status': 'success'}}, ensure_ascii=False)}\n\n"
            
            # 步骤2: 搜索梗图（融合原始query和情绪关键词）
            search_query = f"{request.text} {keywords[0]}" if len(request.text) > len(keywords[0]) * 2 else keywords[0]
            logger.debug(f"🔍 [流式] 融合查询: 原始='{request.text}', 关键词='{keywords[0]}', 融合='{search_query}'")
            
            yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 2, 'tool': 'search_meme', 'arguments': {'query': search_query}, 'status': 'running'}}, ensure_ascii=False)}\n\n"
            
            search_result = await asyncio.to_thread(real_search_meme, query=search_query, top_k=3, min_score=0.0)
            
            meme_paths = []  # 改为列表存储多张图片
            source = None
            score = 0.0
            
            # 步骤3: 判断搜索结果
            if search_result.get("success") and search_result.get("data", {}).get("results"):
                results = search_result["data"]["results"]
                top_result = results[0]
                score = top_result["score"]
                
                SCORE_THRESHOLD = 0.8  # 匹配度阈值
                if score >= SCORE_THRESHOLD:
                    # 搜索成功 - 返回 top3
                    meme_paths = [result["image_path"] for result in results[:3]]
                    source = "search"
                    yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 2, 'tool': 'search_meme', 'arguments': {'query': search_query}, 'result': {'score': score, 'found': True, 'count': len(meme_paths)}, 'status': 'success'}}, ensure_ascii=False)}\n\n"
                else:
                    # 搜索分数不足，生成梗图
                    yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 2, 'tool': 'search_meme', 'arguments': {'query': search_query}, 'result': {'score': score, 'found': False}, 'status': 'low_score'}}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 3, 'tool': 'generate_meme', 'arguments': {'text': keywords[0], 'template': 'wojak'}, 'status': 'running'}}, ensure_ascii=False)}\n\n"
                    
                    gen_result = await asyncio.to_thread(real_generate_meme, text=keywords[0], template="wojak")
                    if gen_result.get("success"):
                        meme_paths = [gen_result["data"]["image_path"]]  # 生成的只有一张
                        source = "generated"
                        yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 3, 'tool': 'generate_meme', 'arguments': {'text': keywords[0], 'template': 'wojak'}, 'result': {'path': meme_paths[0]}, 'status': 'success'}}, ensure_ascii=False)}\n\n"
                    else:
                        error_data = {'type': 'error', 'data': {'error': gen_result.get("error", "生成失败")}}
                        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                        return
            else:
                # 搜索失败，直接生成
                yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 2, 'tool': 'search_meme', 'arguments': {'query': search_query}, 'result': {'found': False}, 'status': 'failed'}}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 3, 'tool': 'generate_meme', 'arguments': {'text': keywords[0], 'template': 'wojak'}, 'status': 'running'}}, ensure_ascii=False)}\n\n"
                
                gen_result = await asyncio.to_thread(real_generate_meme, text=keywords[0], template="wojak")
                if gen_result.get("success"):
                    meme_paths = [gen_result["data"]["image_path"]]  # 生成的只有一张
                    source = "generated"
                    yield f"data: {json.dumps({'type': 'tool_call', 'data': {'step': 3, 'tool': 'generate_meme', 'arguments': {'text': keywords[0], 'template': 'wojak'}, 'result': {'path': meme_paths[0]}, 'status': 'success'}}, ensure_ascii=False)}\n\n"
                else:
                    error_data = {'type': 'error', 'data': {'error': gen_result.get("error", "生成失败")}}
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                    return
            
            # 生成explanation
            explanation = generate_explanation(keywords, source)
            
            # 转换路径（支持多张图片）
            url_paths = [convert_meme_path_to_url(path, source) for path in meme_paths]
            
            # 发送最终结果
            final_data = {
                'type': 'complete',
                'data': {
                    'success': True,
                    'meme_paths': url_paths,  # 改为复数，支持多张图片
                    'explanation': explanation,
                    'source': source,
                    'count': len(url_paths),
                    'session_id': request.session_id or "no_session"
                }
            }
            yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
            logger.info(f"✅ [流式] 查询成功: 返回 {len(url_paths)} 张图片")
            
        except Exception as e:
            logger.error(f"❌ [流式] 查询失败: {e}", exc_info=True)
            error_data = {'type': 'error', 'data': {'error': str(e)}}
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

