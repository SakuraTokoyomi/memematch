"""
Agent 核心功能测试
"""

import os
import sys
import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.agent_core import MemeAgent, create_agent
from agent.config import AgentConfig
from agent.tools import mock_search_meme, mock_generate_meme


class TestAgentBasic:
    """基础功能测试"""
    
    def setup_method(self):
        """测试前准备"""
        # 使用测试配置
        self.config = AgentConfig(
            api_key="9a2266c7-a96a-4459-be90-af5dfc58a655",
            model="Meta-Llama-3.1-8B-Instruct",
            max_iterations=5
        )
        self.agent = MemeAgent(self.config)
        
        # 注册 mock 工具
        self.agent.register_tool("search_meme", mock_search_meme)
        self.agent.register_tool("generate_meme", mock_generate_meme)
    
    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent is not None
        assert self.agent.config.model == "Meta-Llama-3.1-8B-Instruct"
        assert len(self.agent.tools) == 4  # 4 个工具定义
    
    def test_tool_registration(self):
        """测试工具注册"""
        assert "search_meme" in self.agent.tool_functions
        assert "generate_meme" in self.agent.tool_functions
        
        # 测试工具调用（v2 格式）
        result = self.agent.tool_functions["search_meme"]("tired", 3)
        assert result.get("success") == True
        assert "data" in result
        assert "results" in result["data"]
        assert len(result["data"]["results"]) <= 3
        assert "metadata" in result  # v2 新增
    
    def test_refine_query(self):
        """测试查询改写"""
        # 注意：这个测试需要实际的 API key
        if not os.getenv("SAMBANOVA_API_KEY"):
            pytest.skip("需要 SAMBANOVA_API_KEY 环境变量")
        
        result = self.agent._refine_query_internal("我无语了")
        assert "refined" in result
        assert result["original"] == "我无语了"
        print(f"改写结果: {result['original']} → {result['refined']}")
    
    def test_classify_sentiment(self):
        """测试情绪分类"""
        if not os.getenv("SAMBANOVA_API_KEY"):
            pytest.skip("需要 SAMBANOVA_API_KEY 环境变量")
        
        result = self.agent._classify_sentiment_internal("我太累了")
        assert "emotion" in result
        assert "intensity" in result
        print(f"情绪分类: {result}")


class TestAgentIntegration:
    """集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = AgentConfig(
            api_key=os.getenv("SAMBANOVA_API_KEY", "test-key"),
            model="Meta-Llama-3.1-8B-Instruct",
            max_iterations=8
        )
        self.agent = MemeAgent(self.config)
        self.agent.register_tool("search_meme", mock_search_meme)
        self.agent.register_tool("generate_meme", mock_generate_meme)
    
    @pytest.mark.skipif(not os.getenv("SAMBANOVA_API_KEY"), 
                        reason="需要 SAMBANOVA_API_KEY")
    def test_full_query_flow(self):
        """测试完整的查询流程"""
        result = self.agent.process_query("我真的不想努力了", debug=True)
        
        # 验证返回结果
        assert result is not None
        assert "status" in result
        
        if result.get("status") == "success":
            assert "meme_path" in result or "error" in result
            assert "reasoning_steps" in result
            
            print("\n查询结果:")
            print(f"  Meme: {result.get('meme_path')}")
            print(f"  来源: {result.get('source')}")
            print(f"  解释: {result.get('explanation')}")
            print(f"  推理步骤数: {len(result.get('reasoning_steps', []))}")
    
    @pytest.mark.skipif(not os.getenv("SAMBANOVA_API_KEY"),
                        reason="需要 SAMBANOVA_API_KEY")
    def test_multiple_queries(self):
        """测试多个不同的查询"""
        queries = [
            "我无语了",
            "太开心了",
            "震惊",
        ]
        
        for query in queries:
            print(f"\n测试查询: {query}")
            result = self.agent.process_query(query)
            
            assert result is not None
            print(f"  结果: {result.get('status')}")
            print(f"  Meme: {result.get('meme_path')}")


class TestToolInterface:
    """工具接口测试（v2）"""
    
    def test_mock_search_meme(self):
        """测试 mock 搜索工具（v2 格式）"""
        result = mock_search_meme("tired", top_k=3)
        
        # v2 格式断言
        assert result.get("success") == True
        assert "data" in result
        assert "metadata" in result
        assert "results" in result["data"]
        assert len(result["data"]["results"]) <= 3
        assert all("score" in r for r in result["data"]["results"])
        assert all("image_path" in r for r in result["data"]["results"])
    
    def test_mock_generate_meme(self):
        """测试 mock 生成工具（v2 格式）"""
        result = mock_generate_meme("不想努力", template="drake")
        
        # v2 格式断言
        assert result.get("success") == True
        assert "data" in result
        assert "metadata" in result
        assert "image_path" in result["data"]
        assert result["data"]["template"] == "drake"
        assert result["data"]["text"] == "不想努力"


def test_create_agent_helper():
    """测试便捷创建函数"""
    agent = create_agent(
        api_key="test-key",
        model="Meta-Llama-3.1-8B-Instruct"
    )
    
    assert agent is not None
    assert agent.config.api_key == "test-key"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])

