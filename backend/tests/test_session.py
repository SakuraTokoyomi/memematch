#!/usr/bin/env python3
"""
会话管理测试

演示多轮对话功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from for_frontend.agent_service import MemeAgentService


def test_single_query():
    """测试单次查询（无会话）"""
    print("="*60)
    print("测试 1: 单次查询（不启用会话）")
    print("="*60)
    
    agent = MemeAgentService(use_mock=True, enable_session=False)
    
    result1 = agent.query("我太累了")
    print(f"\n查询 1: 我太累了")
    print(f"  成功: {result1['success']}")
    print(f"  Session ID: {result1.get('session_id', '无')}")
    
    result2 = agent.query("再来一张")
    print(f"\n查询 2: 再来一张")
    print(f"  成功: {result2['success']}")
    print(f"  Session ID: {result2.get('session_id', '无')}")
    print(f"  说明: Agent 不记得之前的对话")


def test_multi_turn():
    """测试多轮对话（启用会话）"""
    print("\n" + "="*60)
    print("测试 2: 多轮对话（启用会话）")
    print("="*60)
    
    agent = MemeAgentService(use_mock=True, enable_session=True)
    
    # 第一轮
    result1 = agent.query("我太累了")
    session_id = result1.get("session_id")
    print(f"\n第 1 轮: 我太累了")
    print(f"  成功: {result1['success']}")
    print(f"  Session ID: {session_id}")
    if result1['success']:
        print(f"  Meme: {result1['meme_path']}")
    
    # 第二轮（使用相同 session_id）
    result2 = agent.query("再来一张", session_id=session_id)
    print(f"\n第 2 轮: 再来一张 (session_id={session_id[:8]}...)")
    print(f"  成功: {result2['success']}")
    print(f"  Session ID: {result2.get('session_id')}")
    print(f"  说明: Agent 记得之前说过'我太累了'")
    
    # 第三轮（换个主题）
    result3 = agent.query("换个开心的", session_id=session_id)
    print(f"\n第 3 轮: 换个开心的 (session_id={session_id[:8]}...)")
    print(f"  成功: {result3['success']}")
    if result3['success']:
        print(f"  Meme: {result3['meme_path']}")
    
    # 查看会话信息
    info = agent.get_session_info(session_id)
    if info:
        print(f"\n会话信息:")
        print(f"  消息数: {info['message_count']}")
        print(f"  查询次数: {info['query_count']}")
        print(f"  创建时间: {info['created_at']}")


def test_multiple_sessions():
    """测试多个独立会话"""
    print("\n" + "="*60)
    print("测试 3: 多个独立会话")
    print("="*60)
    
    agent = MemeAgentService(use_mock=True, enable_session=True)
    
    # 会话 A
    result_a1 = agent.query("开心")
    session_a = result_a1.get("session_id")
    print(f"\n会话 A-1: 开心")
    print(f"  Session ID: {session_a[:8]}...")
    
    # 会话 B
    result_b1 = agent.query("难过")
    session_b = result_b1.get("session_id")
    print(f"\n会话 B-1: 难过")
    print(f"  Session ID: {session_b[:8]}...")
    print(f"  说明: 不同的 session ID，互不干扰")
    
    # 继续会话 A
    result_a2 = agent.query("再来一张", session_id=session_a)
    print(f"\n会话 A-2: 再来一张 (继续会话A)")
    print(f"  Session ID: {result_a2.get('session_id', '')[:8]}...")
    print(f"  说明: Agent 记得会话 A 说的是'开心'")
    
    # 继续会话 B
    result_b2 = agent.query("再来一张", session_id=session_b)
    print(f"\n会话 B-2: 再来一张 (继续会话B)")
    print(f"  Session ID: {result_b2.get('session_id', '')[:8]}...")
    print(f"  说明: Agent 记得会话 B 说的是'难过'")


def test_session_clear():
    """测试清除会话"""
    print("\n" + "="*60)
    print("测试 4: 清除会话")
    print("="*60)
    
    agent = MemeAgentService(use_mock=True, enable_session=True)
    
    result1 = agent.query("测试")
    session_id = result1.get("session_id")
    print(f"\n创建会话: {session_id[:8]}...")
    
    info = agent.get_session_info(session_id)
    print(f"会话存在: {info is not None}")
    
    # 清除会话
    cleared = agent.clear_session(session_id)
    print(f"\n清除会话: {cleared}")
    
    info = agent.get_session_info(session_id)
    print(f"会话存在: {info is not None}")


def main():
    """运行所有测试"""
    print("\n" + "🧪"*30)
    print("  会话管理功能测试")
    print("🧪"*30)
    
    try:
        test_single_query()
        test_multi_turn()
        test_multiple_sessions()
        test_session_clear()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
        print("\n📝 使用说明：")
        print("""
# 单次查询（不记住上下文）
agent = MemeAgentService(enable_session=False)
result = agent.query("我太累了")

# 多轮对话（记住上下文）
agent = MemeAgentService(enable_session=True)
result1 = agent.query("我太累了")
session_id = result1["session_id"]
result2 = agent.query("再来一张", session_id=session_id)

# 清除会话
agent.clear_session(session_id)
""")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

