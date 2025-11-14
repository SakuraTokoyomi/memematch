"""
Gradio 完整示例

运行方式：
    pip install gradio
    python gradio_app.py
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from agent_service import MemeAgentService


# ============ 初始化 Agent ============

print("初始化 Meme Agent...")
agent = MemeAgentService(use_mock=True, verbose=False)
print("✓ Agent 已就绪")


# ============ 处理函数 ============

def process_query(user_input):
    """
    处理用户查询
    
    参数：
        user_input: 用户输入的文本
    
    返回：
        (image, explanation, info): 三元组
    """
    if not user_input or not user_input.strip():
        return None, "⚠️ 请输入内容", ""
    
    # 调用 Agent
    result = agent.query(user_input)
    
    # 返回结果
    if result["success"]:
        return (
            result["meme_path"],
            result["explanation"],
            f"✅ 来源: {result['source']}"
        )
    else:
        return (
            None,
            f"❌ {result['error']}",
            "💡 提示：请稍后重试，或尝试更简单的描述"
        )


# ============ 创建界面 ============

def create_demo():
    """创建 Gradio 界面"""
    
    # 自定义 CSS（可选）
    custom_css = """
    .gradio-container {
        max-width: 900px;
        margin: auto;
    }
    """
    
    with gr.Blocks(
        title="Meme Agent",
        css=custom_css,
        theme=gr.themes.Soft()
    ) as demo:
        # 标题
        gr.Markdown("""
        # 🎭 Meme Agent
        ### AI 驱动的智能梗图助手
        """)
        
        # 主界面
        with gr.Row():
            # 左侧：输入区域
            with gr.Column(scale=1):
                gr.Markdown("### 💬 输入")
                
                input_text = gr.Textbox(
                    label="输入你的情绪或想法",
                    placeholder="例如：我太累了、开心、无语...",
                    lines=3
                )
                
                submit_btn = gr.Button(
                    "🔍 找梗图",
                    variant="primary",
                    size="lg"
                )
                
                # 示例按钮
                gr.Examples(
                    examples=[
                        ["我太累了"],
                        ["开心"],
                        ["无语"],
                        ["震惊"],
                        ["不想努力了"]
                    ],
                    inputs=input_text,
                    label="💡 试试这些"
                )
            
            # 右侧：输出区域
            with gr.Column(scale=1):
                gr.Markdown("### 🎨 结果")
                
                output_image = gr.Image(
                    label="推荐的 Meme",
                    type="filepath"
                )
                
                output_text = gr.Textbox(
                    label="推荐理由",
                    lines=4
                )
                
                output_info = gr.Textbox(
                    label="额外信息",
                    lines=1
                )
        
        # 绑定事件
        submit_btn.click(
            fn=process_query,
            inputs=[input_text],
            outputs=[output_image, output_text, output_info]
        )
        
        # Enter 键也可以提交
        input_text.submit(
            fn=process_query,
            inputs=[input_text],
            outputs=[output_image, output_text, output_info]
        )
        
        # 使用说明
        with gr.Accordion("ℹ️ 使用说明", open=False):
            gr.Markdown("""
            ### 如何使用
            
            1. 在左侧输入框中输入你的情绪或想法
            2. 点击「找梗图」按钮（或按 Enter）
            3. AI 会自动推荐最合适的梗图
            
            ### 功能说明
            
            - 🔍 自动检索相关梗图
            - 🎨 找不到时自动生成
            - 💬 提供推荐理由
            
            ### 示例
            
            - "我太累了" → 疲惫类梗图
            - "开心" → 开心类梗图
            - "无语" → 无语类梗图
            
            ---
            
            **技术支持：** 成员 B
            """)
        
        # 页脚
        gr.Markdown("""
        ---
        <center>
        Made with ❤️ using Gradio + Meme Agent
        </center>
        """)
    
    return demo


# ============ 启动应用 ============

if __name__ == "__main__":
    demo = create_demo()
    
    # 启动（可自定义配置）
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,        # 端口
        share=False,             # 是否生成公开链接
        show_error=True          # 显示错误信息
    )

