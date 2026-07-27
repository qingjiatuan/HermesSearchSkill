"""
统一研究引擎：意图路由 + 分层 fallback + 结果融合
"""

import asyncio
import yaml
import os
from typing import List, Optional, Dict
from pathlib import Path

from core.models import SearchResult, ResearchResult, LayerResult
from core.fusion import ResultFusionEngine


class UnifiedResearch:
    """统一研究引擎"""
    
    def __init__(self, config_path: Optional[str] = None, cost_priority: str = "balanced"):
        # 加载配置
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        # 覆盖成本优先级
        if cost_priority != "balanced":
            self.config["cost_priority"] = cost_priority
        
        # 初始化融合引擎
        self.fusion = ResultFusionEngine(self.config)

        # 执行日志(须在 _init_adapters 之前,因为 _log 会被调用)
        self.execution_log: List[str] = []

        # 初始化适配器
        self.adapters: Dict[str, BaseSearchAdapter] = {}
        self._init_adapters()
    
    def _init_adapters(self):
        # 动态导入适配器，避免循环依赖
        from adapters.union_search_adapter import UnionSearchAdapter
        from adapters.anysearch_adapter import AnySearchAdapter
        """初始化所有可用的适配器"""
        skill_path = Path(__file__).parent.parent
        
        # Union Search（第1层：免费）
        union = UnionSearchAdapter(str(skill_path), self.config)
        if union.is_available():
            self.adapters["union-search"] = union
            self._log(f"✓ 已加载 Union Search 适配器")
        else:
            self._log(f"✗ Union Search 不可用")
        
        # AnySearch（第2层：免费限额）
        anysearch = AnySearchAdapter(str(skill_path), self.config)
        if anysearch.is_available():
            self.adapters["anysearch"] = anysearch
            self._log(f"✓ 已加载 AnySearch 适配器")
        else:
            self._log(f"✗ AnySearch 不可用")
        
        # TODO: Agent Reach、Firecrawl 适配器
    
    async def search(self, query: str, max_results: int = 20, 
                    enable_firecrawl: bool = False) -> ResearchResult:
        """执行搜索研究"""
        self._log(f"开始搜索: {query}")
        self._log(f"成本策略: {self.config['cost_priority']}")
        
        all_results: List[SearchResult] = []
        layers_used: List[str] = []
        
        # ========== 第1层：Union Search（免费） ==========
        if "union-search" in self.adapters:
            self._log("执行第1层：Union Search (多引擎并行)")
            layer1 = await self.adapters["union-search"].search(
                query, 
                max_results=min(max_results // 2, 15)
            )
            
            if layer1.success:
                all_results.extend(layer1.results)
                layers_used.append("union-search")
                self._log(f"第1层完成：获取 {len(layer1.results)} 条结果")
                
                # 检查是否需要进入下一层
                need_layer2 = self._need_fallback(
                    all_results, 
                    self.config["fallback"]["layer1_min_results"],
                    self.config["fallback"]["layer1_min_score"]
                )
                
                if not need_layer2:
                    self._log("第1层结果达标，停止 fallback")
                else:
                    self._log(f"第1层结果不足（{len(all_results)}条），继续第2层")
            else:
                self._log(f"第1层失败: {layer1.error_msg}")
        
        # ========== 第2层：AnySearch ==========
        if "anysearch" in self.adapters and len(all_results) < self.config["fallback"]["layer2_min_results"]:
            self._log("执行第2层：AnySearch 实时搜索")
            layer2 = await self.adapters["anysearch"].search(
                query,
                max_results=min(max_results // 2, 10)
            )
            
            if layer2.success:
                all_results.extend(layer2.results)
                layers_used.append("anysearch")
                self._log(f"第2层完成：获取 {len(layer2.results)} 条结果")
        
        # TODO: 第3层：Agent Reach（平台定向）
        # TODO: 第4层：Firecrawl（深度抓取）
        
        # ========== 结果融合 ==========
        self._log(f"共获取 {len(all_results)} 条结果，开始融合处理...")
        final_result = self.fusion.fuse(all_results, query)
        
        # 补充元数据
        final_result.execution_log = self.execution_log.copy()
        final_result.layers_used = layers_used
        
        self._log(f"融合完成：{final_result.total_results} 条唯一结果，质量评分 {final_result.quality_score:.1%}")
        
        return final_result
    
    def _need_fallback(self, results: List[SearchResult], min_count: int, min_score: float) -> bool:
        """判断是否需要 fallback 到下一层"""
        if len(results) < min_count:
            return True
        
        # 计算 Top 结果的平均分数
        top_results = sorted(results, key=lambda x: x.score, reverse=True)[:5]
        avg_score = sum(r.score for r in top_results) / len(top_results)
        
        return avg_score < min_score
    
    def _log(self, message: str):
        """记录执行日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.execution_log.append(f"[{timestamp}] {message}")
    
    def get_available_adapters(self) -> List[str]:
        """获取可用适配器列表"""
        return list(self.adapters.keys())
