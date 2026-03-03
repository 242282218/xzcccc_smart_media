#!/usr/bin/env python3
"""
技能修复脚本 - 自动修复技能库中的常见问题

修复项：
1. 将 frontmatter 中的 name 与目录名对齐
2. 生成修复报告
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict

SKILLS_DIR = Path(r"C:\Users\24228\Desktop\aaaa\.codex\skills")

class SkillFixer:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.fixes: List[str] = []

    def fix_all(self):
        """执行所有修复"""
        print(f"🔧 开始修复技能库... (dry_run={self.dry_run})\n")

        for skill_dir in SKILLS_DIR.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue
            if skill_dir.name == "_TEMPLATE":
                continue

            self.fix_skill(skill_dir)

        self.print_results()

    def fix_skill(self, skill_dir: Path):
        """修复单个技能"""
        skill_name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            return

        # 读取文件
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析 frontmatter
        match = re.match(r'^(---\s*\n)(.*?)(\n---)', content, re.DOTALL)
        if not match:
            return

        frontmatter_text = match.group(2)
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except:
            return

        # 检查 name 字段
        if 'name' in frontmatter and frontmatter['name'] != skill_name:
            old_name = frontmatter['name']
            frontmatter['name'] = skill_name

            # 重新生成 frontmatter
            new_frontmatter_text = yaml.dump(
                frontmatter,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )

            # 替换内容
            new_content = content.replace(
                match.group(0),
                f"---\n{new_frontmatter_text}---"
            )

            if not self.dry_run:
                with open(skill_md, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.fixes.append(f"✓ [{skill_name}] 已修复 name: '{old_name}' → '{skill_name}'")
            else:
                self.fixes.append(f"  [{skill_name}] 将修复 name: '{old_name}' → '{skill_name}'")

    def print_results(self):
        """输出修复结果"""
        print(f"\n{'='*60}")
        if self.dry_run:
            print(f"预览模式：以下是将要执行的修复（共 {len(self.fixes)} 项）")
        else:
            print(f"修复完成！共执行 {len(self.fixes)} 项修复")
        print(f"{'='*60}\n")

        for fix in self.fixes:
            print(fix)

        if self.dry_run and self.fixes:
            print(f"\n💡 运行 'python {__file__} --apply' 来应用这些修复")

def main():
    import sys
    dry_run = '--apply' not in sys.argv

    fixer = SkillFixer(dry_run=dry_run)
    fixer.fix_all()

if __name__ == "__main__":
    main()
