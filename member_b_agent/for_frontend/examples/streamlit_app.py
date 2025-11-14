"""
Streamlit 完整示例

运行方式：
    pip install streamlit
    streamlit run streamlit_app.py
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from agent_service import MemeAgentService


# ============ 初始化 Agent ============

@st.cache_resource
def init_agent():
    """初始化 Agent（只运行一次）"""
    return MemeAgentService(use_mock=True, verbose=False)


# ============ 主界面 ============

def main():
    # 页面配置
    st.set_page_config(
        page_title="Meme Agent",
        page_icon="🎭",
        layout="centered"
    )
    
    # 标题
    st.title("🎭 Meme Agent")
    st.markdown("AI 驱动的智能梗图助手")
    
    # 初始化 Agent
    agent = init_agent()
    
    # 分隔线
    st.divider()
    
    # 用户输入区域
    st.subheader("💬 输入你的情绪或想法")
    user_input = st.text_input(
        label="",
        placeholder="例如：我太累了、开心、无语...",
        help="输入任何情绪或想表达的内容"
    )
    
    # 查询按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        search_btn = st.button("🔍 找梗图", type="primary", use_container_width=True)
    
    # 处理查询
    if search_btn and user_input:
        with st.spinner("🤖 AI 正在思考..."):
            result = agent.query(user_input)
        
        st.divider()
        
        # 显示结果
        if result["success"]:
            # 成功 - 显示 meme
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(
                    result["meme_path"],
                    caption="推荐的 Meme",
                    use_container_width=True
                )
            
            with col2:
                st.success("✅ 找到了！")
                st.markdown(f"**推荐理由：**")
                st.write(result["explanation"])
                st.info(f"**来源：** {result['source']}")
                
                # 下载按钮（可选）
                try:
                    with open(result["meme_path"], "rb") as f:
                        st.download_button(
                            label="💾 下载图片",
                            data=f,
                            file_name="meme.png",
                            mime="image/png"
                        )
                except:
                    pass
            
            # 显示候选结果（可选）
            if result.get("candidates"):
                with st.expander("🔍 查看更多候选"):
                    for i, candidate in enumerate(result["candidates"][:5], 1):
                        st.write(f"{i}. {candidate.get('image_path')} (分数: {candidate.get('score', 0):.2f})")
        
        else:
            # 失败 - 显示错误
            st.error(f"❌ {result['error']}")
            st.info("💡 提示：请稍后重试，或尝试更简单的描述")
    
    elif search_btn:
        st.warning("⚠️ 请输入内容")
    
    # 侧边栏
    with st.sidebar:
        st.header("ℹ️ 使用说明")
        st.markdown("""
        ### 如何使用
        
        1. 在输入框中输入你的情绪或想法
        2. 点击「找梗图」按钮
        3. AI 会自动推荐最合适的梗图
        
        ### 示例输入
        
        - "我太累了"
        - "开心"
        - "无语"
        - "震惊"
        - "不想努力了"
        
        ### 功能说明
        
        - 🔍 自动检索相关梗图
        - 🎨 找不到时自动生成
        - 💬 提供推荐理由
        - 💾 支持下载图片
        
        ---
        
        **技术支持：** 成员 B
        """)
        
        # 调试选项（可选）
        with st.expander("🔧 调试选项"):
            debug_mode = st.checkbox("显示详细信息")
            if debug_mode and "result" in locals():
                st.json(result)


if __name__ == "__main__":
    main()

