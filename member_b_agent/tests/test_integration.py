#!/usr/bin/env python
"""
测试成员A搜索引擎与成员B Agent的集成

运行方式：
    python test_integration.py
"""

import sys
import os

# 添加必要的路径
project_root = os.path.dirname(os.path.abspath(__file__))
member_b_path = os.path.join(project_root, 'member_b_agent')
member_a_path = os.path.join(project_root, 'member_a_search')

if member_b_path not in sys.path:
    sys.path.insert(0, member_b_path)
if member_a_path not in sys.path:
    sys.path.insert(0, member_a_path)

def test_direct_search():
    """测试直接调用成员A的搜索引擎"""
    print("="*60)
    print("测试1：直接调用成员A的搜索引擎")
    print("="*60)
    
    try:
        from engine import search_meme
        print("✅ 成功导入search_meme")
        
        # 测试搜索
        print("\n🔍 测试查询: 'happy'...")
        result = search_meme(query="happy", top_k=3)
        
        if result.get("success"):
            print("✅ 搜索成功!")
            data = result["data"]
            print(f"   - 返回结果: {data['total']} 个")
            print(f"   - 搜索耗时: {result['metadata']['search_time']:.3f}s")
            
            if data["results"]:
                print(f"\n   结果列表:")
                for i, item in enumerate(data["results"], 1):
                    print(f"      {i}. {os.path.basename(item['image_path'])} (分数: {item['score']:.4f})")
            return True
        else:
            print(f"❌ 搜索失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_integration():
    """测试通过Agent调用搜索"""
    print("\n" + "="*60)
    print("测试2：通过Agent调用搜索引擎")
    print("="*60)
    
    try:
        from agent.real_tools import real_search_meme, REAL_SEARCH_AVAILABLE
        
        if not REAL_SEARCH_AVAILABLE:
            print("❌ 搜索引擎未加载到Agent中")
            return False
        
        print("✅ Agent中的搜索接口可用")
        
        # 测试通过Agent接口搜索
        print("\n🔍 测试查询: 'surprised'...")
        result = real_search_meme(query="surprised", top_k=3)
        
        if result.get("success"):
            print("✅ Agent搜索成功!")
            data = result["data"]
            print(f"   - 返回结果: {data['total']} 个")
            
            if data["results"]:
                print(f"\n   结果列表:")
                for i, item in enumerate(data["results"], 1):
                    print(f"      {i}. {os.path.basename(item['image_path'])} (分数: {item['score']:.4f})")
            return True
        else:
            print(f"❌ Agent搜索失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_agent():
    """测试完整的Agent功能"""
    print("\n" + "="*60)
    print("测试3：完整Agent推理（带真实搜索）")
    print("="*60)
    
    try:
        from agent.agent_core import MemeAgent
        from agent.real_tools import setup_real_tools
        
        # 创建Agent
        print("\n📦 创建Agent...")
        agent = MemeAgent()
        
        # 注册真实工具
        print("🔧 注册真实搜索工具...")
        setup_real_tools(agent)
        
        # 测试查询
        user_query = "I'm feeling really tired today"
        print(f"\n🗣️  用户查询: {user_query}")
        print("💭 Agent推理中...\n")
        
        response = agent.process(user_query)
        
        print("\n" + "-"*60)
        print("📋 Agent响应:")
        print("-"*60)
        print(f"消息: {response.get('response', 'N/A')}")
        
        if "memes" in response and response["memes"]:
            print(f"\n推荐的表情包:")
            for i, meme in enumerate(response["memes"], 1):
                print(f"   {i}. {os.path.basename(meme['image_path'])}")
                print(f"      - 分数: {meme['score']:.4f}")
                if meme.get('tags'):
                    print(f"      - 标签: {', '.join(meme['tags'])}")
        
        print("-"*60)
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("\n" + "🧪 " + "="*58)
    print("   成员A搜索引擎 + 成员B Agent 集成测试")
    print("="*60 + "\n")
    
    results = []
    
    # 测试1：直接搜索
    result1 = test_direct_search()
    results.append(("直接搜索", result1))
    
    # 测试2：Agent接口
    result2 = test_agent_integration()
    results.append(("Agent接口", result2))
    
    # 测试3：完整Agent
    result3 = test_full_agent()
    results.append(("完整Agent", result3))
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20} {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("="*60)
    if all_passed:
        print("🎉 所有测试通过！集成成功！")
        print("\n💡 下一步:")
        print("   1. 在API服务中使用: setup_real_tools(agent)")
        print("   2. 测试API: python member_b_agent/api/test_api.py")
    else:
        print("❌ 部分测试失败")
        print("\n🔧 排查建议:")
        print("   1. 检查依赖: pip list | grep -E '(faiss|sentence-transformers)'")
        print("   2. 检查索引文件: ls member_a_search/output/*.index")
        print("   3. 检查配置: cat member_a_search/config.py")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

