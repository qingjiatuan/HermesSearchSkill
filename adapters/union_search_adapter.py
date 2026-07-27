"""
Union Search 适配器：百度、Bing、360、搜狗 多引擎并行
"""

import asyncio
import subprocess
import json
from typing import List, Optional
from core.models import SearchResult, LayerResult, SearchSource
from core.path_utils import get_union_search_path
from adapters.base_adapter import BaseSearchAdapter


class UnionSearchAdapter(BaseSearchAdapter):
    """Union Search 多引擎适配器"""
    
    name: str = "union-search"
    
    def __init__(self, skill_path: str, config: dict):
        super().__init__(skill_path, config)
        self.union_skill_path = str(get_union_search_path())
        self.engines = [
            ("bing", SearchSource.BING),
            ("baidu", SearchSource.BAIDU),
            ("so360", SearchSource.SO360),
            ("sogou", SearchSource.SOGOU),
        ]
    
    async def search(self, query: str, max_results: int = 10, **kwargs) -> LayerResult:
        """并行搜索多个引擎"""
        result = LayerResult(layer_name=self.name)
        
        try:
            # 并行执行多个引擎搜索
            tasks = [
                self._search_engine(engine_name, source, query, max_results // 2)
                for engine_name, source in self.engines
            ]
            
            engine_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_results = []
            for er in engine_results:
                if isinstance(er, list):
                    all_results.extend(er)
            
            result.results = all_results
            result.success = len(all_results) > 0
            if all_results:
                result.avg_score = sum(r.score for r in all_results) / len(all_results)
            
        except Exception as e:
            result.success = False
            result.error_msg = str(e)
        
        return result
    
    async def _search_engine(self, engine_name: str, source: SearchSource, 
                            query: str, max_results: int) -> List[SearchResult]:
        """搜索单个引擎"""
        loop = asyncio.get_event_loop()
        
        if engine_name == "bing":
            script_path = f"{self.union_skill_path}/scripts/bing/bing_cn_no_api.py"
        elif engine_name == "so360":
            script_path = f"{self.union_skill_path}/scripts/so360/so360_no_api.py"
        elif engine_name == "sogou":
            script_path = f"{self.union_skill_path}/scripts/sogou/sogou_no_api.py"
        else:
            return []  # 暂不支持
        
        try:
            # 同步调用转异步
            proc = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    ["python", script_path, query, "-m", str(max_results)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.union_skill_path
                )
            )
            
            if proc.returncode != 0:
                return []
            
            # 解析输出（简化版：从文本中提取结果）
            return self._parse_output(proc.stdout, source)
            
        except Exception as e:
            return []
    
    def _parse_output(self, output: str, source: SearchSource) -> List[SearchResult]:
        """解析 CLI 输出为搜索结果对象"""
        results = []
        
        # 简单的正则解析（适配 union-search 的输出格式）
        import re
        
        # 匹配编号标题：[1] xxx
        pattern = r'\[(\d+)\]\s*(.+?)\s*\n\s*🔗\s*(https?://\S+)\s*(?:\n\s*📝\s*(.+?))?(?=\n\[|$)'
        matches = re.findall(pattern, output, re.DOTALL)
        
        for match in matches:
            idx, title, url, content = match
            results.append(SearchResult(
                title=title.strip(),
                url=url.strip(),
                content=content.strip() if content else "",
                source=source,
                score=0.5,  # 初始分数，后续融合时重新计算
            ))
        
        return results
    
    def is_available(self) -> bool:
        """检查适配器是否可用"""
        import os
        return os.path.exists(self.union_skill_path)
