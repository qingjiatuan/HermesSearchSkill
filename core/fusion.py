"""
结果融合引擎：去重、评分、排序、质量评估
"""

import re
from typing import List, Set
from collections import defaultdict
from datetime import datetime
from core.models import SearchResult, ResearchResult


class ResultFusionEngine:
    """结果融合引擎"""
    
    def __init__(self, config: dict):
        self.config = config
        self.weights = config["scoring"]["weights"]
        self.authority_scores = config["scoring"]["authority_scores"]
    
    def fuse(self, all_results: List[SearchResult], query: str) -> ResearchResult:
        """融合所有搜索结果"""
        # 1. 去重
        unique_results = self._deduplicate(all_results)
        
        # 2. 计算评分
        scored_results = self._score_results(unique_results, query)
        
        # 3. 排序
        sorted_results = sorted(scored_results, key=lambda x: x.score, reverse=True)
        
        # 4. 质量评估
        quality_score = self._assess_quality(sorted_results)
        
        # 5. 识别信息缺口
        info_gaps = self._identify_gaps(sorted_results, query)
        
        # 6. 收集来源
        sources = list({r.source for r in sorted_results})
        
        return ResearchResult(
            query=query,
            total_results=len(sorted_results),
            sources=sources,
            results=sorted_results,
            quality_score=quality_score,
            info_gaps=info_gaps,
        )
    
    def _deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重：URL去重 + 标题语义去重"""
        seen_urls: Set[str] = set()
        seen_titles: Set[str] = set()
        unique = []
        
        for r in results:
            # URL 去重
            if r.url in seen_urls:
                continue
            seen_urls.add(r.url)
            
            # 标题语义去重（简化版）
            title_key = self._normalize_title(r.title)
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            
            unique.append(r)
        
        return unique
    
    def _normalize_title(self, title: str) -> str:
        """标准化标题用于去重"""
        # 移除特殊字符，小写，取前30字符
        t = re.sub(r"[^\w\u4e00-\u9fff]", "", title.lower())
        return t[:30]
    
    def _score_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """计算每条结果的综合评分"""
        query_keywords = self._extract_keywords(query)
        
        for r in results:
            # 1. 相关性评分
            relevance = self._calc_relevance(r, query_keywords)
            
            # 2. 时效性评分
            timeliness = self._calc_timeliness(r)
            
            # 3. 来源权威性评分
            authority = self.authority_scores.get(r.source.value, 0.7)
            
            # 4. 加权综合
            r.score = (
                relevance * self.weights["relevance"] +
                timeliness * self.weights["timeliness"] +
                authority * self.weights["authority"]
            )
        
        return results
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取查询关键词（简化版）"""
        # 移除常见停用词
        stopwords = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        words = re.findall(r"[\w\u4e00-\u9fff]{2,}", query)
        return [w for w in words if w not in stopwords]
    
    def _calc_relevance(self, result: SearchResult, keywords: List[str]) -> float:
        """计算相关性评分（关键词匹配）"""
        if not keywords:
            return 0.5
        
        text = (result.title + " " + result.content).lower()
        matches = sum(1 for kw in keywords if kw.lower() in text)
        return min(1.0, matches / len(keywords) * 1.2)  # 1.2 是宽松系数
    
    def _calc_timeliness(self, result: SearchResult) -> float:
        """计算时效性评分"""
        if not result.published_at:
            return 0.5  # 默认中等
        
        try:
            # 解析日期
            if isinstance(result.published_at, str):
                from datetime import datetime
                pub_date = datetime.fromisoformat(result.published_at.replace("Z", "+00:00"))
            else:
                pub_date = result.published_at
            
            days_ago = (datetime.now() - pub_date).days
            
            # 越新分数越高
            if days_ago <= 7:
                return 1.0
            elif days_ago <= 30:
                return 0.9
            elif days_ago <= 90:
                return 0.75
            elif days_ago <= 180:
                return 0.6
            elif days_ago <= 365:
                return 0.45
            else:
                return 0.3
        except:
            return 0.5
    
    def _assess_quality(self, results: List[SearchResult]) -> float:
        """评估整体结果质量"""
        if not results:
            return 0.0
        
        # Top N 的平均分数
        top_n = min(10, len(results))
        top_scores = [r.score for r in results[:top_n]]
        avg_top_score = sum(top_scores) / len(top_scores)
        
        # 结果数量加成
        count_bonus = min(0.1, len(results) / 100)
        
        # 来源多样性加成
        sources = {r.source for r in results}
        diversity_bonus = min(0.1, len(sources) / 10)
        
        return min(1.0, avg_top_score * 0.8 + count_bonus + diversity_bonus)
    
    def _identify_gaps(self, results: List[SearchResult], query: str) -> List[str]:
        """识别信息缺口"""
        gaps = []
        
        if len(results) < 5:
            gaps.append(f"结果数量较少（{len(results)} 条），可能需要补充搜索")
        
        if results:
            avg_score = sum(r.score for r in results) / len(results)
            if avg_score < 0.5:
                gaps.append("整体相关性较低，建议调整关键词或扩大搜索范围")
            
            # 检查来源多样性
            sources = {r.source for r in results}
            if len(sources) <= 2:
                gaps.append(f"来源较为单一（{', '.join(s.value for s in sources)}），建议尝试多平台搜索")
        
        # 高分结果占比
        high_score = [r for r in results if r.score >= 0.7]
        if len(high_score) < 3:
            gaps.append("高相关性结果不足，可能需要深度抓取")
        
        return gaps
