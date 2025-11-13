#!/usr/bin/env python
"""
环境测试脚本

运行此脚本检查环境是否正确安装

使用方法：
    python test_setup.py
"""

import sys


def test_python_version():
    """测试Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("   ❌ Python版本过低，需要 >= 3.7")
        return False
    print("   ✅ Python版本正常")
    return True


def test_imports():
    """测试必要的包是否安装"""
    print("\n🔍 检查依赖包...")
    
    packages = [
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('sklearn', 'scikit-learn'),
        ('yaml', 'PyYAML'),
        ('sentence_transformers', 'sentence-transformers'),
        ('torch', 'PyTorch'),
    ]
    
    all_ok = True
    for module_name, package_name in packages:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✅ {package_name}: {version}")
        except ImportError:
            print(f"   ❌ {package_name}: 未安装")
            all_ok = False
    
    return all_ok


def test_data_files():
    """测试数据文件是否存在"""
    print("\n🔍 检查数据文件...")
    
    from pathlib import Path
    
    files = [
        'data/memes_sample.json',
        'data/queries_sample.json',
        'config/models.yaml',
    ]
    
    all_ok = True
    for file_path in files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}: 文件不存在")
            all_ok = False
    
    return all_ok


def test_model_loading():
    """测试模型是否可以加载"""
    print("\n🔍 测试模型加载...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print("   尝试加载轻量模型...")
        model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # 最小的模型
        
        # 测试编码
        text = "测试文本"
        embedding = model.encode([text])
        
        print(f"   ✅ 模型加载成功")
        print(f"   ✅ 编码成功，向量维度: {embedding.shape[1]}")
        return True
        
    except Exception as e:
        print(f"   ❌ 模型加载失败: {e}")
        print(f"   💡 提示：可能需要下载模型（首次运行需要联网）")
        return False


def test_json_loading():
    """测试JSON数据加载"""
    print("\n🔍 测试数据加载...")
    
    try:
        import json
        
        # 测试表情包数据
        with open('data/memes_sample.json', 'r', encoding='utf-8') as f:
            memes = json.load(f)
        print(f"   ✅ 表情包数据: {len(memes)} 个")
        
        # 测试查询数据
        with open('data/queries_sample.json', 'r', encoding='utf-8') as f:
            queries = json.load(f)
        print(f"   ✅ 查询数据: {len(queries.get('test', []))} 条")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 数据加载失败: {e}")
        return False


def test_quick_evaluation():
    """快速评估测试"""
    print("\n🔍 快速评估测试...")
    
    try:
        from src.model_evaluator import MemeModelEvaluator
        from src.utils import load_data
        
        # 加载示例数据
        meme_ids, meme_texts, query_ids, query_texts, ground_truth = load_data(
            data_dir="data",
            meme_file="memes_sample.json",
            query_file="queries_sample.json",
            split="test"
        )
        
        print(f"   数据加载成功")
        print(f"   - 表情包: {len(meme_ids)} 个")
        print(f"   - 查询: {len(query_ids)} 条")
        
        print(f"   ⏳ 正在测试评估流程（可能需要1-2分钟）...")
        
        # 使用最小的模型快速测试
        evaluator = MemeModelEvaluator('paraphrase-MiniLM-L3-v2')
        metrics, _, _, _ = evaluator.evaluate(
            query_texts=query_texts[:3],  # 只测试3条
            meme_texts=meme_texts,
            ground_truth=ground_truth,
            query_ids=query_ids[:3],
            meme_ids=meme_ids
        )
        
        print(f"   ✅ 评估完成")
        print(f"   - Recall@3: {metrics['recall@3']:.4f}")
        print(f"   - MRR: {metrics['mrr']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  评估测试失败: {e}")
        print(f"   （这可能是因为首次下载模型，可以忽略）")
        return False


def main():
    """主测试流程"""
    print("="*70)
    print("🧪 MemeMatch 模型工程师 - 环境测试")
    print("="*70)
    
    results = []
    
    # 必要测试
    results.append(("Python版本", test_python_version()))
    results.append(("依赖包", test_imports()))
    results.append(("数据文件", test_data_files()))
    
    # 如果基础测试通过，进行高级测试
    if all(r[1] for r in results):
        results.append(("JSON加载", test_json_loading()))
        results.append(("模型加载", test_model_loading()))
        results.append(("快速评估", test_quick_evaluation()))
    
    # 输出总结
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:12} {status}")
    
    all_passed = all(r[1] for r in results[:3])  # 前3个是必须的
    
    print("="*70)
    if all_passed:
        print("✅ 环境配置正常！可以开始工作了")
        print("\n💡 下一步:")
        print("   1. 等待成员2提供数据")
        print("   2. 运行: python scripts/01_compare_models.py")
        print("   3. 查看: QUICKSTART.md")
    else:
        print("❌ 环境配置有问题，请修复后再试")
        print("\n💡 修复建议:")
        print("   1. 重新运行: pip install -r requirements.txt")
        print("   2. 检查Python版本 >= 3.7")
        print("   3. 确保网络连接正常（下载模型需要）")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


