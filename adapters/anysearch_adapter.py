"""
AnySearch 适配器：实时搜索 + 垂直领域 + URL内容提取
"""

import asyncio
import subprocess
from typing import List, Optional
from core.models import SearchResult, LayerResult, SearchSource
from core.path_utils import get_anysearch_path
from adapters.base_adapter import BaseSearchAdapter


class AnySearchAdapter(BaseSearchAdapter):
    """AnySearch 适配器"""
    
    name: str = "anysearch"
    
    def __init__(self, skill_path: str, config: dict):
        super().__init__(skill_path, config)
        self.anysearch_skill_path = str(get_anysearch_path())
    
    async def search(self, query: str, max_results: int = 10, **kwargs) -> LayerResult:
        """执行 AnySearch 搜索"""
        result = LayerResult(layer_name=self.name)
        
        try:
            loop = asyncio.get_event_loop()
            script_path = f"{self.anysearch_skill_path}/scripts/anysearch_cli.py"
            
            proc = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    ["python", script_path, "search", query, "--max_results", str(max_results)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.anysearch_skill_path
                )
            )
            
            if proc.returncode != 0:
                result.success = False
                result.error_msg = proc.stderr or "Unknown error"
                return result
            
            results = self._parse_output(proc.stdout)
            result.results = results
            result.success = len(results) > 0
            if results:
                result.avg_score = sum(r.score for r in results) / len(results)
            
        except Exception as e:
            result.success = False
            result.error_msg = str(e)
        
        return result
    
    async def vertical_search(self, query: str, domain: str, subdomain: Optional[str] = None,
                             max_results: int = 10) -> LayerResult:
        """垂直领域搜索"""
        # TODO: 实现垂直领域搜索
        result = LayerResult(layer_name=f"anysearch-{domain}")
        result.success = False
        result.error_msg = "Vertical search not implemented yet"
        return result
    
    def _parse_output(self, output: str) -> List[SearchResult]:
        """解析 AnySearch CLI 输出"""
        results = []
        import re
        
        # 匹配 AnySearch 输出格式
        pattern = r'###\s*(\d+)\.\s*(.+?)\s*\n- \*\*URL\*\*: (https?://\S+)\s*\n- (.+?)(?=\n###|\Z)'
        matches = re.findall(pattern, output, re.DOTALL)
        
        for match in matches:
            idx, title, url, rest = match
            results.append(SearchResult(
                title=title.strip(),
                url=url.strip(),
                content=rest.strip(),
                source=SearchSource.ANYSEARCH,
                score=0.6,
            ))
        
        return results
    
    def is_available(self) -> bool:
        """检查适配器是否可用"""
        import os
        return os.path.exists(self.anysearch_skill_path)
