"""
Unified Research 快速开始示例
"""

import asyncio
import sys
import os

# 添加技能路径
skill_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, skill_path)

from core.unified_research import UnifiedResearch


async def main():
    print("=" * 60)
    print("Unified Research - 统一研究引擎 演示")
    print("=" * 60)
    
    # 初始化引擎
    engine = UnifiedResearch(cost_priority="balanced")
    
    # 打印可用适配器
    print("\n可用适配器:", engine.get_available_adapters())
    
    # 执行搜索（示例，需网络环境）
    # result = await engine.search("运动生理学 肌肉肥大", max_results=20)
    # print(result.markdown_report)
    
    print("\n✅ 引擎初始化成功！")
    print("\n提示: 根据你的网络环境，可能需要配置代理或调整适配器")


if __name__ == "__main__":
    asyncio.run(main())
