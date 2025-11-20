"""
测试成员C（Meme生成器）的集成
"""

import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from agent.real_tools import real_generate_meme, REAL_GENERATE_AVAILABLE

def test_generate_availability():
    """测试生成器是否可用"""
    print("=" * 60)
    print("测试1: 检查生成器可用性")
    print("=" * 60)
    
    if REAL_GENERATE_AVAILABLE:
        print("✅ 成员C的Meme生成器已成功导入")
        return True
    else:
        print("❌ 成员C的Meme生成器导入失败")
        return False


def test_drake_template():
    """测试Drake模板"""
    print("\n" + "=" * 60)
    print("测试2: Drake模板生成")
    print("=" * 60)
    
    result = real_generate_meme(
        text="写文档|写代码",
        template="drake"
    )
    
    if result.get("success"):
        print(f"✅ 生成成功")
        print(f"   路径: {result['data']['image_path']}")
        print(f"   模板: {result['data']['template']}")
        print(f"   耗时: {result['metadata']['generation_time']}s")
        return True
    else:
        print(f"❌ 生成失败: {result.get('error')}")
        return False


def test_doge_template():
    """测试Doge模板"""
    print("\n" + "=" * 60)
    print("测试3: Doge模板生成")
    print("=" * 60)
    
    result = real_generate_meme(
        text="如此优雅的代码",
        template="doge"
    )
    
    if result.get("success"):
        print(f"✅ 生成成功")
        print(f"   路径: {result['data']['image_path']}")
        print(f"   模板: {result['data']['template']}")
        print(f"   耗时: {result['metadata']['generation_time']}s")
        return True
    else:
        print(f"❌ 生成失败: {result.get('error')}")
        return False


def test_wojak_template():
    """测试Wojak模板"""
    print("\n" + "=" * 60)
    print("测试4: Wojak模板生成")
    print("=" * 60)
    
    result = real_generate_meme(
        text="又要加班了",
        template="wojak"
    )
    
    if result.get("success"):
        print(f"✅ 生成成功")
        print(f"   路径: {result['data']['image_path']}")
        print(f"   模板: {result['data']['template']}")
        print(f"   耗时: {result['metadata']['generation_time']}s")
        return True
    else:
        print(f"❌ 生成失败: {result.get('error')}")
        return False


def test_invalid_template():
    """测试无效模板"""
    print("\n" + "=" * 60)
    print("测试5: 无效模板（错误处理）")
    print("=" * 60)
    
    result = real_generate_meme(
        text="测试",
        template="unknown"
    )
    
    if not result.get("success"):
        print(f"✅ 正确处理错误: {result.get('error')}")
        print(f"   错误代码: {result.get('error_code')}")
        return True
    else:
        print(f"❌ 应该返回错误但却成功了")
        return False


def test_custom_options():
    """测试自定义选项"""
    print("\n" + "=" * 60)
    print("测试6: 自定义选项")
    print("=" * 60)
    
    result = real_generate_meme(
        text="Python|Java",
        template="drake",
        options={
            "font_size": 40,
            "text_color": "#FFD700"
        }
    )
    
    if result.get("success"):
        print(f"✅ 生成成功（自定义样式）")
        print(f"   路径: {result['data']['image_path']}")
        print(f"   参数: {result['metadata']['parameters_used']}")
        return True
    else:
        print(f"❌ 生成失败: {result.get('error')}")
        return False


if __name__ == "__main__":
    print("🎨 成员C集成测试")
    print("=" * 60)
    
    tests = [
        test_generate_availability,
        test_drake_template,
        test_doge_template,
        test_wojak_template,
        test_invalid_template,
        test_custom_options
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"✅ 通过: {passed}/{len(tests)}")
    print(f"❌ 失败: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！成员C集成成功！")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")

