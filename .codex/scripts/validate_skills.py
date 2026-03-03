#!/usr/bin/env python3
"""
技能验证脚本 - 检查 .codex/skills 目录中的技能是否符合规范

检查项：
1. 所有 SKILL.md 必须有 name 和 description
2. description 必须是中文（如果在中文环境）
3. 外部技能必须有 .upstream.yaml
4. 技能名称与目录名一致
5. RULES.md 中引用的技能都存在
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Tuple

# 配置
SKILLS_DIR = Path(r"C:\Users\24228\Desktop\aaaa\.codex\skills")
RULES_FILE = Path(r"C:\Users\24228\Desktop\aaaa\.codex\core\RULES.md")

class SkillValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.skills_found: List[str] = []

    def validate_all(self) -> bool:
        """执行所有验证"""
        print("🔍 开始验证技能库...\n")

        # 1. 验证技能目录结构
        self.validate_skills_directory()

        # 2. 验证 RULES.md 中的技能引用
        self.validate_rules_references()

        # 3. 输出结果
        return self.print_results()

    def validate_skills_directory(self):
        """验证技能目录"""
        if not SKILLS_DIR.exists():
            self.errors.append(f"技能目录不存在: {SKILLS_DIR}")
            return

        for skill_dir in SKILLS_DIR.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue

            if skill_dir.name == "_TEMPLATE":
                continue

            self.validate_skill(skill_dir)

    def validate_skill(self, skill_dir: Path):
        """验证单个技能"""
        skill_name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        upstream_yaml = skill_dir / ".upstream.yaml"

        # 检查 SKILL.md 是否存在
        if not skill_md.exists():
            self.errors.append(f"[{skill_name}] 缺少 SKILL.md 文件")
            return

        # 解析 frontmatter
        frontmatter = self.parse_frontmatter(skill_md)
        if not frontmatter:
            self.errors.append(f"[{skill_name}] SKILL.md 缺少 frontmatter")
            return

        # 检查必填字段
        if 'name' not in frontmatter:
            self.errors.append(f"[{skill_name}] frontmatter 缺少 'name' 字段")
        elif frontmatter['name'] != skill_name:
            self.errors.append(
                f"[{skill_name}] frontmatter 中的 name '{frontmatter['name']}' 与目录名不一致"
            )

        if 'description' not in frontmatter:
            self.errors.append(f"[{skill_name}] frontmatter 缺少 'description' 字段")
        else:
            # 检查 description 是否包含中文
            if not self.contains_chinese(frontmatter['description']):
                self.warnings.append(
                    f"[{skill_name}] description 不包含中文，可能影响中文触发: {frontmatter['description'][:50]}"
                )

        # 检查是否有 .upstream.yaml（判断是否为外部技能）
        if upstream_yaml.exists():
            # 验证 .upstream.yaml 格式
            try:
                with open(upstream_yaml, 'r', encoding='utf-8') as f:
                    upstream_data = yaml.safe_load(f)
                    if 'upstream_url' not in upstream_data:
                        self.warnings.append(f"[{skill_name}] .upstream.yaml 缺少 'upstream_url' 字段")
                    if 'last_synced' not in upstream_data:
                        self.warnings.append(f"[{skill_name}] .upstream.yaml 缺少 'last_synced' 字段")
            except Exception as e:
                self.errors.append(f"[{skill_name}] .upstream.yaml 格式错误: {e}")

        self.skills_found.append(skill_name)

    def parse_frontmatter(self, skill_md: Path) -> Dict:
        """解析 SKILL.md 的 frontmatter"""
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # 匹配 frontmatter (--- ... ---)
            match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not match:
                return {}

            frontmatter_text = match.group(1)
            return yaml.safe_load(frontmatter_text)
        except Exception as e:
            self.errors.append(f"解析 {skill_md} 失败: {e}")
            return {}

    def contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def validate_rules_references(self):
        """验证 RULES.md 中引用的技能是否都存在"""
        if not RULES_FILE.exists():
            self.errors.append(f"RULES.md 不存在: {RULES_FILE}")
            return

        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            rules_content = f.read()

        # 提取所有 **skill-name** 格式的技能引用
        skill_references = re.findall(r'\*\*([a-z0-9-]+)\*\*', rules_content)

        for skill_ref in set(skill_references):
            if skill_ref not in self.skills_found:
                # 检查是否是特殊关键词（非技能名）
                if skill_ref in ['must', 'should', 'may', 'yaml']:
                    continue
                self.warnings.append(
                    f"RULES.md 引用了不存在的技能: {skill_ref}"
                )

    def print_results(self) -> bool:
        """输出验证结果"""
        print(f"\n{'='*60}")
        print(f"验证完成！共检查 {len(self.skills_found)} 个技能")
        print(f"{'='*60}\n")

        if self.errors:
            print(f"❌ 发现 {len(self.errors)} 个错误：\n")
            for error in self.errors:
                print(f"  • {error}")
            print()

        if self.warnings:
            print(f"⚠️  发现 {len(self.warnings)} 个警告：\n")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✅ 所有检查通过！")
            return True
        elif not self.errors:
            print("✅ 没有错误，但有一些警告需要注意")
            return True
        else:
            print("❌ 验证失败，请修复上述错误")
            return False

def main():
    validator = SkillValidator()
    success = validator.validate_all()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
