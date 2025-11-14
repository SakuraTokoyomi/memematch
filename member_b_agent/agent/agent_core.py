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
from typing import List, Dict, Any, Optional, Callable
from openai import OpenAI

from .config import AgentConfig


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemeAgent:
    """
    Meme Agent 核心类
    
    使用 SambaNova Cloud + Function Calling 实现智能 meme 推荐
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        初始化 Agent
        
        Args:
            config: Agent 配置，如果为 None 则从环境变量加载
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
                    "description": "从数据库检索相关的 meme 图片。当用户想要找现成的梗图时使用。返回按相似度排序的 top-k 结果。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "检索关键词，应该是描述 meme 情绪、场景或内容的英文词组，例如 'tired reaction meme' 或 'surprised cat'"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "返回结果数量，默认 5",
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
                    "name": "refine_query",
                    "description": "将用户的中文口语化输入改写成适合检索的英文关键词。当用户输入模糊、口语化或不够具体时使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_query": {
                                "type": "string",
                                "description": "用户的原始输入文本"
                            }
                        },
                        "required": ["user_query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "classify_sentiment",
                    "description": "分析用户输入的情绪类型和强度。用于理解用户想表达的情感，帮助选择合适的 meme。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "需要分析情绪的文本"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_meme",
                    "description": "生成新的 meme 图片。当检索不到合适的现成梗图时使用（例如检索结果为空或相似度分数太低）。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "要在 meme 上显示的文字内容，应该简洁有力"
                            },
                            "template": {
                                "type": "string",
                                "description": "使用的模板类型",
                                "enum": ["drake", "doge", "wojak", "distracted_boyfriend", "two_buttons"]
                            }
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
    
    def _get_system_prompt(self) -> str:
        """
        获取系统 prompt
        
        Returns:
            系统提示词
        """
        return """你是一个专业的 meme（梗图）推荐助手 Meme Agent。你的任务是帮助用户找到或生成最合适的梗图来表达他们的情绪。

## 你的能力

你可以使用以下工具：
1. **search_meme**: 从数据库检索现有的梗图
2. **refine_query**: 将中文输入改写成适合检索的英文关键词
3. **classify_sentiment**: 分析用户的情绪类型
4. **generate_meme**: 生成新的梗图（当找不到合适的时）

## 工作流程建议

1. **理解用户意图**
   - 如果用户输入很模糊或是中文口语，先使用 refine_query 改写
   - 可以使用 classify_sentiment 分析情绪（可选）

2. **检索梗图**
   - 使用 search_meme 检索数据库
   - 检索关键词要用英文，例如 "tired", "surprised cat", "facepalm"
   
3. **判断结果质量**
   - 如果检索结果的 score < 0.6，说明匹配度不够好
   - 如果没有结果或质量差，考虑生成新梗图

4. **生成新梗图（fallback）**
   - 使用 generate_meme 创建新的
   - 选择合适的模板（drake, doge, wojak 等）
   - 提取用户输入中最核心的文字

5. **给出推荐理由**
   - 用 1-2 句话自然地解释为什么推荐这个梗图
   - 体现对用户情绪的理解

## 注意事项

- 始终用中文和用户交流
- 但检索关键词要用英文
- 优先检索现有梗图，检索失败时才生成
- 推荐理由要自然、口语化，不要太正式
- 不要产生幻觉，只根据工具返回的实际结果来回答

开始工作吧！"""

    def process_query(
        self, 
        user_query: str, 
        max_iterations: Optional[int] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        处理用户查询的主函数（Agent 推理循环）
        
        Args:
            user_query: 用户输入的查询文本
            max_iterations: 最大迭代次数，默认使用配置中的值
            debug: 是否输出调试信息
            
        Returns:
            {
                "meme_path": "路径/到/meme.png",
                "explanation": "推荐理由",
                "candidates": [前 k 个候选结果],
                "reasoning_steps": [Agent 推理步骤],
                "status": "success|error",
                "source": "search|generated"
            }
        """
        max_iterations = max_iterations or self.config.max_iterations
        
        # 初始化对话历史
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_query}
        ]
        
        reasoning_steps = []
        final_result = {}
        
        logger.info(f"开始处理查询: {user_query}")
        
        try:
            for iteration in range(max_iterations):
                if debug:
                    print(f"\n{'='*60}")
                    print(f"迭代 {iteration + 1}/{max_iterations}")
                    print('='*60)
                
                # 调用 LLM（带 Function Calling）
                try:
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=messages,
                        tools=self.tools,
                        tool_choice="auto",
                        temperature=self.config.temperature
                    )
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
                    logger.info("Agent 完成推理，返回最终结果")
                    final_result.update({
                        "explanation": message.content,
                        "reasoning_steps": reasoning_steps,
                        "status": "success"
                    })
                    
                    # 如果之前没有获取到 meme，说明出错了
                    if "meme_path" not in final_result:
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
                    
                    if debug:
                        print(f"\n[工具调用] {tool_name}")
                        print(f"[参数] {json.dumps(tool_args, ensure_ascii=False, indent=2)}")
                    
                    logger.info(f"调用工具: {tool_name}({tool_args})")
                    
                    # 执行工具
                    try:
                        result = self._execute_tool(tool_name, tool_args)
                        result_str = json.dumps(result, ensure_ascii=False)
                        
                        if debug:
                            print(f"[返回] {result_str[:200]}...")
                        
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
                    
                    # 保存检索结果
                    if tool_name == "search_meme" and "error" not in result:
                        results = result.get("results", [])
                        if results:
                            final_result.update({
                                "meme_path": results[0].get("image_path"),
                                "candidates": results,
                                "source": "search",
                                "search_score": results[0].get("score", 0)
                            })
                    
                    # 保存生成结果
                    if tool_name == "generate_meme" and "error" not in result:
                        final_result.update({
                            "meme_path": result.get("image_path"),
                            "candidates": [],
                            "source": "generated"
                        })
                    
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
                        logger.info("已生成 meme，准备结束")
                        # 添加一个特殊的消息告诉 Agent 任务完成
                        messages.append({
                            "role": "user",
                            "content": "任务已完成，请给出最终推荐理由并结束。"
                        })
                    elif final_result.get("search_score", 0) >= self.config.search_score_threshold:
                        # 检索结果质量好，可以结束
                        logger.info("检索结果质量足够，准备生成解释")
            
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
        
        logger.info(f"查询处理完成，状态: {final_result.get('status', 'unknown')}")
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

