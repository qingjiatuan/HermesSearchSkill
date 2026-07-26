#!/usr/bin/env python3
"""
Unified Research 依赖检查与安装脚本
检查并安装所有必要的依赖技能
"""

import os
import sys
import subprocess
from pathlib import Path


def get_hermes_dir():
    """获取 Hermes 配置目录"""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA")) / "hermes"
    else:
        return Path.home() / ".hermes"


def check_dir(name, path):
    """检查目录是否存在"""
    path = Path(os.path.expandvars(path)).expanduser()
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {name}: {path}")
    return exists


def install_skill(name, git_url, target_dir):
    """安装技能"""
    target_dir = Path(os.path.expandvars(target_dir)).expanduser()
    
    if target_dir.exists():
        print(f"  ⏭️  {name} 已存在，跳过")
        return True
    
    print(f"  📦 正在安装 {name}...")
    
    try:
        subprocess.run(
            ["git", "clone", git_url, str(target_dir)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"  ✅ {name} 安装成功")
        return True
    except Exception as e:
        print(f"  ❌ {name} 安装失败: {e}")
        return False


def main():
    print("=" * 60)
    print("Unified Research - 依赖检查与安装")
    print("=" * 60)
    print()
    
    hermes_dir = get_hermes_dir()
    print(f"Hermes 目录: {hermes_dir}")
    print()
    
    # 定义依赖
    dependencies = [
        {
            "name": "union-search-skill",
            "git_url": "git@github.com:runningZ1/union-search-skill.git",
            "target": f"{hermes_dir}/skills/research/union-search-skill",
            "required": True,
            "description": "多引擎并行搜索（Bing/百度/360/搜狗）"
        },
        {
            "name": "anysearch-skill",
            "git_url": "git@github.com:anysearch-ai/anysearch-skill.git",
            "target": f"{hermes_dir}/plugins/anysearch-skill",
            "required": True,
            "description": "实时搜索 + 垂直领域"
        },
        # Agent Reach 和 Firecrawl 可选
    ]
    
    print("【1】检查现有依赖")
    print()
    
    all_ok = True
    for dep in dependencies:
        print(f"{dep['name']} ({dep['description']})")
        if not check_dir(dep['name'], dep['target']):
            all_ok = False
    print()
    
    if all_ok:
        print("✅ 所有依赖已满足！")
        return
    
    print("【2】安装缺失的依赖")
    print()
    
    for dep in dependencies:
        dep_path = Path(os.path.expandvars(dep['target'])).expanduser()
        if not dep_path.exists():
            install_skill(dep['name'], dep['git_url'], dep['target'])
    
    print()
    print("=" * 60)
    print("安装完成！")
    print("=" * 60)
    print()
    print("⚠️  注意事项:")
    print("  1. AnySearch 需要配置 API Key")
    print("  2. 重启 Hermes 网关: hermes gateway restart")
    print("  3. 运行 python check_deps.py 再次验证")


if __name__ == "__main__":
    main()
