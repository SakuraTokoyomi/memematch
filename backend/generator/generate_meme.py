import os
import time
import hashlib
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional, Tuple


def generate_meme(text: str, template: str = "drake", options: dict = None) -> dict:
    """
    生成表情包图片

    Args:
        text: 要显示在 meme 上的文字
        template: 模板类型 (drake/doge/wojak)
        options: 生成选项（字体、颜色等）

    Returns:
        包含生成结果的字典
    """
    start_time = time.time()

    # 有效模板列表（仅三个）
    valid_templates = ["drake", "doge", "wojak"]

    # 默认选项
    default_options = {
        "font_size": 32,
        "font_family": "genshen",  # 默认使用genshen字体支持中文
        "text_color": "#FFFFFF",
        "output_format": "png"
    }

    # 合并选项
    if options is None:
        options = {}
    params = {**default_options, **options}

    try:
        # 验证模板
        if template not in valid_templates:
            return {
                "success": False,
                "error": f"Template '{template}' not found",
                "error_code": "TEMPLATE_NOT_FOUND",
                "metadata": {
                    "available_templates": valid_templates
                }
            }

        # 验证文本
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Text cannot be empty",
                "error_code": "INVALID_TEXT",
                "metadata": {}
            }

        # 确保输出目录存在
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        # 生成图片
        image, dimensions = _create_meme_image(text, template, params)

        # 生成文件名
        text_hash = hashlib.md5(f"{text}{time.time()}".encode()).hexdigest()[:8]
        filename = f"generated_{template}_{text_hash}.{params['output_format']}"
        output_path = output_dir / filename

        # 保存图片
        image.save(output_path, format=params['output_format'].upper())
        file_size = output_path.stat().st_size

        generation_time = time.time() - start_time

        return {
            "success": True,
            "data": {
                "image_path": str(output_path),
                "template": template,
                "text": text,
                "dimensions": dimensions,
                "file_size": file_size,
                "format": params['output_format']
            },
            "metadata": {
                "generation_time": round(generation_time, 3),
                "template_version": "1.0",
                "parameters_used": params,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "GENERATION_ERROR",
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }


def _load_font(font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
    """
    加载字体，优先使用genshen.ttf支持中文

    Args:
        font_family: 字体名称
        font_size: 字体大小

    Returns:
        字体对象
    """
    # 字体路径优先级列表
    font_paths = [
        f"templates/{font_family}.ttf",  # 自定义字体文件夹
        f"{font_family}.ttf",  # 当前目录
        "templates/genshen.ttf",  # 默认中文字体
        "genshen.ttf",  # 根目录的genshen字体
        "/usr/share/fonts/truetype/arphic/uming.ttc",  # Linux 中文字体
        "/System/Library/Fonts/PingFang.ttc",  # macOS 中文字体
        "C:\\Windows\\Fonts\\msyh.ttc",  # Windows 微软雅黑
        "arial.ttf"  # 备用字体
    ]

    # 尝试加载字体
    for font_path in font_paths:
        try:
            if Path(font_path).exists():
                return ImageFont.truetype(font_path, font_size)
        except Exception:
            continue

    # 如果都失败，返回默认字体
    print("⚠️  Warning: Cannot load custom font, using default")
    return ImageFont.load_default()


def _is_chinese_char(char: str) -> bool:
    """判断是否为中文字符"""
    return '\u4e00' <= char <= '\u9fff'


def _has_chinese(text: str) -> bool:
    """判断文本是否包含中文"""
    return any(_is_chinese_char(char) for char in text)


def _create_meme_image(text: str, template: str, params: dict) -> Tuple[Image.Image, list]:
    """
    创建表情包图片

    Returns:
        (Image对象, [width, height])
    """
    # 模板配置
    template_configs = {
        "drake": {
            "size": (600, 600),
            "text_areas": [
                {"position": (380, 150), "max_width": 200},  # 上方文字区
                {"position": (380, 450), "max_width": 200}  # 下方文字区
            ]
        },
        "doge": {
            "size": (600, 600),
            "text_areas": [
                {"position": (300, 480), "max_width": 500}  # 底部居中显示
            ]
        },
        "wojak": {
            "size": (500, 500),
            "text_areas": [
                {"position": (250, 420), "max_width": 400}
            ]
        }
    }

    config = template_configs[template]
    width, height = config["size"]

    # 尝试加载模板图片，如果不存在则创建基础模板
    template_path = Path(f"templates/{template}.png")

    if template_path.exists():
        image = Image.open(template_path).convert("RGB")
        image = image.resize(config["size"])
    else:
        # 创建基础模板
        image = _create_basic_template(template, config)

    # 在图片上添加文字
    image = _add_text_to_image(image, text, template, config, params)

    return image, [width, height]


def _create_basic_template(template: str, config: dict) -> Image.Image:
    """创建基础模板（当模板图片不存在时）"""
    width, height = config["size"]
    image = Image.new("RGB", (width, height), color="#FFFFFF")
    draw = ImageDraw.Draw(image)

    if template == "drake":
        # Drake 模板：上下两部分
        # 上半部分 - 拒绝（浅色）
        draw.rectangle([(0, 0), (width, height // 2)], fill="#FFE4B5")
        # 下半部分 - 接受（绿色）
        draw.rectangle([(0, height // 2), (width, height)], fill="#90EE90")
        # 分割线
        draw.line([(0, height // 2), (width, height // 2)], fill="#000000", width=3)
        # 中间竖线
        draw.line([(width // 2, 0), (width // 2, height)], fill="#000000", width=3)

        # 左侧图标区域
        left_width = width // 2

        # 上方 - 拒绝姿势（使用文字代替emoji）
        draw.rectangle([(20, 50), (left_width - 20, height // 2 - 50)], fill="#DEB887")
        emoji_font = _load_font("genshen", 60)
        draw.text((left_width // 2, height // 4), "×", fill="#8B0000", font=emoji_font, anchor="mm")

        # 下方 - 接受姿势
        draw.rectangle([(20, height // 2 + 50), (left_width - 20, height - 50)], fill="#DEB887")
        draw.text((left_width // 2, 3 * height // 4), "✓", fill="#006400", font=emoji_font, anchor="mm")

    elif template == "doge":
        # Doge 模板：柴犬背景色
        draw.rectangle([(0, 0), (width, height)], fill="#F4D03F")

        # 绘制简化的柴犬
        # 头部
        draw.ellipse([(200, 200), (400, 400)], fill="#D4A574", outline="#000000", width=3)
        # 耳朵
        draw.polygon([(180, 250), (220, 180), (240, 250)], fill="#D4A574", outline="#000000")
        draw.polygon([(360, 250), (380, 180), (420, 250)], fill="#D4A574", outline="#000000")
        # 眼睛
        draw.ellipse([(240, 280), (270, 310)], fill="#000000")
        draw.ellipse([(330, 280), (360, 310)], fill="#000000")
        # 鼻子
        draw.ellipse([(285, 330), (315, 360)], fill="#000000")
        # 嘴巴
        draw.arc([(260, 330), (340, 380)], 0, 180, fill="#000000", width=3)

        # 添加经典 Doge 文字装饰（固定装饰文字）
        doge_font = _load_font("genshen", 24)
        draw.text((50, 50), "such wow", fill="#FF1493", font=doge_font)
        draw.text((480, 80), "very", fill="#4169E1", font=doge_font)
        draw.text((80, 500), "much", fill="#32CD32", font=doge_font)

    elif template == "wojak":
        # Wojak 模板：简单悲伤背景
        draw.rectangle([(0, 0), (width, height)], fill="#D3D3D3")

        # 头
        draw.ellipse([(150, 80), (350, 320)], fill="#FFE4C4", outline="#000000", width=3)

        # 眼睛（悲伤）
        draw.ellipse([(190, 150), (220, 180)], fill="#000000")
        draw.ellipse([(280, 150), (310, 180)], fill="#000000")

        # 眉毛（悲伤上扬）
        draw.arc([(180, 130), (230, 160)], 180, 360, fill="#000000", width=4)
        draw.arc([(270, 130), (320, 160)], 180, 360, fill="#000000", width=4)

        # 嘴巴（悲伤下弯）
        draw.arc([(210, 240), (290, 280)], 0, 180, fill="#000000", width=4)

        # 泪水
        draw.ellipse([(215, 190), (225, 230)], fill="#ADD8E6", outline="#4682B4", width=2)
        draw.ellipse([(305, 190), (315, 230)], fill="#ADD8E6", outline="#4682B4", width=2)

    return image


def _add_text_to_image(image: Image.Image, text: str, template: str,
                       config: dict, params: dict) -> Image.Image:
    """在图片上添加文字"""
    draw = ImageDraw.Draw(image)

    # 加载字体（使用genshen.ttf支持中文）
    font = _load_font(params['font_family'], params['font_size'])

    # 解析颜色
    text_color = params['text_color']

    # 根据模板类型处理文字
    if template == "drake":
        # Drake 模板：分割文字到上下两部分
        text_parts = _split_text(text, 2)
        for i, area in enumerate(config["text_areas"]):
            if i < len(text_parts) and text_parts[i].strip():
                wrapped_text = _wrap_text_smart(text_parts[i], font, area["max_width"], draw)
                _draw_text_with_outline(
                    draw, area["position"], wrapped_text,
                    font, text_color, "mm"
                )

    else:  # doge 和 wojak 都是单区域显示
        # 居中显示，支持长文本换行
        area = config["text_areas"][0]
        wrapped_text = _wrap_text_smart(text, font, area["max_width"], draw)
        _draw_text_with_outline(
            draw, area["position"], wrapped_text,
            font, text_color, "mm"
        )

    return image


def _split_text(text: str, parts: int) -> list:
    """将文字分割成指定数量的部分"""
    # 优先使用|分隔符
    if "|" in text:
        return text.split("|")[:parts]

    # 如果没有|，尝试智能分割
    words = text.split()
    if len(words) <= parts:
        return words + [""] * (parts - len(words))

    chunk_size = len(words) // parts
    result = []
    for i in range(parts):
        start = i * chunk_size
        end = start + chunk_size if i < parts - 1 else len(words)
        result.append(" ".join(words[start:end]))

    return result


def _wrap_text_smart(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> str:
    """
    智能换行文字，支持中英文混合
    - 中文按字符换行
    - 英文按单词换行
    - 混合文本智能处理
    """
    if not text.strip():
        return text

    # 检查是否包含中文
    has_cn = _has_chinese(text)

    if has_cn:
        # 中文文本处理：按字符换行
        return _wrap_chinese_text(text, font, max_width, draw)
    else:
        # 英文文本处理：按单词换行
        return _wrap_english_text(text, font, max_width, draw)


def _wrap_chinese_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> str:
    """中文文本自动换行（按字符）"""
    lines = []
    current_line = ""

    for char in text:
        # 如果是换行符，直接添加到结果
        if char == '\n':
            lines.append(current_line)
            current_line = ""
            continue

        test_line = current_line + char

        # 测量文本宽度
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
        except:
            width = draw.textlength(test_line, font=font)

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = char
            else:
                # 单个字符就超宽，强制添加
                lines.append(char)
                current_line = ""

    if current_line:
        lines.append(current_line)

    return '\n'.join(lines)


def _wrap_english_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> str:
    """英文文本自动换行（按单词）"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])

        try:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
        except:
            width = draw.textlength(test_line, font=font)

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # 单词太长，强制添加
                lines.append(word)

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)


def _draw_text_with_outline(draw: ImageDraw.Draw, position: tuple, text: str,
                            font: ImageFont.FreeTypeFont, color: str, anchor: str = "mm"):
    """绘制带描边的文字（提高可读性）"""
    x, y = position
    outline_color = "#000000" if color != "#000000" else "#FFFFFF"

    # 绘制描边（增强对比度）
    outline_range = 2
    for offset_x in range(-outline_range, outline_range + 1):
        for offset_y in range(-outline_range, outline_range + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text(
                    (x + offset_x, y + offset_y), text,
                    font=font, fill=outline_color, anchor=anchor
                )

    # 绘制主文字
    draw.text((x, y), text, font=font, fill=color, anchor=anchor)


# ============= 测试代码 =============
if __name__ == "__main__":
    print("🎨 表情包生成器 - 简化版\n")
    print("=" * 60)

    # 测试1: Drake 模板 - 中文
    print("\n📋 测试 1: Drake 模板（中文）")
    result1 = generate_meme(
        text="写文档|写代码",
        template="drake"
    )
    print(f"✅ 成功: {result1['success']}")
    if result1['success']:
        print(f"📁 路径: {result1['data']['image_path']}")
        print(f"⏱️  耗时: {result1['metadata']['generation_time']}s")

    # 测试2: Doge 模板 - 单行文本
    print("\n📋 测试 2: Doge 模板（单行文本）")
    result2 = generate_meme(
        text="如此优雅的代码",
        template="doge",
        options={"font_size": 36}
    )
    print(f"✅ 成功: {result2['success']}")
    if result2['success']:
        print(f"📁 路径: {result2['data']['image_path']}")
        print(f"⏱️  耗时: {result2['metadata']['generation_time']}s")

    # 测试3: Wojak 模板 - 长文本自动换行
    print("\n📋 测试 3: Wojak 模板（长文本换行）")
    result3 = generate_meme(
        text="这是一段很长很长的文字，应该会自动换行显示在图片上，不会超出边界才对",
        template="wojak",
        options={"font_size": 32, "text_color": "#FF0000"}
    )
    print(f"✅ 成功: {result3['success']}")
    if result3['success']:
        print(f"📁 路径: {result3['data']['image_path']}")
        print(f"⏱️  耗时: {result3['metadata']['generation_time']}s")

    # 测试4: Drake 长文本
    print("\n📋 测试 4: Drake 模板（长文本）")
    result4 = generate_meme(
        text="每天都要写很多很多的文档|终于可以开心地写代码了",
        template="drake",
        options={"font_size": 28}
    )
    print(f"✅ 成功: {result4['success']}")
    if result4['success']:
        print(f"📁 路径: {result4['data']['image_path']}")

    # 测试5: Doge 长文本换行
    print("\n📋 测试 5: Doge 模板（长文本换行）")
    result5 = generate_meme(
        text="这是一段很长的描述文字会自动换行显示",
        template="doge",
        options={"font_size": 32, "text_color": "#FF1493"}
    )
    print(f"✅ 成功: {result5['success']}")
    if result5['success']:
        print(f"📁 路径: {result5['data']['image_path']}")

    # 测试6: 超长中文文本
    print("\n📋 测试 6: 超长中文文本换行")
    result6 = generate_meme(
        text="当你看到这段超级超级超级长的文字时，它应该会自动换行显示，每一行都不会超出图片的边界范围",
        template="wojak",
        options={"font_size": 24}
    )
    print(f"✅ 成功: {result6['success']}")
    if result6['success']:
        print(f"📁 路径: {result6['data']['image_path']}")

    # 测试7: 错误处理
    print("\n📋 测试 7: 错误模板")
    result7 = generate_meme(
        text="测试",
        template="unknown"
    )
    print(f"❌ 成功: {result7['success']}")
    print(f"🚫 错误: {result7['error']}")
    print(f"📝 可用模板: {result7['metadata']['available_templates']}")

    # 测试8: 空文本
    print("\n📋 测试 8: 空文本验证")
    result8 = generate_meme(
        text="   ",
        template="drake"
    )
    print(f"❌ 成功: {result8['success']}")
    print(f"🚫 错误: {result8['error']}")

    print("\n" + "=" * 60)
    print("✨ 所有测试完成！\n")
    print("💡 模板说明：")
    print("  📌 Drake: 上下对比（用|分隔）")
    print("  📌 Doge: 底部单行显示，支持长文本换行")
    print("  📌 Wojak: 底部单行显示，支持长文本换行")
    print("\n📝 使用示例：")
    print("  generate_meme('写文档|写代码', 'drake')")
    print("  generate_meme('如此优雅的代码', 'doge')")
    print("  generate_meme('又要加班了', 'wojak')")