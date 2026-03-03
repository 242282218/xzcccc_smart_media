#!/usr/bin/env python3
"""
生成新的 RULES.md 技能分类部分
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List

SKILLS_DIR = Path(r"C:\Users\24228\Desktop\smart_media\.codex\skills")
RULES_FILE = Path(r"C:\Users\24228\Desktop\smart_media\.codex\core\RULES.md")

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
        return {}

def categorize_skill(skill_name: str, description: str) -> tuple:
    """根据技能名称和描述推断分类和强制级别"""
    name_lower = skill_name.lower()
    desc_lower = description.lower()

    # 元编排（强制）
    if 'meta' in name_lower or 'dispatcher' in name_lower:
        return ('meta', '强制（复杂项目）', '接收 PRD 或复杂需求时')

    # 通用开发团队（按需）
    if 'universal' in name_lower:
        return ('meta', '按需', '初学者或需要全流程指导时')

    # 需求分析（强制）
    if 'analyzer' in name_lower:
        return ('analysis', '强制（所有任务）', '对话开始时')
    if 'brainstorm' in name_lower:
        return ('analysis', '强制（创造性任务）', '创造性工作之前')

    # 架构设计（强制）
    if 'tech-stack' in name_lower or 'architect' in name_lower:
        return ('architecture', '强制（新项目/重大迭代）', '技术栈选择或架构设计时')
    if 'api-design' in name_lower:
        return ('architecture', '强制（API 设计）', '设计或评审 API 时')

    # 发现与搜索（按需）
    if 'github' in name_lower and 'search' in name_lower:
        return ('discovery', '按需', '查找开源库或参考案例时')
    if 'find-skills' in name_lower:
        return ('discovery', '按需', '用户询问"如何做某事"时')

    # 前端开发（强制）
    if 'frontend-design' in name_lower:
        return ('frontend', '强制（前端 UI）', '构建 Web 组件、美化 UI 时')
    if 'frontend-code-review' in name_lower:
        return ('frontend', '强制（前端审查）', '审查前端文件时')
    if 'vercel-react' in name_lower:
        return ('frontend', '强制（React）', '编写/审查 React/Next.js 代码时')
    if 'ui-ux-pro-max' in name_lower:
        return ('frontend', '强制（UI/UX）', '规划/设计/优化 UI/UX 时')
    if 'web-design-guidelines' in name_lower:
        return ('frontend', '强制（无障碍审查）', '审查 UI 或检查无障碍时')

    # 后端开发（强制）
    if 'backend' in name_lower:
        if 'database' in name_lower:
            return ('backend', '强制（数据库）', '数据库设计或 SQL 优化时')
        if 'node' in name_lower:
            return ('backend', '强制（Node.js）', 'Node.js 后端开发时')
        if 'python' in name_lower:
            return ('backend', '强制（Python）', 'Python 后端开发时')
    if 'mcp-builder' in name_lower:
        return ('backend', '强制（MCP）', '构建 MCP Server 时')

    # 全栈开发（强制）
    if 'fullstack' in name_lower:
        return ('fullstack', '强制（全栈）', '涉及前后端+数据库的全栈开发时')

    # 测试与自动化（强制）
    if 'test-driven' in name_lower:
        return ('testing', '强制（所有实现）', '实现新功能或修复 Bug 之前')
    if 'playwright' in name_lower:
        return ('testing', '强制（浏览器自动化）', '需要浏览器自动化时')
    if 'browser-use' in name_lower:
        return ('testing', '强制（Web 交互）', '需要 Web 测试或数据提取时')
    if 'webapp-testing' in name_lower:
        return ('testing', '强制（Web 测试）', '测试本地 Web 应用时')

    # 代码审查（强制）
    if 'requesting-code-review' in name_lower:
        return ('review', '强制（所有任务）', '完成任务或代码合并前')

    # 部署与 CI/CD（强制）
    if 'docker-ci' in name_lower:
        return ('deployment', '强制（Docker CI/CD）', '设置 Docker CI/CD 时')
    if 'cloudflare-deploy' in name_lower:
        return ('deployment', '强制（Cloudflare）', '部署到 Cloudflare 时')

    # 安全（强制）
    if 'security' in name_lower:
        return ('security', '强制（安全审查）', '设计认证系统或安全审查时')

    # 办公文档（按需）
    if 'docx' in name_lower:
        return ('office', '按需', '处理 Word 文档时')
    if 'pdf' in name_lower:
        return ('office', '按需', '处理 PDF 文档时')
    if 'xlsx' in name_lower or 'excel' in name_lower:
        return ('office', '按需', '处理 Excel 表格时')

    # 文档查询（强制）
    if 'openai-docs' in name_lower:
        return ('docs', '强制（OpenAI 查询）', '咨询 OpenAI 产品或 API 时')

    # 技能管理（按需）
    if 'codex-skills-sync' in name_lower:
        return ('skill-management', '按需', '同步技能库时')

    # 多智能体编排（强制）
    if 'trae' in name_lower or 'deepagent' in name_lower:
        return ('orchestration', '强制（复杂编排）', '复杂多智能体编排时')

    return ('other', '按需', '特定场景')

def scan_skills():
    """扫描所有技能并分类"""
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
        'security': [],
        'office': [],
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

        category, mandatory, trigger = categorize_skill(skill_name, description)
        skills_by_category[category].append({
            'name': skill_name,
            'description': description,
            'mandatory': mandatory,
            'trigger': trigger
        })

    return skills_by_category

def generate_rules_skills_section(skills_by_category: Dict) -> str:
    """生成 RULES.md 的技能分类部分"""
    category_info = {
        'meta': ('元编排与调度', '复杂项目或需要全流程指导时'),
        'analysis': ('需求分析', '任务开始时'),
        'architecture': ('架构设计', '新项目或重大迭代时'),
        'discovery': ('发现与搜索', '查找资源或技能时'),
        'frontend': ('前端开发', '涉及前端必须触发'),
        'backend': ('后端开发', '涉及后端必须触发'),
        'fullstack': ('全栈开发', '涉及全栈必须触发'),
        'testing': ('测试与自动化', '涉及测试必须触发'),
        'review': ('代码审查', '完成后必须触发'),
        'deployment': ('部署与 CI/CD', '涉及部署必须触发'),
        'security': ('安全', '涉及安全必须触发'),
        'office': ('办公文档', '处理文档时'),
        'docs': ('文档查询', '查询文档时'),
        'skill-management': ('技能管理', '管理技能时'),
        'orchestration': ('多智能体编排', '复杂编排时'),
        'other': ('其他', '特定场景')
    }

    output = []
    output.append("### 技能分类与触发时机\n")
    output.append("> **技能按功能领域组织，标记强制级别和触发条件。**\n")

    for category, (title, desc) in category_info.items():
        skills = skills_by_category.get(category, [])
        if not skills:
            continue

        output.append(f"\n#### {title}（{desc}）\n")
        output.append("\n| 技能 | 触发条件 | 强制级别 |")
        output.append("\n|------|----------|----------|")

        for skill in sorted(skills, key=lambda x: x['name']):
            name = skill['name']
            trigger = skill['trigger']
            mandatory = skill['mandatory']
            output.append(f"\n| **{name}** | {trigger} | {mandatory} |")

        output.append("\n")

    return ''.join(output)

def update_rules_file():
    """更新 RULES.md 文件"""
    print("🔍 扫描技能目录...")
    skills_by_category = scan_skills()

    total_skills = sum(len(skills) for skills in skills_by_category.values())
    print(f"✅ 共扫描到 {total_skills} 个技能\n")

    print("📝 生成技能分类部分...")
    new_skills_section = generate_rules_skills_section(skills_by_category)

    print("📄 读取 RULES.md...")
    with open(RULES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到技能分类部分的开始和结束
    start_marker = "### 技能分类与触发时机"
    end_marker = "## 七、特定领域 / 工作流"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print("❌ 错误：找不到标记位置")
        return False

    # 替换内容
    new_content = (
        content[:start_idx] +
        new_skills_section +
        content[end_idx:]
    )

    print("💾 写入 RULES.md...")
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ RULES.md 已更新！")
    return True

if __name__ == "__main__":
    update_rules_file()
