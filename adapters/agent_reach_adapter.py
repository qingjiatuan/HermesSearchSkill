"""
Agent Reach 适配器 - 15+平台定向搜索（小红书/B站/Twitter/雪球等）
"""

import asyncio
import subprocess
from typing import List, Optional
from core.models import SearchResult, LayerResult, SearchSource
from core.path_utils import get_agent_reach_path
from adapters.base_adapter import BaseSearchAdapter


class AgentReachAdapter(BaseSearchAdapter):
    """Agent Reach 平台定向搜索适配器"""
    
    name: str = "agent-reach"
    
    def __init__(self, skill_path: str, config: dict):
        super().__init__(skill_path, config)
        try:
            self.agent_reach_path = str(get_agent_reach_path())
            self.available = True
        except FileNotFoundError:
            self.available = False
    
    async def search(self, query: str, max_results: int = 10, 
                    platform: Optional[str] = None, **kwargs) -> LayerResult:
        """
        执行 Agent Reach 搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            platform: 指定平台（xiaohongshu/bilibili/twitter/xueqiu等）
        """
        result = LayerResult(layer_name=self.name)
        
        if not self.available:
            result.success = False
            result.error_msg = "Agent Reach 未安装，请运行: python check_deps.py"
            return result
        
        # 如果指定了平台，使用定向搜索
        if platform:
            return await self._platform_search(query, platform, max_results)
        
        # 自动检测查询中的平台关键词
        detected_platform = self._detect_platform(query)
        if detected_platform:
            return await self._platform_search(query, detected_platform, max_results)
        
        # 没有指定平台，尝试通用搜索
        return await self._general_search(query, max_results)
    
    def _detect_platform(self, query: str) -> Optional[str]:
        """从查询中检测平台"""
        query_lower = query.lower()
        
        platform_keywords = {
            "xiaohongshu": ["小红书", "小红薯", "xhs", "xiaohongshu"],
            "bilibili": ["b站", "哔哩哔哩", "bilibili", "小破站"],
            "twitter": ["推特", "twitter", "tweet", "x.com"],
            "xueqiu": ["雪球", "xueqiu", "股票", "行情"],
            "linkedin": ["领英", "linkedin", "招聘", "求职"],
            "zhihu": ["知乎", "zhihu"],
            "weibo": ["微博", "weibo"],
        }
        
        for platform, keywords in platform_keywords.items():
            for kw in keywords:
                if kw in query_lower:
                    return platform
        
        return None
    
    async def _platform_search(self, query: str, platform: str, 
                               max_results: int) -> LayerResult:
        """指定平台的定向搜索"""
        result = LayerResult(layer_name=f"{self.name}-{platform}")
        
        # Agent Reach 目前通过 CLI 调用，这里先做模拟实现
        # 实际调用需要适配 Agent Reach 的具体命令格式
        result.results = await self._mock_platform_search(query, platform, max_results)
        result.success = len(result.results) > 0
        
        if result.success:
            result.avg_score = sum(r.score for r in result.results) / len(result.results)
        
        return result
    
    async def _general_search(self, query: str, max_results: int) -> LayerResult:
        """通用搜索（不指定平台）"""
        result = LayerResult(layer_name=self.name)
        
        # 并行搜索多个高相关平台
        platforms = ["xiaohongshu", "bilibili", "twitter", "xueqiu"]
        tasks = [
            self._platform_search(query, p, max_results // len(platforms))
            for p in platforms
        ]
        
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for pr in platform_results:
            if isinstance(pr, LayerResult) and pr.success:
                all_results.extend(pr.results)
        
        result.results = all_results[:max_results]
        result.success = len(all_results) > 0
        
        if result.success:
            result.avg_score = sum(r.score for r in all_results) / len(all_results)
        
        return result
    
    async def _mock_platform_search(self, query: str, platform: str, 
                                    max_results: int) -> List[SearchResult]:
        """
        模拟平台搜索结果（临时实现，待对接真实 Agent Reach CLI）
        
        TODO: 对接 Agent Reach 的真实 CLI 调用接口
        """
        # 这是一个临时的模拟实现，展示框架结构
        # 后续需要根据 Agent Reach 的实际 CLI 接口进行适配
        
        mock_results = []
        
        # 根据平台构造不同的模拟结果
        platform_names = {
            "xiaohongshu": "小红书",
            "bilibili": "B站",
            "twitter": "Twitter",
            "xueqiu": "雪球",
            "linkedin": "领英",
            "zhihu": "知乎",
            "weibo": "微博",
        }
        
        p_name = platform_names.get(platform, platform)
        
        for i in range(min(3, max_results)):
            mock_results.append(SearchResult(
                title=f"[{p_name}] {query} - 相关内容 {i+1}",
                url=f"https://{platform}.com/search?q={query}",
                content=f"来自 {p_name} 的搜索结果摘要",
                source=SearchSource.UNKNOWN,  # 后续可以添加专门的 source 类型
                score=0.65 + i * 0.05,
            ))
        
        return mock_results
    
    def is_available(self) -> bool:
        """检查适配器是否可用"""
        return self.available
