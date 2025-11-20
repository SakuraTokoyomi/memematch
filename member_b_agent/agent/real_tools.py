"""
真实工具集成模块
将成员A的搜索引擎集成到Agent中
"""

import sys
import os
import logging
from typing import Dict, Any

# 配置日志
logger = logging.getLogger(__name__)

# 添加member_a_search到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
search_module_path = os.path.join(project_root, 'member_a_search')
generate_module_path = os.path.join(project_root, 'member_c_generate')

if search_module_path not in sys.path:
    sys.path.insert(0, search_module_path)
if generate_module_path not in sys.path:
    sys.path.insert(0, generate_module_path)

# 导入成员A的搜索引擎
try:
    from engine import search_meme as search_meme_real
    REAL_SEARCH_AVAILABLE = True
    print("✅ 成员A的搜索引擎已成功导入")
except ImportError as e:
    print(f"⚠️  无法导入成员A的搜索引擎: {e}")
    print(f"   搜索路径: {search_module_path}")
    REAL_SEARCH_AVAILABLE = False
    search_meme_real = None

# 导入成员C的Meme生成器
try:
    from generate_meme import generate_meme as generate_meme_real
    REAL_GENERATE_AVAILABLE = True
    print("✅ 成员C的Meme生成器已成功导入")
except ImportError as e:
    print(f"⚠️  无法导入成员C的Meme生成器: {e}")
    print(f"   生成器路径: {generate_module_path}")
    REAL_GENERATE_AVAILABLE = False
    generate_meme_real = None


def real_search_meme(query: str, top_k: int = 5, min_score: float = 0.0, **kwargs) -> Dict[str, Any]:
    """
    成员A的真实搜索引擎接口
    
    这是对成员A search_meme的包装，确保接口兼容
    
    Args:
        query: 检索关键词
        top_k: 返回结果数量
        min_score: 最小分数阈值（0-1）
        
    Returns:
        {
            "success": bool,
            "data": {
                "query": str,
                "results": [...],
                "total": int,
                "filtered": int
            },
            "metadata": {...}
        }
    """
    logger.debug(f"🔍 [real_search_meme] 收到请求: query='{query}', top_k={top_k}, min_score={min_score}")
    
    if not REAL_SEARCH_AVAILABLE:
        logger.error(f"❌ [real_search_meme] 搜索引擎不可用")
        return {
            "success": False,
            "error": "Search engine not available",
            "error_code": "ENGINE_NOT_LOADED"
        }
    
    try:
        # 调用成员A的真实搜索引擎
        logger.debug(f"⚙️  [real_search_meme] 调用成员A搜索引擎...")
        result = search_meme_real(query=query, top_k=top_k, min_score=min_score)
        
        # 打印结果摘要
        if result.get("success"):
            data = result.get("data", {})
            total = data.get("total", 0)
            logger.info(f"✅ [real_search_meme] 搜索成功: 找到 {total} 个结果")
            if data.get("results"):
                logger.debug(f"   Top-1: {data['results'][0].get('image_path')} (score: {data['results'][0].get('score', 0):.4f})")
        else:
            logger.warning(f"⚠️  [real_search_meme] 搜索返回失败: {result.get('error')}")
        
        logger.debug(f"📦 [real_search_meme] 返回结果: {str(result)[:200]}...")
        
        # 成员A已经返回正确的格式，直接返回
        return result
        
    except Exception as e:
        # 捕获任何异常并返回标准错误格式
        logger.error(f"❌ [real_search_meme] 异常: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_code": "REAL_SEARCH_ERROR"
        }


def real_generate_meme(text: str, template: str = "drake", options: Dict = None, **kwargs) -> Dict[str, Any]:
    """
    成员C的真实Meme生成接口
    
    Args:
        text: 要显示在 meme 上的文字
        template: 模板类型 (drake/doge/wojak)
        options: 生成选项（字体、颜色等）
        
    Returns:
        {
            "success": bool,
            "data": {
                "image_path": str,  # 相对路径
                "template": str,
                "text": str,
                ...
            },
            "metadata": {...}
        }
    """
    logger.debug(f"🎨 [real_generate_meme] 收到请求: text='{text}', template='{template}'")
    
    if not REAL_GENERATE_AVAILABLE:
        logger.error(f"❌ [real_generate_meme] 生成器不可用")
        return {
            "success": False,
            "error": "Meme generator not available",
            "error_code": "GENERATOR_NOT_LOADED"
        }
    
    try:
        # 保存当前工作目录
        original_cwd = os.getcwd()
        
        # 切换到member_c_generate目录（因为生成器依赖相对路径）
        os.chdir(generate_module_path)
        
        try:
            # 调用成员C的真实生成器
            logger.debug(f"⚙️  [real_generate_meme] 调用成员C生成器...")
            result = generate_meme_real(text=text, template=template, options=options)
            
            # 成功时，转换路径为相对于项目根目录的路径
            if result.get("success"):
                # 生成的图片路径是相对于member_c_generate的
                # 例如: outputs/generated_drake_xxx.png
                relative_path = result["data"]["image_path"]
                
                # 转换为相对于项目根目录的路径
                # member_c_generate/outputs/generated_drake_xxx.png
                project_relative_path = os.path.join("member_c_generate", relative_path)
                result["data"]["image_path"] = project_relative_path
                
                logger.info(f"✅ [real_generate_meme] 生成成功: {project_relative_path}")
                logger.debug(f"   模板: {template}, 耗时: {result['metadata']['generation_time']}s")
            else:
                logger.warning(f"⚠️  [real_generate_meme] 生成返回失败: {result.get('error')}")
            
            logger.debug(f"📦 [real_generate_meme] 返回结果: {str(result)[:200]}...")
            
            return result
            
        finally:
            # 恢复原始工作目录
            os.chdir(original_cwd)
        
    except Exception as e:
        logger.error(f"❌ [real_generate_meme] 异常: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_code": "REAL_GENERATE_ERROR"
        }


def setup_real_tools(agent):
    """
    为Agent注册真实的工具函数
    
    Args:
        agent: MemeAgent实例
    """
    # 注册搜索工具（成员A）
    if REAL_SEARCH_AVAILABLE:
        agent.register_tool("search_meme", real_search_meme)
        print("✅ 真实搜索工具已注册（成员A）")
    else:
        print("⚠️  搜索引擎不可用，将使用mock版本")
        from .tools import mock_search_meme
        agent.register_tool("search_meme", mock_search_meme)
        print("✅ Mock搜索工具已注册（降级模式）")
    
    # 注册生成工具（成员C）
    if REAL_GENERATE_AVAILABLE:
        agent.register_tool("generate_meme", real_generate_meme)
        print("✅ 真实生成工具已注册（成员C）")
    else:
        print("⚠️  Meme生成器不可用，将使用mock版本")
        from .tools import mock_generate_meme
        agent.register_tool("generate_meme", mock_generate_meme)
        print("✅ Mock生成工具已注册（降级模式）")


def test_real_search():
    """
    测试真实搜索引擎是否工作正常
    
    Returns:
        bool: 是否测试通过
    """
    if not REAL_SEARCH_AVAILABLE:
        print("❌ 搜索引擎未加载")
        return False
    
    print("\n🧪 测试真实搜索引擎...")
    
    # 测试查询
    test_query = "happy"
    print(f"   查询: {test_query}")
    
    try:
        result = real_search_meme(query=test_query, top_k=3)
        
        if result.get("success"):
            data = result["data"]
            print(f"   ✅ 搜索成功")
            print(f"   - 返回结果: {data['total']} 个")
            print(f"   - 搜索耗时: {result['metadata']['search_time']:.3f}s")
            print(f"   - 索引大小: {result['metadata']['index_size']}")
            
            # 显示前3个结果
            if data["results"]:
                print(f"\n   前{min(3, len(data['results']))}个结果:")
                for i, item in enumerate(data["results"][:3], 1):
                    print(f"      {i}. {os.path.basename(item['image_path'])} (score: {item['score']:.4f})")
            
            return True
        else:
            print(f"   ❌ 搜索失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 直接运行此文件时进行测试
    print("="*60)
    print("真实工具集成测试")
    print("="*60)
    
    success = test_real_search()
    
    if success:
        print("\n✅ 集成测试通过！")
    else:
        print("\n❌ 集成测试失败")
        print("\n排查建议:")
        print("  1. 检查member_a_search目录是否存在")
        print("  2. 检查是否有必要的索引文件（output/*.index）")
        print("  3. 运行: python -c 'from member_a_search.engine import search_meme'")

