#!/usr/bin/env python
"""
脚本1：模型对比实验

功能：
- 加载配置文件中的多个候选模型
- 在测试集上评估各模型性能
- 输出对比结果（CSV + 控制台报告）

使用方法：
    python scripts/01_compare_models.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
from src.model_evaluator import MemeModelEvaluator
from src.utils import load_config, load_data, save_results, format_report


def main():
    """主函数"""
    print("="*70)
    print("🚀 MemeMatch 模型对比实验")
    print("="*70)
    
    # 1. 加载配置
    print("\n📖 加载配置...")
    config = load_config(str(project_root / "config/models.yaml"))
    models_config = config['models']
    print(f"   待评估模型数量: {len(models_config)}")
    
    # 2. 加载数据
    print("\n📊 加载数据...")
    try:
        # 优先尝试加载完整数据
        try:
            meme_ids, meme_texts, query_ids, query_texts, ground_truth = load_data(
                data_dir=str(project_root / "data"),
                meme_file="memes.json",
                query_file="queries_test.json",
                split="test"
            )
            print("   ✅ 使用完整测试数据")
        except FileNotFoundError:
            # 如果完整数据不存在，使用示例数据
            print("   ⚠️  完整数据未找到，使用示例数据")
            meme_ids, meme_texts, query_ids, query_texts, ground_truth = load_data(
                data_dir=str(project_root / "data"),
                meme_file="memes_sample.json",
                query_file="queries_sample.json",
                split="test"
            )
            print("   ℹ️  这仅用于测试，等待成员2提供完整数据")
    except Exception as e:
        print(f"   ❌ 数据加载失败: {e}")
        print("\n💡 请检查:")
        print("   1. data/ 目录是否存在")
        print("   2. 是否有 memes_sample.json 和 queries_sample.json")
        print("   3. 数据格式是否正确（参考 data/README.md）")
        return
    
    # 3. 逐个评估模型
    results = []
    all_reports = []
    
    for idx, model_config in enumerate(models_config, 1):
        model_name = model_config['name']
        
        print(f"\n{'='*70}")
        print(f"📋 [{idx}/{len(models_config)}] 评估模型: {model_name}")
        print(f"   描述: {model_config.get('description', 'N/A')}")
        print(f"   维度: {model_config.get('dimensions', 'N/A')}")
        print(f"{'='*70}")
        
        try:
            # 初始化评估器
            evaluator = MemeModelEvaluator(model_name)
            
            # 评估
            start_time = time.time()
            metrics, _, _, inference_time = evaluator.evaluate(
                query_texts=query_texts,
                meme_texts=meme_texts,
                ground_truth=ground_truth,
                query_ids=query_ids,
                meme_ids=meme_ids
            )
            total_time = time.time() - start_time
            
            # 保存结果
            result = {
                'model_name': model_name,
                'dimensions': model_config.get('dimensions', 'N/A'),
                'language': model_config.get('language', 'N/A'),
                'recall@1': metrics['recall@1'],
                'recall@3': metrics['recall@3'],
                'recall@5': metrics['recall@5'],
                'mrr': metrics['mrr'],
                'inference_time_s': inference_time,
                'total_time_s': total_time,
                'queries_per_sec': len(query_texts) / inference_time if inference_time > 0 else 0
            }
            results.append(result)
            
            # 生成报告
            report = format_report(model_name, metrics, inference_time)
            all_reports.append(report)
            print(report)
            
        except Exception as e:
            print(f"❌ 模型评估失败: {e}")
            print(f"   跳过此模型，继续下一个...")
            continue
    
    # 4. 输出汇总结果
    if not results:
        print("\n❌ 没有成功评估的模型！")
        return
    
    print(f"\n{'='*70}")
    print(f"📊 评估完成！共成功评估 {len(results)} 个模型")
    print(f"{'='*70}")
    
    # 5. 保存结果
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # 保存CSV
    csv_path = output_dir / "model_comparison.csv"
    save_results(results, str(csv_path))
    
    # 保存详细报告
    report_path = output_dir / "evaluation_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("MemeMatch 模型评估报告\n")
        f.write("="*70 + "\n\n")
        f.write(f"测试集大小: {len(query_texts)} 条查询\n")
        f.write(f"表情包数量: {len(meme_texts)} 个\n")
        f.write(f"评估模型数: {len(results)} 个\n\n")
        for report in all_reports:
            f.write(report + "\n")
    print(f"✅ 详细报告已保存: {report_path}")
    
    # 6. 推荐最佳模型
    best_by_recall3 = max(results, key=lambda x: x['recall@3'])
    best_by_speed = max(results, key=lambda x: x['queries_per_sec'])
    
    print(f"\n{'='*70}")
    print(f"🏆 最佳模型推荐")
    print(f"{'='*70}")
    print(f"📈 准确率最高 (Recall@3): {best_by_recall3['model_name']}")
    print(f"   Recall@3 = {best_by_recall3['recall@3']:.4f}")
    print(f"\n⚡ 速度最快: {best_by_speed['model_name']}")
    print(f"   速度 = {best_by_speed['queries_per_sec']:.1f} 句/秒")
    print(f"{'='*70}")
    
    print(f"\n💡 下一步:")
    print(f"   1. 查看详细结果: {csv_path}")
    print(f"   2. 选择最佳模型进行向量导出")
    print(f"   3. 运行: python scripts/02_export_embeddings.py --model <模型名>")
    print()


if __name__ == "__main__":
    main()


