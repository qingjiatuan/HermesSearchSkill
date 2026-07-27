"""
Union Search 适配器：百度、Bing、360、搜狗 多引擎并行
"""

import asyncio
import subprocess
import json
import re
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
        elif engine_name == "baidu":
            script_path = f"{self.union_skill_path}/scripts/baidu/baidu_no_api.py"
        elif engine_name == "so360":
            script_path = f"{self.union_skill_path}/scripts/so360/so360_no_api.py"
        elif engine_name == "sogou":
            script_path = f"{self.union_skill_path}/scripts/sogou/sogou_no_api.py"
        else:
            return []  # 暂不支持

        try:
            # 同步调用转异步
            # 用 sys.executable 确保使用和适配器相同的 Python 解释器
            import sys as _sys
            proc = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    [_sys.executable, script_path, query, "-m", str(max_results)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.union_skill_path
                )
            )

            if proc.returncode != 0:
                return []

            # 解析输出
            return self._parse_output(proc.stdout, source)

        except Exception as e:
            return []

    def _parse_output(self, output: str, source: SearchSource) -> List[SearchResult]:
        """
        解析 CLI 输出为搜索结果对象，兼容各引擎不同输出格式。

        各引擎输出格式示例：
        - bing:     [N] title\n    🔗 https://url\n    📝 content
        - baidu:    [N] title\n    🔗 https://baidu.com/link?url=...
        - so360:    [N] title\n    🔗 https://so.com/link?m=...
        - sogou:    [N] title\n    🔗 /link?url=...  (相对路径，需补全)
        """
        results = []
        SOGOU_BASE = "https://www.sogou.com"

        # 按 [N] 编号切分结果块（兼容不同分隔格式）
        blocks = re.split(r'\n\s*(?=\[\d+\])', output)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # 提取标题：紧跟 [N] 之后的内容，到换行为止
            title_match = re.match(r'\[\d+\]\s*(.+?)(?:\n|$)', block)
            if not title_match:
                continue
            title = title_match.group(1).strip()

            # 提取 URL：🔗 开头的行，支持多种格式
            url_match = re.search(r'🔗\s*(https?://\S+|//\S+|/\S+)', block)
            url = url_match.group(1).strip() if url_match else ""
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = SOGOU_BASE + url

            # 提取内容摘要：📝 开头的行（可选，有些引擎没有）
            content_match = re.search(r'📝\s*(.+?)(?:\n|$)', block)
            content = content_match.group(1).strip() if content_match else ""

            if title and url:
                results.append(SearchResult(
                    title=title,
                    url=url,
                    content=content,
                    source=source,
                    score=0.5,
                ))

        return results

    def is_available(self) -> bool:
        """检查适配器是否可用"""
        import os
        return os.path.exists(self.union_skill_path)