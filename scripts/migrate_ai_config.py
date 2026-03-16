#!/usr/bin/env python3
"""
AI 配置迁移工具

将旧的分散配置迁移到统一的 OpenAI 兼容格式
"""

import sys
from pathlib import Path

import yaml


def migrate_config(config_path: str = "config.yaml"):
    """迁移配置文件"""
    path = Path(config_path)
    if not path.exists():
        print(f"配置文件不存在: {config_path}")
        return False

    # 读取现有配置
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # 检查是否已有新配置
    if "ai" in config and "providers" in config.get("ai", {}):
        print("✓ 已使用新配置格式")
        return True

    # 迁移旧配置
    providers = []
    priority = 100

    # DeepSeek
    if "deepseek" in config and config["deepseek"].get("api_key"):
        providers.append({
            "name": "deepseek",
            "api_key": config["deepseek"]["api_key"],
            "base_url": config["deepseek"].get("base_url", "https://api.deepseek.com/v1"),
            "model": config["deepseek"].get("model", "deepseek-chat"),
            "timeout": config["deepseek"].get("timeout", 20),
            "enabled": True,
            "priority": priority,
        })
        priority -= 10

    # GLM
    if "glm" in config and config["glm"].get("api_key"):
        providers.append({
            "name": "glm",
            "api_key": config["glm"]["api_key"],
            "base_url": config["glm"].get("base_url", "https://open.bigmodel.cn/api/paas/v4"),
            "model": config["glm"].get("model", "glm-4-flash"),
            "timeout": config["glm"].get("timeout", 15),
            "enabled": True,
            "priority": priority,
        })
        priority -= 10

    # Kimi
    if "kimi" in config and config["kimi"].get("api_key"):
        providers.append({
            "name": "kimi",
            "api_key": config["kimi"]["api_key"],
            "base_url": config["kimi"].get("base_url", "https://integrate.api.nvidia.com/v1"),
            "model": config["kimi"].get("model", "moonshotai/kimi-k2.5"),
            "timeout": config["kimi"].get("timeout", 15),
            "enabled": True,
            "priority": priority,
        })
        priority -= 10

    # Zhipu
    if "zhipu" in config and config["zhipu"].get("api_key"):
        providers.append({
            "name": "zhipu",
            "api_key": config["zhipu"]["api_key"],
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4-flash",
            "timeout": 15,
            "enabled": True,
            "priority": priority,
        })

    if not providers:
        print("⚠ 未找到可迁移的 AI 配置")
        return False

    # 添加新配置
    config["ai"] = {
        "providers": providers,
        "max_retries": 3,
        "fallback_enabled": True,
    }

    # 备份原文件
    backup_path = path.with_suffix(".yaml.backup")
    with open(backup_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    print(f"✓ 已备份到: {backup_path}")

    # 写入新配置
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    print(f"✓ 已迁移 {len(providers)} 个 AI provider")
    print("\n新配置:")
    for p in providers:
        print(f"  - {p['name']} (priority: {p['priority']})")

    return True


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    success = migrate_config(config_path)
    sys.exit(0 if success else 1)
