# -*- coding: utf-8 -*-
"""
测试 cloud_types 用数组格式
"""

import httpx
import asyncio


async def test_array_format():
    url = "http://pansou.xzcccc.eu.org/api/search"

    # 测试1: 字符串格式（当前代码）
    print("=" * 80)
    print("测试1: cloud_types 用字符串格式")
    print("=" * 80)

    params1 = {
        "kw": "流浪地球",
        "res": "merged_by_type",
        "src": "all",
        "cloud_types": "quark"  # 字符串
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.post(url, json=params1)
        data = response.json()

    total1 = data.get('data', {}).get('total', 0)
    print(f"Total: {total1}")

    merged1 = data.get('data', {}).get('merged_by_type', {})
    print(f"Types: {list(merged1.keys())}")

    # 显示前5条
    for cloud_type, items in merged1.items():
        print(f"\n{cloud_type} ({len(items)} 个):")
        for i, item in enumerate(items[:5], 1):
            print(f"  {i}. {item.get('note', '')[:50]}...")
        break

    # 测试2: 数组格式（文档示例）
    print("\n" + "=" * 80)
    print("测试2: cloud_types 用数组格式")
    print("=" * 80)

    params2 = {
        "kw": "流浪地球",
        "res": "merged_by_type",
        "src": "all",
        "cloud_types": ["quark"]  # 数组
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.post(url, json=params2)
        data = response.json()

    total2 = data.get('data', {}).get('total', 0)
    print(f"Total: {total2}")

    merged2 = data.get('data', {}).get('merged_by_type', {})
    print(f"Types: {list(merged2.keys())}")

    # 显示前5条
    for cloud_type, items in merged2.items():
        print(f"\n{cloud_type} ({len(items)} 个):")
        for i, item in enumerate(items[:5], 1):
            print(f"  {i}. {item.get('note', '')[:50]}...")
        break

    # 测试3: 不传 cloud_types
    print("\n" + "=" * 80)
    print("测试3: 不传 cloud_types")
    print("=" * 80)

    params3 = {
        "kw": "流浪地球",
        "res": "merged_by_type",
        "src": "all"
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.post(url, json=params3)
        data = response.json()

    total3 = data.get('data', {}).get('total', 0)
    print(f"Total: {total3}")

    merged3 = data.get('data', {}).get('merged_by_type', {})
    print(f"Types: {list(merged3.keys())}")

    # 显示前5条
    for cloud_type, items in merged3.items():
        print(f"\n{cloud_type} ({len(items)} 个):")
        for i, item in enumerate(items[:5], 1):
            print(f"  {i}. {item.get('note', '')[:50]}...")
        break

    # 对比
    print("\n" + "=" * 80)
    print("对比")
    print("=" * 80)
    print(f"字符串格式: {total1} 条")
    print(f"数组格式:   {total2} 条")
    print(f"不传参数:   {total3} 条")


if __name__ == "__main__":
    asyncio.run(test_array_format())
