#!/usr/bin/env python3
"""
API 测试脚本

测试 FastAPI 服务是否正常工作
"""

import requests
import json
import time


BASE_URL = "http://localhost:8000"


def print_section(title):
    """打印分节"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_health():
    """测试健康检查"""
    print_section("1. 健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if data.get("status") == "healthy":
            print("✅ 服务运行正常")
            return True
        else:
            print("❌ 服务异常")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n💡 提示: 请先启动服务")
        print("   python api_server.py")
        return False


def test_single_query():
    """测试单次查询"""
    print_section("2. 单次查询")
    
    payload = {
        "text": "我太累了"
    }
    
    print(f"请求: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json=payload
        )
        data = response.json()
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if data.get("success"):
            print(f"\n✅ 查询成功")
            print(f"   Meme: {data.get('meme_path')}")
            print(f"   理由: {data.get('explanation', '')[:50]}...")
            print(f"   来源: {data.get('source')}")
            return data.get("session_id")
        else:
            print(f"❌ 查询失败: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def test_multi_turn(session_id):
    """测试多轮对话"""
    print_section("3. 多轮对话")
    
    if not session_id:
        print("⚠️  跳过（没有 session_id）")
        return
    
    queries = [
        "再来一张",
        "换个开心的"
    ]
    
    for i, text in enumerate(queries, 2):
        print(f"\n第 {i} 轮: {text}")
        print(f"Session ID: {session_id[:8]}...")
        
        payload = {
            "text": text,
            "session_id": session_id
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/query",
                json=payload
            )
            data = response.json()
            
            if data.get("success"):
                print(f"✅ 成功")
                print(f"   Meme: {data.get('meme_path')}")
                print(f"   理由: {data.get('explanation', '')[:50]}...")
            else:
                print(f"❌ 失败: {data.get('error')}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        time.sleep(0.5)  # 避免请求过快


def test_session_info(session_id):
    """测试获取会话信息"""
    print_section("4. 获取会话信息")
    
    if not session_id:
        print("⚠️  跳过（没有 session_id）")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/api/session/{session_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 会话信息:")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   消息数: {data.get('message_count')}")
            print(f"   查询次数: {data.get('query_count')}")
            print(f"   创建时间: {data.get('created_at')}")
        else:
            print(f"❌ 获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_clear_session(session_id):
    """测试清除会话"""
    print_section("5. 清除会话")
    
    if not session_id:
        print("⚠️  跳过（没有 session_id）")
        return
    
    try:
        response = requests.delete(f"{BASE_URL}/api/session/{session_id}")
        data = response.json()
        
        if data.get("success"):
            print(f"✅ {data.get('message')}")
        else:
            print(f"⚠️  {data.get('message')}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_stats():
    """测试统计信息"""
    print_section("6. 统计信息")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        data = response.json()
        
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print("✅ 统计信息获取成功")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def main():
    """运行所有测试"""
    print("\n" + "🧪"*30)
    print("  Meme Agent API 测试")
    print("🧪"*30)
    
    # 1. 健康检查
    if not test_health():
        return
    
    # 2. 单次查询
    session_id = test_single_query()
    
    # 3. 多轮对话
    test_multi_turn(session_id)
    
    # 4. 会话信息
    test_session_info(session_id)
    
    # 5. 统计信息
    test_stats()
    
    # 6. 清除会话
    test_clear_session(session_id)
    
    print("\n" + "="*60)
    print("  ✅ 测试完成")
    print("="*60)
    
    print("\n📖 更多信息：")
    print(f"   API 文档: {BASE_URL}/docs")
    print(f"   健康检查: {BASE_URL}/health")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

