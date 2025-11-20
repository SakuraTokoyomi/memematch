"""
Meme Agent 核心模块
基于 SambaNova + OpenAI Function Calling 实现

负责：
1. LLM Agent 推理循环（ReAct）
2. 工具调用调度
3. 查询改写（refine_query）
4. 情绪分类（classify_sentiment）
5. 推荐理由生成
"""

import json
import logging
import os
import sys
from typing import List, Dict, Any, Optional, Callable
from openai import OpenAI

# 处理导入路径（支持直接运行和作为模块导入）
try:
    from .config import AgentConfig
except ImportError:
    # 如果相对导入失败，添加路径并使用绝对导入
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(backend_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from backend.agent.config import AgentConfig


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemeAgent:
    """
    Meme Agent 核心类
    
    使用 SambaNova Cloud + Function Calling 实现智能 meme 推荐
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, session_manager=None):
        """
        初始化 Agent
        
        Args:
            config: Agent 配置，如果为 None 则从环境变量加载
            session_manager: 会话管理器实例（可选）
        """
        self.config = config or AgentConfig.from_env()
        
        # 初始化 OpenAI 客户端（连接到 SambaNova）
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
        
        # 工具函数注册表
        self.tool_functions: Dict[str, Callable] = {}
        
        # 定义工具 schema
        self.tools = self._define_tools()
        
        # 会话管理器（可选）
        self.session_manager = session_manager
        
        logger.info(f"Agent 初始化完成，使用模型: {self.config.model}")
    
    def register_tool(self, name: str, func: Callable):
        """
        注册外部工具函数
        
        Args:
            name: 工具名称（必须与 tools schema 中的 name 一致）
            func: 工具函数
        """
        self.tool_functions[name] = func
        logger.info(f"工具已注册: {name}")
    
    def _define_tools(self) -> List[Dict]:
        """
        定义所有可用工具的 Function Calling schema
        
        Returns:
            工具定义列表
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_meme",
                    "description": "检索梗图。用情绪词搜索现成的图片，返回最相似的结果。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "情绪关键词，如：开心、累、无语、压力"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "返回结果数量",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_meme",
                    "description": "生成梗图。当搜索结果不佳时（分数<0.6），用情绪词生成新图片。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "显示的文字，简短的情绪词"
                            },
                            "template": {
                                "type": "string",
                                "description": "图片模板",
                                "enum": ["drake", "doge", "wojak", "distracted_boyfriend", "two_buttons"],
                                "default": "wojak"
                            }
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
    
    def extract_emotion_keywords(self, user_query: str) -> List[str]:
        """
        提取用户输入中的情绪关键词（简化版：LLM只负责情绪识别）
        
        Args:
            user_query: 用户输入
            
        Returns:
            情绪关键词列表（最多3个）
        """
        logger.info(f"🔍 提取情绪关键词: {user_query}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,  # 低温度保证稳定性
                max_tokens=50  # 只需要简短的关键词
            )
            
            keywords_text = response.choices[0].message.content.strip()
            logger.info(f"✅ LLM提取结果: '{keywords_text}'")
            
            # 解析关键词（支持逗号、顿号分隔）
            keywords = [kw.strip() for kw in keywords_text.replace('、', ',').split(',') if kw.strip()]
            keywords = keywords[:3]  # 最多3个
            
            logger.info(f"📋 解析后的关键词: {keywords}")
            return keywords
            
        except Exception as e:
            logger.error(f"❌ 情绪提取失败: {e}")
            # 降级：直接使用用户输入作为关键词
            return [user_query[:10]]
    
    def _get_system_prompt(self) -> str:
        """
        获取系统 prompt
        
        Returns:
            系统提示词
        """
        return """你是情绪识别专家。你的唯一任务是：从用户输入中提取核心情绪关键词。

## 规则

1. 只提取情绪或状态词（开心、累、压力、无奈等）
2. 忽略动作词（想、要、分享、表达、希望等）
3. 忽略对象词（老板、项目、考试等）
4. 最多提取3个关键词，用逗号分隔
5. 只输出关键词，不要有任何其他内容

## 示例

用户："今天好开心"
你的输出："开心"

用户："累死了"
你的输出："累"

用户："我服了"
你的输出："服了"

用户："无语"
你的输出："无语"

用户："又咋了"
你的输出："疑问"

用户："我今天工作很顺利，老板还夸奖了我，想分享这份喜悦"
你的输出："喜悦"

用户："项目延期了，压力好大"
你的输出："压力"

用户："考试考砸了"
你的输出："沮丧"

用户："既开心又紧张"
你的输出："开心,紧张"

用户："累得要死，还有点烦"
你的输出："累,烦"

开始工作！只输出情绪关键词，不要有任何解释！"""

    def process_query(
        self, 
        user_query: str, 
        max_iterations: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理用户查询的主函数（Agent 推理循环）
        
        Args:
            user_query: 用户输入的查询文本
            max_iterations: 最大迭代次数，默认使用配置中的值
            session_id: 会话 ID（可选），用于多轮对话
            
        Returns:
            {
                "meme_path": "路径/到/meme.png",
                "explanation": "推荐理由",
                "candidates": [前 k 个候选结果],
                "reasoning_steps": [Agent 推理步骤],
                "status": "success|error",
                "source": "search|generated",
                "session_id": "会话ID"
            }
        """
        max_iterations = max_iterations or self.config.max_iterations
        
        # 初始化对话历史
        if session_id and self.session_manager:
            # 使用会话管理器获取历史
            messages = self.session_manager.get_messages(session_id, self._get_system_prompt())
            messages.append({"role": "user", "content": user_query})
            logger.info(f"使用会话 {session_id}，历史消息数: {len(messages)}")
        else:
            # 无会话：单次查询模式
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": user_query}
            ]
            if session_id:
                logger.warning(f"会话 ID {session_id} 已提供，但未启用会话管理器")
        
        reasoning_steps = []
        final_result = {}
        
        logger.info(f"🚀 ========== 开始处理查询 ==========")
        logger.info(f"📝 用户输入: {user_query}")
        logger.info(f"🔄 最大迭代次数: {max_iterations}")
        logger.info(f"💬 会话ID: {session_id or 'None (单次查询)'}")
        logger.debug(f"📨 初始消息数: {len(messages)}")
        
        # 检查是否是新会话（只有system prompt + 用户消息）
        is_new_session = len(messages) <= 2
        
        try:
            for iteration in range(max_iterations):
                logger.info(f"{'='*50}")
                logger.info(f"🔄 迭代 {iteration + 1}/{max_iterations}")
                logger.info(f"{'='*50}")
                
                # 调用 LLM（带 Function Calling）
                logger.debug(f"🤖 迭代 {iteration + 1}/{max_iterations}: 调用LLM...")
                
                # 🚨 第一次迭代：检查是否需要强制工具调用
                greetings = ["你好", "hi", "hello", "在吗", "在不在", "hey"]
                is_greeting = any(greet in user_query.lower() for greet in greetings)
                
                # 强制策略：每次用户输入（第一次迭代）都必须调用工具，除非是问候语
                if iteration == 0 and not is_greeting:
                    tool_choice = "required"  # 强制必须调用工具
                    logger.debug("🔒 用户输入（非问候语），强制要求调用工具")
                else:
                    tool_choice = "auto"
                    if iteration == 0 and is_greeting:
                        logger.debug("👋 识别为问候语，允许直接回复")
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=messages,
                        tools=self.tools,
                        tool_choice=tool_choice,
                        temperature=self.config.temperature
                    )
                    logger.debug(f"✅ LLM响应成功: reponse {response}")
                except Exception as api_error:
                    logger.error(f"API 调用失败 (迭代 {iteration + 1}): {api_error}")
                    
                    # 如果已经有结果，直接返回
                    if "meme_path" in final_result:
                        logger.info("API 失败，但已有结果，提前返回")
                        final_result["explanation"] = final_result.get("explanation", "已为你找到合适的梗图")
                        final_result["reasoning_steps"] = reasoning_steps
                        final_result["status"] = "success"
                        return final_result
                    
                    # 如果是 500 错误且已经尝试多次，返回错误
                    if "500" in str(api_error) or "Internal" in str(api_error):
                        return {
                            "error": f"API 服务暂时不可用，请稍后重试: {str(api_error)}",
                            "reasoning_steps": reasoning_steps,
                            "status": "error"
                        }
                    
                    # 其他错误继续抛出
                    raise
                
                message = response.choices[0].message
                
                # 如果没有工具调用，说明 Agent 认为任务完成
                if not message.tool_calls:
                    logger.info("✅ Agent完成推理，无更多工具调用")
                    logger.debug(f"💬 最终回复: {message.content[:100]}...")
                    final_result.update({
                        "explanation": message.content,
                        "reasoning_steps": reasoning_steps,
                        "status": "success"
                    })
                    
                    # 如果之前没有获取到 meme，说明出错了（但问候语除外）
                    if "meme_path" not in final_result and not is_greeting:
                        final_result["error"] = "未能获取 meme"
                        final_result["status"] = "error"
                    
                    break
                
                # 将 assistant 的消息添加到历史（包含 tool_calls）
                messages.append(message)
                
                # 执行所有工具调用
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"工具参数解析失败: {e}")
                        tool_args = {}
                    
                    logger.info(f"🔧 调用工具: {tool_name}")
                    logger.debug(f"📋 工具参数: {json.dumps(tool_args, ensure_ascii=False, indent=2)}")
                    
                    # 执行工具
                    try:
                        logger.debug(f"⚙️  开始执行工具: {tool_name}")
                        result = self._execute_tool(tool_name, tool_args)
                        result_str = json.dumps(result, ensure_ascii=False)
                        
                        # 打印工具返回结果的关键信息
                        if isinstance(result, dict):
                            if result.get("success"):
                                logger.info(f"✅ 工具执行成功: {tool_name}")
                                if tool_name == "search_meme" and result.get("data"):
                                    data = result["data"]
                                    logger.info(f"🔍 搜索结果: 找到 {data.get('total', 0)} 个结果")
                                    if data.get("results"):
                                        top_result = data["results"][0]
                                        logger.debug(f"   Top-1: {top_result.get('image_path')} (score: {top_result.get('score', 0):.4f})")
                            else:
                                logger.warning(f"⚠️  工具返回失败: {tool_name}")
                                logger.debug(f"   错误: {result.get('error', 'Unknown')}")
                        
                        logger.debug(f"📦 完整返回: {result_str[:300]}...")
                        
                    except Exception as e:
                        logger.error(f"工具执行失败: {e}")
                        result = {"error": str(e)}
                        result_str = json.dumps(result, ensure_ascii=False)
                    
                    # 记录推理步骤
                    reasoning_steps.append({
                        "step": len(reasoning_steps) + 1,
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": result
                    })
                    
                    # 保存检索结果（v2 格式）
                    if tool_name == "search_meme":
                        if result.get("success") and result.get("data"):
                            data = result["data"]
                            results = data.get("results", [])
                            if results:
                                meme_path = results[0].get("image_path")
                                score = results[0].get("score", 0)
                                final_result.update({
                                    "meme_path": meme_path,
                                    "candidates": results,
                                    "source": "search",
                                    "search_score": score
                                })
                                logger.info(f"💾 保存搜索结果: {meme_path}")
                                logger.debug(f"   分数: {score:.4f}, 候选数: {len(results)}")
                    
                    # 保存生成结果（v2 格式）
                    if tool_name == "generate_meme":
                        if result.get("success") and result.get("data"):
                            data = result["data"]
                            meme_path = data.get("image_path")
                            final_result.update({
                                "meme_path": meme_path,
                                "candidates": [],
                                "source": "generated"
                            })
                            logger.info(f"💾 保存生成结果: {meme_path}")
                    
                    # 添加工具返回结果到对话历史
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str
                    })
                
                # 如果已经获取到 meme 且质量足够好，可以提前结束
                if "meme_path" in final_result:
                    if final_result.get("source") == "generated":
                        # 生成的直接可用，强制结束避免重复调用
                        logger.info("已生成 meme，强制结束推理")
                        # 添加一个特殊的消息告诉 Agent 任务完成
                        messages.append({
                            "role": "user",
                            "content": "✅ 很好！你已经生成了梗图。现在请用1-2句话，用轻松、友好的语气给出推荐理由，然后结束任务。不要再调用任何工具。"
                        })
                    elif final_result.get("search_score", 0) >= self.config.search_score_threshold:
                        # 检索结果质量好，强制结束
                        logger.info(f"检索结果质量足够（score={final_result.get('search_score'):.4f} >= {self.config.search_score_threshold}），强制结束推理")
                        # 添加强制结束消息
                        messages.append({
                            "role": "user",
                            "content": f"✅ 很好！你已经找到了非常合适的梗图。现在请用1-2句话，用轻松、友好、共情的语气给出推荐理由（不要提及分数、匹配度等技术信息），然后结束任务。不要再调用任何工具。"
                        })
            
            # 达到最大迭代次数
            if iteration == max_iterations - 1:
                logger.warning("达到最大迭代次数")
                if "meme_path" not in final_result:
                    final_result.update({
                        "error": "达到最大迭代次数但未获取到 meme",
                        "status": "error"
                    })
        
        except Exception as e:
            logger.error(f"Agent 执行出错: {e}", exc_info=True)
            return {
                "error": str(e),
                "reasoning_steps": reasoning_steps,
                "status": "error"
            }
        
        # 确保有解释
        if "explanation" not in final_result and "meme_path" in final_result:
            final_result["explanation"] = self._generate_explanation(
                user_query, 
                final_result
            )
        
        final_result["reasoning_steps"] = reasoning_steps
        
        # 如果使用会话管理，更新会话历史
        if session_id and self.session_manager:
            # 保存最终的 messages（包含本次完整对话）
            self.session_manager.update_messages(session_id, messages)
            final_result["session_id"] = session_id
            logger.debug(f"💬 会话已保存: {session_id}")
        
        # 打印最终结果摘要
        logger.info(f"🎉 ========== 查询处理完成 ==========")
        logger.info(f"📊 状态: {final_result.get('status', 'unknown')}")
        if final_result.get("meme_path"):
            logger.info(f"🖼️  Meme路径: {final_result['meme_path']}")
            logger.info(f"📍 来源: {final_result.get('source', 'unknown')}")
        if final_result.get("error"):
            logger.warning(f"❌ 错误: {final_result['error']}")
        logger.info(f"🔄 推理步骤数: {len(reasoning_steps)}")
        logger.debug(f"📦 完整结果: {json.dumps(final_result, ensure_ascii=False, indent=2)}")
        
        return final_result
    
    def _execute_tool(self, tool_name: str, args: Dict) -> Dict:
        """
        执行工具函数
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            
        Returns:
            工具执行结果
        """
        # 内部工具：由 Agent 自己实现
        if tool_name == "refine_query":
            return self._refine_query_internal(args["user_query"])
        
        elif tool_name == "classify_sentiment":
            return self._classify_sentiment_internal(args["text"])
        
        # 外部工具：由其他成员提供
        elif tool_name in self.tool_functions:
            return self.tool_functions[tool_name](**args)
        
        else:
            logger.error(f"工具未注册: {tool_name}")
            return {"error": f"工具 {tool_name} 未注册。请确保已调用 register_tool() 注册该工具。"}
    
    def _refine_query_internal(self, user_query: str) -> Dict:
        """
        内部实现：查询改写
        
        将中文口语化输入改写成适合检索的英文关键词
        
        Args:
            user_query: 用户原始输入
            
        Returns:
            {"original": "...", "refined": "..."}
        """
        prompt = f"""将以下中文表达改写成适合搜索 meme 的英文关键词。

要求：
1. 提取核心情绪或场景
2. 使用简洁的英文词组（2-5 个单词）
3. 考虑常见 meme 的表达方式
4. 可以加上 "meme", "reaction" 等词

示例：
- "我无语了" → "speechless reaction meme"
- "太离谱了" → "surprised shocked face"
- "我太难了" → "tired exhausted struggle"

用户输入：{user_query}

只返回英文关键词，不要解释，不要加引号："""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            refined = response.choices[0].message.content.strip()
            logger.info(f"查询改写: '{user_query}' → '{refined}'")
            
            return {
                "original": user_query,
                "refined": refined
            }
        
        except Exception as e:
            logger.error(f"查询改写失败: {e}")
            return {
                "original": user_query,
                "refined": user_query,  # 失败时返回原查询
                "error": str(e)
            }
    
    def _classify_sentiment_internal(self, text: str) -> Dict:
        """
        内部实现：情绪分类
        
        分析文本的情绪类型和强度
        
        Args:
            text: 需要分析的文本
            
        Returns:
            {"emotion": "...", "intensity": 0.0-1.0, "description": "..."}
        """
        prompt = f"""分析以下文本的情绪，从这些类别中选择最合适的一个：

        情绪类别：
        - happy（开心、愉快）
        - sad（悲伤、失落）
        - angry（生气、愤怒）
        - surprised（惊讶、震惊）
        - disgusted（厌恶、反感）
        - fearful（恐惧、害怕）
        - tired（疲惫、累）
        - confused（困惑、迷茫）
        - excited（兴奋、激动）
        - neutral（中性、平淡）

        文本：{text}

        返回 JSON 格式（不要 markdown 代码块）：
        {{"emotion": "情绪类别", "intensity": 0.8, "description": "简短描述"}}

        intensity 是 0.0-1.0 的浮点数，表示情绪强度。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # 尝试解析 JSON
            try:
                # 移除可能的 markdown 代码块标记
                content = content.replace("```json", "").replace("```", "").strip()
                result = json.loads(content)
            except json.JSONDecodeError:
                # 如果解析失败，返回默认值
                result = {
                    "emotion": "neutral",
                    "intensity": 0.5,
                    "description": "无法准确识别情绪"
                }
            
            logger.info(f"情绪分类: {result}")
            return result
        
        except Exception as e:
            logger.error(f"情绪分类失败: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.5,
                "description": "分析失败",
                "error": str(e)
            }
    
    def _generate_explanation(self, user_query: str, result: Dict) -> str:
        """
        生成推荐理由
        
        Args:
            user_query: 用户原始输入
            result: Agent 返回的结果
            
        Returns:
            推荐理由文本
        """
        source = result.get("source", "unknown")
        meme_path = result.get("meme_path", "")
        
        if source == "generated":
            context = f"我们为你生成了一张新的梗图"
        else:
            score = result.get("search_score", 0)
            context = f"我们找到了一张梗图（匹配度 {score:.2f}）"
        
        prompt = f"""用户说："{user_query}"

{context}：{meme_path}

请用 1-2 句话自然、口语化地解释为什么推荐这个梗图。

要求：
1. 自然、轻松、口语化
2. 体现对用户情绪的理解
3. 不要太正式或生硬
4. 不要说"我推荐"、"我认为"等，直接说明这个梗图的特点

例如：
- "这张图完美表达了那种累到不想动的感觉，就是你现在的状态吧~"
- "这个表情简直就是'我无语了'的最佳诠释哈哈哈"

解释："""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            
            explanation = response.choices[0].message.content.strip()
            logger.info(f"生成推荐理由: {explanation}")
            return explanation
        
        except Exception as e:
            logger.error(f"生成推荐理由失败: {e}")
            return "这张梗图应该很适合你现在的心情~"


def create_agent(
    api_key: Optional[str] = None,
    model: str = "Meta-Llama-3.1-8B-Instruct",
    **kwargs
) -> MemeAgent:
    """
    便捷函数：创建 Agent 实例
    
    Args:
        api_key: SambaNova API key，如果为 None 则从环境变量读取
        model: 模型名称
        **kwargs: 其他配置参数
        
    Returns:
        MemeAgent 实例
    """
    config = AgentConfig(
        api_key=api_key or "",
        model=model,
        **kwargs
    )
    
    if not config.api_key:
        config = AgentConfig.from_env()
    
    return MemeAgent(config)

