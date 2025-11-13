#!/usr/bin/env python
"""
脚本2：导出向量文件

功能：
- 加载最佳模型（或指定模型）
- 编码所有表情包描述为向量
- 导出向量文件供检索系统使用

使用方法：
    # 使用指定模型
    python scripts/02_export_embeddings.py --model paraphrase-multilingual-MiniLM-L12-v2
    
    # 使用本地微调模型
    python scripts/02_export_embeddings.py --model ./models/finetuned_model
"""

import sys
from pathlib import Path
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.embedding_exporter import EmbeddingExporter


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='导出表情包向量')
    parser.add_argument(
        '--model',
        type=str,
        default='paraphrase-multilingual-MiniLM-L12-v2',
        help='模型名称或路径（默认：paraphrase-multilingual-MiniLM-L12-v2）'
    )
    parser.add_argument(
        '--meme-file',
        type=str,
        default='memes.json',
        help='表情包数据文件名（默认：memes.json）'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs',
        help='输出目录（默认：outputs）'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='批处理大小（默认：32）'
    )
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    print("="*70)
    print("📦 MemeMatch 向量导出工具")
    print("="*70)
    print(f"模型: {args.model}")
    print(f"输入: data/{args.meme_file}")
    print(f"输出: {args.output_dir}/")
    print(f"批大小: {args.batch_size}")
    print("="*70)
    
    # 构建路径
    meme_data_path = project_root / "data" / args.meme_file
    output_dir = project_root / args.output_dir
    
    # 检查输入文件
    if not meme_data_path.exists():
        print(f"\n❌ 错误: 数据文件不存在: {meme_data_path}")
        print(f"\n💡 请检查:")
        print(f"   1. 数据文件是否在 data/ 目录")
        print(f"   2. 文件名是否正确: {args.meme_file}")
        print(f"   3. 如果使用示例数据: --meme-file memes_sample.json")
        return
    
    try:
        # 1. 初始化导出器
        exporter = EmbeddingExporter(args.model)
        
        # 2. 导出向量
        embeddings, meme_ids, meme_texts = exporter.export_meme_embeddings(
            meme_data_path=str(meme_data_path),
            output_dir=str(output_dir),
            batch_size=args.batch_size
        )
        
        # 3. 输出成功信息
        print(f"\n🎉 向量导出成功!")
        print(f"\n📋 导出摘要:")
        print(f"   - 表情包数量: {len(meme_ids)}")
        print(f"   - 向量维度: {embeddings.shape[1]}")
        print(f"   - 向量文件: {output_dir}/meme_embeddings.npy")
        print(f"   - ID文件: {output_dir}/meme_ids.json")
        
        print(f"\n✅ 请将以下文件交付给成员3（检索系统工程师）:")
        print(f"   📁 {output_dir}/")
        print(f"      ├── meme_embeddings.npy  (向量数据)")
        print(f"      ├── meme_ids.json        (ID映射)")
        print(f"      ├── meme_texts.txt       (文本列表)")
        print(f"      └── metadata.json        (元数据)")
        
        print(f"\n💡 成员3使用示例:")
        print(f"   import numpy as np")
        print(f"   import json")
        print(f"   embeddings = np.load('{output_dir}/meme_embeddings.npy')")
        print(f"   with open('{output_dir}/meme_ids.json') as f:")
        print(f"       meme_ids = json.load(f)")
        print()
        
    except Exception as e:
        print(f"\n❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()

