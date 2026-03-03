#!/usr/bin/env python3
"""
扫描技能目录并生成技能分类信息
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List

SKILLS_DIR = Path(r"C:\Users\24228\Desktop\smart_media\.codex\skills")

def parse_frontmatter(skill_md: Path) -> Dict:
    """解析 SKILL.md 的 frontmatter"""
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}

        frontmatter_text = match.group(1)
        return yaml.safe_load(frontmatter_text)
    except Exception as e:
        print(f"警告：解析 {skill_md} 失败: {e}")
        return {}

def categorize_skill(skill_name: str, description: str) -> str:
    """根据技能名称和描述推断分类"""
    name_lower = skill_name.lower()
    desc_lower = description.lower()

    # 元编排
    if 'meta' in name_lower or 'dispatcher' in name_lower or 'universal' in name_lower:
        return 'meta'

    # 需求分析
    if 'analyzer' in name_lower or 'brainstorm' in name_lower:
        return 'analysis'

    # 架构设计
    if 'architect' in name_lower or 'tech-stack' in name_lower or 'api-design' in name_lower:
        return 'architecture'

    # 发现与搜索
    if 'discovery' in name_lower or 'search' in name_lower or 'find' in name_lower:
        return 'discovery'

    # 前端开发
    if any(x in name_lower for x in ['frontend', 'ui-ux', 'web-design', 'vercel', 'react']):
        return 'frontend'

    # 后端开发
    if 'backend' in name_lower or 'database' in name_lower or 'mcp' in name_lower:
        return 'backend'

    # 全栈开发
    if 'fullstack' in name_lower:
        return 'fullstack'

    # 测试
    if 'test' in name_lower or 'playwright' in name_lower or 'browser' in name_lower:
        return 'testing'

    # 代码审查
    if 'review' in name_lower:
        return 'review'

    # 部署
    if 'deploy' in name_lower or 'docker' in name_lower or 'ci' in name_lower or 'cloudflare' in name_lower:
        return 'deployment'

    # 办公文档
    if 'office' in name_lower or 'docx' in name_lower or 'excel' in name_lower or 'pdf' in name_lower:
        return 'office'

    # 安全
    if 'security' in name_lower:
        return 'security'

    # 文档查询
    if 'docs' in name_lower or 'openai' in name_lower:
        return 'docs'

    # 技能管理
    if 'skill' in name_lower or 'codex' in name_lower:
        return 'skill-management'

    # 多智能体编排
    if 'trae' in name_lower or 'deepagent' in name_lower:
        return 'orchestration'

    return 'other'

def scan_skills():
    """扫描所有技能"""
    skills_by_category = {
        'meta': [],
        'analysis': [],
        'architecture': [],
        'discovery': [],
        'frontend': [],
        'backend': [],
        'fullstack': [],
        'testing': [],
        'review': [],
        'deployment': [],
        'office': [],
        'security': [],
        'docs': [],
        'skill-management': [],
        'orchestration': [],
        'other': []
    }

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith('.') or skill_dir.name == '_TEMPLATE':
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        frontmatter = parse_frontmatter(skill_md)
        if not frontmatter:
            continue

        skill_name = frontmatter.get('name', skill_dir.name)
        description = frontmatter.get('description', '')

        category = categorize_skill(skill_name, description)
        skills_by_category[category].append({
            'name': skill_name,
            'description': description
        })

    return skills_by_category

def print_skills_by_category(skills_by_category: Dict):
    """打印技能分类"""
    category_names = {
        'meta': '元编排（Meta）',
        'analysis': '需求分析（Analysis）',
        'architecture': '架构设计（Architecture）',
        'discovery': '发现与搜索（Discovery）',
        'frontend': '前端开发（Frontend）',
        'backend': '后端开发（Backend）',
        'fullstack': '全栈开发（Fullstack）',
        'testing': '测试与自动化（Testing）',
        'review': '代码审查（Review）',
        'deployment': '部署与 CI/CD（Deployment）',
        'office': '办公文档（Office）',
        'security': '安全（Security）',
        'docs': '文档查询（Docs）',
        'skill-management': '技能管理（Skill Management）',
        'orchestration': '多智能体编排（Orchestration）',
        'other': '其他（Other）'
    }

    for category, skills in skills_by_category.items():
        if not skills:
            continue

        print(f"\n### {category_names[category]}")
        print(f"\n共 {len(skills)} 个技能：\n")
        print("| 技能 | 描述 |")
        print("|------|------|")
        for skill in sorted(skills, key=lambda x: x['name']):
            desc = skill['description'][:80] + '...' if len(skill['description']) > 80 else skill['description']
            print(f"| **{skill['name']}** | {desc} |")

if __name__ == "__main__":
    print("🔍 扫描技能目录...\n")
    skills_by_category = scan_skills()

    total_skills = sum(len(skills) for skills in skills_by_category.values())
    print(f"✅ 共扫描到 {total_skills} 个技能\n")
    print("="*80)

    print_skills_by_category(skills_by_category)
