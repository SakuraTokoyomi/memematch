"""
集成测试
测试 Agent 与真实工具的集成
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.agent_core import create_agent
from agent.tools import setup_mock_tools


class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.agent = create_agent(
            api_key=os.getenv("SAMBANOVA_API_KEY", "test-key"),
            model="Meta-Llama-3.1-8B-Instruct"
        )
    
    def test_with_mock_tools(self):
        """测试使用 Mock 工具"""
        setup_mock_tools(self.agent)
        
        result = self.agent.process_query("开心", max_iterations=3)
        
        # 基本验证
        assert result is not None
        assert "status" in result
    
    @pytest.mark.skipif(
        not os.getenv("SAMBANOVA_API_KEY"),
        reason="需要 SAMBANOVA_API_KEY"
    )
    def test_with_real_api(self):
        """测试真实 API"""
        setup_mock_tools(self.agent)
        
        test_queries = ["开心", "难过", "无语"]
        
        for query in test_queries:
            result = self.agent.process_query(query, max_iterations=3)
            
            assert result is not None
            assert result.get("status") in ["success", "error"]
            
            if result["status"] == "success":
                assert "meme_path" in result or "explanation" in result
    
    # TODO: 等待成员 A 完成后添加
    # def test_with_real_search(self):
    #     """测试真实的检索工具"""
    #     from member_a_search import search_meme
    #     self.agent.register_tool("search_meme", search_meme)
    #     ...
    
    # TODO: 等待成员 C 完成后添加
    # def test_with_real_generation(self):
    #     """测试真实的生成工具"""
    #     from member_c_generate import generate_meme
    #     self.agent.register_tool("generate_meme", generate_meme)
    #     ...


class TestPerformance:
    """性能测试"""
    
    def test_response_time(self):
        """测试响应时间"""
        import time
        
        agent = create_agent(api_key="test-key")
        setup_mock_tools(agent)
        
        start = time.time()
        result = agent.process_query("测试", max_iterations=2)
        duration = time.time() - start
        
        # Mock 模式应该很快
        assert duration < 1.0, f"响应时间 {duration:.2f}s 过长"
    
    @pytest.mark.skipif(
        not os.getenv("SAMBANOVA_API_KEY"),
        reason="需要 SAMBANOVA_API_KEY"
    )
    def test_api_response_time(self):
        """测试 API 响应时间"""
        import time
        
        agent = create_agent(
            api_key=os.getenv("SAMBANOVA_API_KEY")
        )
        setup_mock_tools(agent)
        
        start = time.time()
        result = agent.process_query("测试", max_iterations=3)
        duration = time.time() - start
        
        # API 调用应该在合理范围内
        assert duration < 10.0, f"响应时间 {duration:.2f}s 过长"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

