---
name: unified-research
description: >
  [GitHub: qingjiatuan/HermesSearchSkill](https://github.com/qingjiatuan/HermesSearchSkill)
  统一研究入口，智能路由 + 分层 fallback + 多源结果融合。自动选择最优搜索组合：
  union-search (免费多引擎) → agent-reach (平台定向) → anysearch (垂直领域) → firecrawl (深度抓取)。
  单次查询自动完成多源互补、去重、相关性排序，输出高质量研究结果。
triggers:
  - research: 调研/研究/全网调研/深度调研/帮我调研/research
  - search: 搜索/查一下/找一下/搜一下/search/查询
  - deep: 深度搜索/全站抓取/全文提取/爬取
metadata:
  author: Hermes Agent
  version: 1.0.0
  depends: [union-search-skill, agent-reach, anysearch, firecrawl]
---

# 🔬 统一研究引擎

## 核心架构

```
用户查询 → 意图识别 & 路由 → 分层搜索 → 结果融合 → 质量评估 → 最终输出
```

## 快速开始

### 基础用法
```python
from core.unified_research import UnifiedResearch

engine = UnifiedResearch()
result = await engine.search("AI Agent 最新发展趋势", max_results=20)
print(result.markdown_report)
```

### 配置优先级
```python
engine = UnifiedResearch(
    cost_priority="balanced",  # cost_first / balanced / quality_first
    enable_firecrawl=True,
    max_free_calls=5,
)
```

## 路由规则（自动匹配）

| 关键词 | 路由目标 |
|--------|----------|
| 小红书/xhs/小红书 | agent-reach → 小红书 |
| B站/bilibili/哔哩哔哩 | agent-reach → B站 |
| 推特/twitter/x.com | agent-reach → Twitter |
| 股票/行情/雪球/xueqiu | agent-reach → 雪球 + anysearch 金融 |
| github/代码/仓库/issue | agent-reach → GitHub + union-search GitHub |
| 学术/论文/专利/医疗 | anysearch 垂直领域 |
| 全文/爬取/全站/抓取 | firecrawl 深度抓取 |
| 其他通用查询 | union-search (3引擎并行) → anysearch 补充 |

## 分层 Fallback 逻辑

```
第1层：union-search (百度/Bing/360 并行) → 完全免费无限额
    ↓ 相关性 < 0.6 或 结果 < 5条
第2层：agent-reach 平台定向搜索 → 免费（需配置登录态）
    ↓ 相关性 < 0.7 或 结果 < 8条
第3层：anysearch 实时搜索 + 垂直领域 → 免费限额
    ↓ 仍有信息缺口 + 用户确认
第4层：firecrawl 目标站点深度抓取 → 付费额度
```

## 结果融合能力

- ✅ 多源结果去重（URL 去重 + 语义去重）
- ✅ 相关性评分（TF-IDF + 关键词匹配）
- ✅ 跨平台结果排序（按时间、热度、相关性加权）
- ✅ 质量评估（信息完整性、时效性、来源权威性）
- ✅ 自动生成研究报告（Markdown 格式）

## 额度保护

- **免费额度优先**：付费技能只在免费层结果不达标时启用
- **调用阈值**：firecrawl 默认关闭，需显式启用
- **用户确认**：大额调用（>10 页 firecrawl）前需确认
- **使用统计**：每次调用输出各技能消耗情况

## 配置文件

配置文件路径: `core/config.yaml`

```yaml
cost_priority: balanced  # cost_first / balanced / quality_first

routing:
  enable_platform_routing: true
  enable_intent_recognition: true

fallback:
  layer1_min_results: 5
  layer1_min_score: 0.6
  layer2_min_results: 8
  layer2_min_score: 0.7
  layer3_min_results: 10
  layer3_min_score: 0.8

limits:
  max_free_calls_per_query: 5
  enable_firecrawl_by_default: false
  firecrawl_max_pages_per_query: 10

scoring:
  weights:
    relevance: 0.5
    timeliness: 0.3
    authority: 0.2
```

## 适配的技能

| 技能 | 状态 | 适配器 |
|------|------|--------|
| union-search-skill | ✅ 已集成 | `adapters/union_search_adapter.py` |
| agent-reach | ✅ 已集成 | `adapters/agent_reach_adapter.py` |
| anysearch | ✅ 已集成 | `adapters/anysearch_adapter.py` |
| firecrawl | ⚠️ 可选（默认关闭） | `adapters/firecrawl_adapter.py` |

## 使用示例

### 通用搜索
```python
result = engine.search("Python 3.13 新特性")
```

### 特定平台搜索
```python
result = engine.search("小红书上的 AI Agent 工具推荐")
# 自动路由到 agent-reach 小红书
```

### 深度调研模式
```python
result = engine.deep_research(
    "2024 年大模型推理优化技术",
    dimensions=["技术方案", "性能对比", "开源项目", "产业应用"],
    time_range="3个月"
)
```

## 输出格式

```python
ResearchResult(
    query="查询关键词",
    total_results=25,
    sources=["bing", "baidu", "github", "anysearch"],
    results=[
        SearchResult(
            title="标题",
            url="https://...",
            content="摘要内容",
            source="bing",
            score=0.92,
            published_at="2024-07-20"
        ),
        ...
    ],
    quality_score=0.85,
    info_gaps=["技术细节对比不足", "缺少国内厂商案例"],
    markdown_report="# 研究报告...",
)
```
