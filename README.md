# Hermes Search Skill - 统一研究技能

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
Layer 3: Agent Reach (平台定向搜索) ✅ 框架已实现（可选安装）
    ↓ 结果<12条 + 用户已安装
Layer 4: Firecrawl (深度全文抓取) ✅ 框架已实现（需显式启用）
    ↓
结果融合层 → 去重 + 评分 + 排序 + 质量报告
```

> ℹ️ **说明**：Agent Reach 和 Firecrawl 的适配器框架已完成，搜索逻辑为模拟实现，后续可根据实际 CLI/API 接口适配。

## 安装方法

### 方式一：Hermes 插件安装（推荐）

#### HTTPS 方式（无需配置 SSH Key，新手推荐）
```bash
hermes plugins install https://github.com/qingjiatuan/HermesSearchSkill.git --enable
```

#### SSH 方式（需要配置 GitHub SSH Key）
```bash
hermes plugins install git@github.com:qingjiatuan/HermesSearchSkill.git --enable
```

### 方式二：手动安装

1. 克隆或下载本仓库
2. 将文件夹复制到 Hermes 技能目录：
   - Windows: `%APPDATA%\hermes\skills
esearch\`
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


## 依赖技能

Unified Research 是一个**调度路由层**，它通过适配器整合以下搜索技能的能力：

| 技能 | 必需 | GitHub 仓库 | 功能 |
|------|------|-------------|------|
| **union-search-skill** | ✅ | [runningZ1/union-search-skill](https://github.com/runningZ1/union-search-skill) | 多引擎并行搜索（Bing/百度/360/搜狗），完全免费 |
| **anysearch-skill** | ✅ | [anysearch-ai/anysearch-skill](https://github.com/anysearch-ai/anysearch-skill) | 实时搜索 + 15+垂直领域，免费限额 |
| **agent-reach** | ⏳ | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | 小红书/B站/Twitter/雪球等平台定向搜索 |
| **firecrawl** | ✅ 框架已实现 | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 深度全文抓取 + 结构化数据提取 |

> 💡 **是的，必须安装这些依赖技能**！Unified Research 本身不包含搜索逻辑，它负责智能路由、分层 fallback 和结果融合。

### 🚀 一键安装所有依赖（推荐）

```bash
# 进入技能目录
cd path/to/HermesSearchSkill

# 运行脚本自动检查并 git clone 所有缺失的依赖
python check_deps.py
```

脚本会自动下载以下仓库到正确的位置：
- union-search-skill → `skills/research/`
- anysearch-skill → `plugins/`

---

### 手动安装（如果一键脚本失败）

```bash
# 1. 安装 union-search-skill
hermes plugins install git@github.com:runningZ1/union-search-skill.git --enable

# 2. 安装 anysearch-skill
hermes plugins install git@github.com:anysearch-ai/anysearch-skill.git --enable

# 3. 可选：安装 agent-reach
hermes plugins install git@github.com:Panniantong/Agent-Reach.git --enable
```

### 配置 AnySearch API Key

编辑 `plugins/anysearch-skill/.env` 文件：

```env
ANYSEARCH_API_KEY=你的API_KEY
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

## ❓ 常见问题

### Q: 必须安装所有依赖技能吗？

**A**: `union-search-skill` 和 `anysearch-skill` 是必须的。
- ✅ union-search-skill 提供基础的免费搜索引擎能力
- ✅ anysearch-skill 提供实时搜索和垂直领域能力
- ⏳ agent-reach 和 firecrawl 是可选的，适配器正在开发中

### Q: 为什么不把这些功能直接整合进来？

**A**: 这是**解耦设计**的考量：
1. **独立迭代**：每个搜索技能可以独立更新、优化、修复
2. **灵活替换**：如果你有更好的搜索方案，可以替换某个适配器而不影响整体
3. **能力复用**：这些技能本身也可以独立使用
4. **渐进增强**：先安装核心依赖，需要时再添加更多能力

### Q: 安装后怎么验证是否工作？

```bash
cd 到技能目录
python example.py
```

如果引擎初始化成功，说明依赖路径配置正确。
