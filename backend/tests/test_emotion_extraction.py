"""
情绪识别能力测试

测试LLM（Meta-Llama-3.3-70B-Instruct）从用户输入中提取情绪词的准确率
"""

import os
import sys
from openai import OpenAI

# SambaNova API配置
API_KEY = os.getenv("SAMBANOVA_API_KEY", "9a2266c7-a96a-4459-be90-af5dfc58a655")
BASE_URL = "https://api.sambanova.ai/v1"
MODEL = "Meta-Llama-3.3-70B-Instruct"

# 初始化客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# 情绪提取Prompt
EMOTION_EXTRACTION_PROMPT = """你是情绪识别专家。从用户输入中提取核心情绪词。

规则：
1. 只提取情绪或状态词（开心、难过、累、压力、无奈等）
2. 忽略动作词（想、要、分享、表达、希望等）
3. 忽略对象词（老板、项目、考试等）
4. 只输出1-2个字的情绪词，不要解释

示例：
用户："我今天好开心" → 输出：开心
用户："我想分享这份喜悦" → 输出：喜悦
用户："项目延期了压力好大" → 输出：压力
用户："又咋了" → 输出：疑问

现在开始提取。"""


def extract_emotion(user_input: str, temperature: float = 0.1) -> str:
    """
    使用LLM提取情绪词
    
    Args:
        user_input: 用户输入
        temperature: 温度参数
        
    Returns:
        提取的情绪词
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": EMOTION_EXTRACTION_PROMPT},
                {"role": "user", "content": f"用户输入：{user_input}\n\n提取情绪词："}
            ],
            temperature=temperature,
            max_tokens=20
        )
        
        emotion = response.choices[0].message.content.strip()
        return emotion
        
    except Exception as e:
        return f"[错误: {e}]"


# 测试用例集
TEST_CASES = [
    # 类别1：简单直接的情绪词
    {
        "category": "简单情绪",
        "cases": [
            {"input": "开心", "expected": "开心"},
            {"input": "累", "expected": "累"},
            {"input": "无语", "expected": "无语"},
            {"input": "难过", "expected": "难过"},
            {"input": "生气", "expected": "生气"},
        ]
    },
    
    # 类别2：包含修饰词的情绪
    {
        "category": "修饰情绪",
        "cases": [
            {"input": "今天好开心", "expected": "开心"},
            {"input": "我太累了", "expected": "累"},
            {"input": "真的很难过", "expected": "难过"},
            {"input": "有点烦", "expected": "烦"},
            {"input": "非常生气", "expected": "生气"},
        ]
    },
    
    # 类别3：复杂句子（包含动作词）
    {
        "category": "复杂句子",
        "cases": [
            {"input": "我想分享这份喜悦", "expected": "喜悦"},
            {"input": "想表达一下开心的心情", "expected": "开心"},
            {"input": "希望能缓解一下压力", "expected": "压力"},
            {"input": "我需要发泄一下愤怒", "expected": "愤怒"},
        ]
    },
    
    # 类别4：长句子（LLM容易被干扰）
    {
        "category": "长句干扰",
        "cases": [
            {"input": "我今天工作很顺利，老板还夸奖了我，想分享这份喜悦", "expected": "喜悦"},
            {"input": "项目延期了，客户又催了，压力真的很大", "expected": "压力"},
            {"input": "今天考试考砸了，感觉特别沮丧", "expected": "沮丧"},
            {"input": "加班到很晚，回家路上堵车，真的累爆了", "expected": "累"},
        ]
    },
    
    # 类别5：隐含情绪（需要推理）
    {
        "category": "隐含情绪",
        "cases": [
            {"input": "项目又延期了", "expected": "无奈"},
            {"input": "考试考砸了", "expected": "沮丧"},
            {"input": "老板又给我加任务", "expected": "无奈"},
            {"input": "终于解决了这个bug", "expected": "开心"},
        ]
    },
    
    # 类别6：网络用语/口语
    {
        "category": "网络用语",
        "cases": [
            {"input": "我真的会谢", "expected": "无语"},
            {"input": "我服了", "expected": "服了"},
            {"input": "又咋了", "expected": "疑问"},
            {"input": "绷不住了", "expected": "崩溃"},
            {"input": "emo了", "expected": "emo"},
        ]
    },
    
    # 类别7：多情绪混合
    {
        "category": "多情绪",
        "cases": [
            {"input": "既开心又紧张", "expected": "开心"},  # 倾向主要情绪
            {"input": "累并快乐着", "expected": "累"},
            {"input": "有点焦虑但也期待", "expected": "焦虑"},
        ]
    },
    
    # 类别8：误导性测试
    {
        "category": "误导测试",
        "cases": [
            {"input": "我想分享", "expected": "分享"},  # 这个确实没有情绪
            {"input": "告诉我", "expected": "疑问"},
            {"input": "帮我找一个", "expected": "请求"},
        ]
    }
]


def run_tests():
    """运行所有测试用例"""
    print("=" * 80)
    print("🧪 情绪识别能力测试")
    print(f"📊 模型: {MODEL}")
    print(f"🌡️  温度: 0.1")
    print("=" * 80)
    
    total_count = 0
    correct_count = 0
    results = []
    
    for category_data in TEST_CASES:
        category = category_data["category"]
        cases = category_data["cases"]
        
        print(f"\n📂 类别: {category}")
        print("-" * 80)
        
        category_correct = 0
        category_total = len(cases)
        
        for case in cases:
            user_input = case["input"]
            expected = case["expected"]
            
            # 调用LLM提取情绪
            extracted = extract_emotion(user_input)
            
            # 判断是否正确（模糊匹配）
            is_correct = expected in extracted or extracted in expected
            
            # 统计
            total_count += 1
            if is_correct:
                correct_count += 1
                category_correct += 1
            
            # 显示结果
            status = "✅" if is_correct else "❌"
            print(f"{status} 输入: {user_input:50s} | 预期: {expected:8s} | 实际: {extracted:8s}")
            
            results.append({
                "category": category,
                "input": user_input,
                "expected": expected,
                "extracted": extracted,
                "correct": is_correct
            })
        
        # 类别统计
        accuracy = (category_correct / category_total * 100) if category_total > 0 else 0
        print(f"   📊 类别准确率: {category_correct}/{category_total} ({accuracy:.1f}%)")
    
    # 总体统计
    print("\n" + "=" * 80)
    print("📊 总体统计")
    print("=" * 80)
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    print(f"✅ 正确: {correct_count}/{total_count}")
    print(f"❌ 错误: {total_count - correct_count}/{total_count}")
    print(f"📈 准确率: {accuracy:.2f}%")
    
    # 分析错误
    errors = [r for r in results if not r["correct"]]
    if errors:
        print(f"\n❌ 错误分析（共{len(errors)}个）:")
        print("-" * 80)
        for err in errors:
            print(f"类别: {err['category']}")
            print(f"  输入: {err['input']}")
            print(f"  预期: {err['expected']} | 实际: {err['extracted']}")
            print()
    
    # 评级
    print("\n" + "=" * 80)
    if accuracy >= 90:
        print("🏆 评级: 优秀 - LLM情绪识别能力很强")
    elif accuracy >= 80:
        print("🥈 评级: 良好 - LLM情绪识别基本准确")
    elif accuracy >= 70:
        print("🥉 评级: 中等 - LLM情绪识别有待提升")
    else:
        print("⚠️  评级: 较差 - 建议优化Prompt或换模型")
    print("=" * 80)
    
    return results, accuracy


def test_different_temperatures():
    """测试不同温度对准确率的影响"""
    print("\n" + "=" * 80)
    print("🌡️  温度对比测试")
    print("=" * 80)
    
    temperatures = [0.0, 0.1, 0.3, 0.5, 0.7]
    test_input = "我今天工作很顺利，老板还夸奖了我，想分享这份喜悦"
    expected = "喜悦"
    
    print(f"测试输入: {test_input}")
    print(f"预期输出: {expected}")
    print("-" * 80)
    
    for temp in temperatures:
        extracted = extract_emotion(test_input, temperature=temp)
        is_correct = expected in extracted or extracted in expected
        status = "✅" if is_correct else "❌"
        print(f"{status} 温度={temp:.1f} | 提取结果: {extracted}")
    
    print("=" * 80)
    print("💡 建议: 通常温度越低（0.1-0.3），提取越稳定")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试LLM情绪识别能力")
    parser.add_argument("--temp-test", action="store_true", help="测试不同温度的影响")
    parser.add_argument("--single", type=str, help="测试单个输入")
    
    args = parser.parse_args()
    
    if args.single:
        # 单个测试
        print(f"输入: {args.single}")
        emotion = extract_emotion(args.single)
        print(f"提取情绪: {emotion}")
    
    elif args.temp_test:
        # 温度测试
        test_different_temperatures()
    
    else:
        # 完整测试套件
        results, accuracy = run_tests()
        
        # 可选：温度测试
        print("\n是否进行温度对比测试? (y/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                test_different_temperatures()
        except:
            pass

