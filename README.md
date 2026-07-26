# Hermes Unified Research Skill

🔬 统一研究技能 - 智能路由 + 分层 fallback + 多源结果融合

## 功能特性

- 🎯 **意图识别路由** - 自动识别查询类型，选择最优搜索组合
- 🏛️ **四层搜索架构** - Union Search → AnySearch → Agent Reach → Firecrawl
- 🧩 **结果融合引擎** - 跨源去重、质量评分、相关性排序
- 📊 **质量评估报告** - 自动识别信息缺口，提供改进建议
- 💰 **成本优先策略** - 优先使用免费资源，不浪费额度

## 四层搜索架构

```
用户查询
    ↓
Layer 1: Union Search (Bing/百度/360/搜狗 4引擎并行) ✅ 完全免费
    ↓ 结果<5条 或 平均分<0.6
Layer 2: AnySearch (实时搜索 + 15+垂直领域) ✅ 免费限额
    ↓ 结果<8条 或 平均分<0.7
Layer 3: Agent Reach (平台定向搜索) ⏳ 待实现
    ↓ 仍有信息缺口 + 用户确认
Layer 4: Firecrawl (深度全文抓取) ⏳ 待实现
    ↓
结果融合层 → 去重 + 评分 + 排序 + 质量报告
```

## 安装方法

### 方式一：Hermes 插件安装（推荐）

```bash
hermes plugins install git@github.com:你的用户名/hermes-unified-research.git --enable
```

### 方式二：手动安装

1. 克隆或下载本仓库
2. 将文件夹复制到 Hermes 技能目录：
   - Windows: `%APPDATA%\hermes\skillsesearch\`
   - Linux/macOS: `~/.hermes/skills/research/`
3. 重启 Hermes 网关：`hermes gateway restart`

### 验证安装

```bash
hermes skills list | grep unified-research
```

## 使用方法

### Python API

```python
import sys
sys.path.append("path/to/unified-research")

from core.unified_research import UnifiedResearch

# 初始化引擎
engine = UnifiedResearch(cost_priority="balanced")  # cost_first / balanced / quality_first

# 执行搜索
result = await engine.search("Python 3.13 新特性", max_results=20)

# 查看结果
print(result.markdown_report)
```

### 配置选项

在 `core/config.yaml` 中可以调整：

```yaml
# 成本策略
cost_priority: balanced  # cost_first (优先免费) / balanced / quality_first (不惜成本)

# Fallback 阈值
fallback:
  layer1_min_results: 5
  layer1_min_score: 0.6
  layer2_min_results: 8
  layer2_min_score: 0.7

# 评分权重
scoring:
  weights:
    relevance: 0.5   # 相关性
    timeliness: 0.3  # 时效性
    authority: 0.2   # 来源权威性
```

## 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| **数据模型** | `core/models.py` | SearchResult / ResearchResult |
| **融合引擎** | `core/fusion.py` | 去重、评分、排序、质量评估 |
| **核心引擎** | `core/unified_research.py` | 路由、分层 fallback、日志 |
| **Union Search** | `adapters/union_search_adapter.py` | 多引擎并行搜索 |
| **AnySearch** | `adapters/anysearch_adapter.py` | 实时搜索 + 垂直领域 |

## 依赖要求

```bash
pip install pyyaml requests
```

可选依赖（按需安装）：
```bash
pip install metapub      # PubMed
pip install pyalex       # OpenAlex
pip install habanero     # Crossref
pip install semanticscholar  # Semantic Scholar
```

## 开发计划

- [ ] Agent Reach 适配器（小红书/B站/Twitter/雪球）
- [ ] Firecrawl 适配器（深度抓取）
- [ ] LLM 意图识别增强
- [ ] CLI 命令行工具
- [ ] 调用统计 + 额度管理
- [ ] 深度调研工作流（多轮自动搜索 + 报告生成）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
