"""
Firecrawl 适配器 - 深度全文抓取 + 结构化数据提取
"""

import asyncio
import subprocess
from typing import List, Optional, Dict, Any
from core.models import SearchResult, LayerResult, SearchSource
from core.path_utils import get_firecrawl_path
from adapters.base_adapter import BaseSearchAdapter


class FirecrawlAdapter(BaseSearchAdapter):
    """Firecrawl 深度抓取适配器"""
    
    name: str = "firecrawl"
    
    def __init__(self, skill_path: str, config: dict):
        super().__init__(skill_path, config)
        try:
            self.firecrawl_path = str(get_firecrawl_path())
            self.available = True
        except FileNotFoundError:
            self.available = False
        
        # Firecrawl 配置
        self.api_key = None
        self.api_url = "https://api.firecrawl.dev"
    
    async def search(self, query: str, max_results: int = 10,
                    enable_full_content: bool = False, **kwargs) -> LayerResult:
        """
        Firecrawl 搜索 + 抓取
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            enable_full_content: 是否启用全文抓取
        """
        result = LayerResult(layer_name=self.name)
        
        if not self.available:
            result.success = False
            result.error_msg = "Firecrawl 未安装，请运行: python check_deps.py"
            return result
        
        # Firecrawl 主要是抓取工具，搜索能力较弱
        # 这里实现为：先搜索，然后对 Top N 结果进行全文抓取
        
        # 1. 先搜索（使用 Firecrawl 的 search 端点）
        search_results = await self._firecrawl_search(query, max_results)
        
        if not search_results:
            result.success = False
            result.error_msg = "Firecrawl 搜索无结果"
            return result
        
        # 2. 如果启用全文抓取，对 Top 结果进行内容提取
        if enable_full_content and len(search_results) > 0:
            top_urls = [r.url for r in search_results[:3]]  # 只抓取前3个的全文
            full_contents = await asyncio.gather(
                *[self._scrape_url(url) for url in top_urls],
                return_exceptions=True
            )
            
            # 更新结果内容
            for r, content in zip(search_results[:3], full_contents):
                if isinstance(content, str) and content:
                    r.content = content
        
        result.results = search_results
        result.success = len(search_results) > 0
        
        if result.success:
            result.avg_score = sum(r.score for r in search_results) / len(search_results)
        
        return result
    
    async def _firecrawl_search(self, query: str, max_results: int) -> List[SearchResult]:
        """调用 Firecrawl 搜索 API"""
        # 模拟实现，展示框架结构
        # 后续需要对接 Firecrawl 的真实 API 或 CLI
        
        mock_results = []
        
        for i in range(min(2, max_results)):
            mock_results.append(SearchResult(
                title=f"[Firecrawl] {query} - 深度抓取结果 {i+1}",
                url=f"https://example.com/page{i+1}",
                content=f"Firecrawl 抓取的完整页面内容（经过清理的 Markdown 格式）",
                source=SearchSource.UNKNOWN,
                score=0.85,  # Firecrawl 抓取结果质量高
            ))
        
        return mock_results
    
    async def _scrape_url(self, url: str) -> str:
        """抓取单个 URL 的完整内容"""
        # 模拟抓取延迟
        await asyncio.sleep(0.5)
        
        return f"[{url}] 的完整页面内容（清理后的 Markdown 格式）...\n" * 10
    
    async def crawl_site(self, url: str, max_pages: int = 10) -> Dict[str, Any]:
        """整站爬取"""
        # TODO: 实现整站爬取功能
        return {"url": url, "pages_crawled": max_pages, "status": "in_progress"}
    
    async def extract_structured_data(self, url: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """提取结构化数据"""
        # TODO: 实现结构化数据提取（基于 LLM 的 schema 提取）
        return {"url": url, "extracted_data": {}}
    
    def is_available(self) -> bool:
        """检查适配器是否可用"""
        return self.available
