"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class SearchSource(str, Enum):
    """搜索来源枚举"""
    BING = "bing"
    BAIDU = "baidu"
    SOGOU = "sogou"
    SO360 = "so360"
    XIAOHONGSHU = "xiaohongshu"
    BILIBILI = "bilibili"
    TWITTER = "twitter"
    REDDIT = "reddit"
    V2EX = "v2ex"
    GITHUB = "github"
    XUEQIU = "xueqiu"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    ANYSEARCH = "anysearch"
    FIRECRAWL = "firecrawl"
    UNKNOWN = "unknown"


@dataclass
class SearchResult:
    """单条搜索结果"""
    title: str
    url: str
    content: str = ""
    source: SearchSource = SearchSource.UNKNOWN
    score: float = 0.0  # 相关性评分 0-1
    published_at: Optional[str] = None
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.source, str):
            try:
                self.source = SearchSource(self.source.lower())
            except ValueError:
                self.source = SearchSource.UNKNOWN
    
    @property
    def id(self) -> str:
        """生成唯一ID用于去重"""
        import hashlib
        content = f"{self.url}|{self.title[:50]}".lower()
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    @property
    def domain(self) -> str:
        """提取域名"""
        import re
        match = re.search(r"https?://(?:www\.)?([^/]+)", self.url)
        return match.group(1) if match else ""


@dataclass
class ResearchResult:
    """完整研究结果"""
    query: str
    total_results: int = 0
    sources: List[SearchSource] = field(default_factory=list)
    results: List[SearchResult] = field(default_factory=list)
    quality_score: float = 0.0  # 整体质量评分 0-1
    info_gaps: List[str] = field(default_factory=list)  # 信息缺口
    execution_log: List[str] = field(default_factory=list)
    layers_used: List[str] = field(default_factory=list)
    
    @property
    def markdown_report(self) -> str:
        """生成 Markdown 报告"""
        lines = [f"# 研究报告：{self.query}", ""]
        
        # 执行摘要
        lines.append("## 执行摘要")
        lines.append(f"- 总结果数：{self.total_results}")
        lines.append(f"- 使用来源：{', '.join(s.value for s in self.sources)}")
        lines.append(f"- 使用层级：{' → '.join(self.layers_used)}")
        lines.append(f"- 质量评分：{self.quality_score:.1%}")
        lines.append("")
        
        # 信息缺口
        if self.info_gaps:
            lines.append("## ⚠️ 信息缺口")
            for gap in self.info_gaps:
                lines.append(f"- {gap}")
            lines.append("")
        
        # Top 结果
        lines.append("## Top 搜索结果")
        lines.append("")
        for i, r in enumerate(sorted(self.results, key=lambda x: x.score, reverse=True)[:15], 1):
            lines.append(f"### {i}. {r.title}")
            lines.append(f"- **来源**：{r.source.value}")
            lines.append(f"- **评分**：{r.score:.1%}")
            lines.append(f"- **链接**：[{r.domain}]({r.url})")
            if r.published_at:
                lines.append(f"- **发布时间**：{r.published_at}")
            if r.content:
                lines.append(f"- **摘要**：{r.content[:200]}...")
            lines.append("")
        
        # 执行日志
        lines.append("## 执行日志")
        for log in self.execution_log:
            lines.append(f"- {log}")
        
        return "\n".join(lines)


@dataclass
class LayerResult:
    """单层搜索结果"""
    layer_name: str
    results: List[SearchResult] = field(default_factory=list)
    avg_score: float = 0.0
    success: bool = False
    error_msg: str = ""
