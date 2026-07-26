"""
路径工具 - 跨系统自动查找依赖技能路径
"""

import os
import sys
import yaml
from pathlib import Path


def get_hermes_dir():
    """获取 Hermes 配置目录"""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA")) / "hermes"
    else:
        return Path.home() / ".hermes"


def get_skill_path(skill_name: str) -> Path:
    """获取依赖技能的路径（跨平台自动查找）"""
    hermes_dir = get_hermes_dir()
    
    # 可能的路径列表
    possible_paths = [
        # 插件目录
        hermes_dir / "plugins" / skill_name,
        hermes_dir / "plugins" / skill_name.replace("-skill", ""),
        hermes_dir / "plugins" / skill_name.replace("-skill", "-skill"),
        # 技能目录
        hermes_dir / "skills" / "research" / skill_name,
        hermes_dir / "skills" / "research" / skill_name.replace("-skill", ""),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError(
        f"未找到技能: {skill_name}\n"
        f"请运行: python check_deps.py"
    )


def find_script_in_dir(directory: Path, script_name: str) -> Path:
    """在目录中递归查找脚本"""
    for root, dirs, files in os.walk(directory):
        for f in files:
            if script_name in f.lower() and f.endswith('.py'):
                return Path(root) / f
    raise FileNotFoundError(f"在 {directory} 中未找到脚本: {script_name}")


# 常用技能路径快捷方式
def get_union_search_path() -> Path:
    return get_skill_path("union-search-skill")

def get_anysearch_path() -> Path:
    return get_skill_path("anysearch-skill")

def get_agent_reach_path() -> Path:
    return get_skill_path("agent-reach")

def get_firecrawl_path() -> Path:
    return get_skill_path("firecrawl")
