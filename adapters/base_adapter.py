"""
适配器基类
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from core.models import SearchResult, LayerResult


class BaseSearchAdapter(ABC):
    """搜索适配器基类"""
    
    name: str = "base"
    
    def __init__(self, skill_path: str, config: dict):
        self.skill_path = skill_path
        self.config = config
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10, **kwargs) -> LayerResult:
        """执行搜索"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查适配器是否可用"""
        pass
