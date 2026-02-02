# -*- coding: utf-8 -*-
"""
直接测试 pansou API，对比 refresh 参数
"""

import httpx
import asyncio


async def test_pansou():
    url = "http://pansou.xzcccc.eu.org/api/search"

    # 测试1: 不带 refresh
    print("=" * 80)
    print("测试1: 不带 refresh 参数")
    print("=" * 80)

    params1 = {
        "kw": "流浪地球",
        "res": "merged_by_type",
        "src": "all",
        "cloud_types": "quark"
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response1 = await client.post(url, json=params1)
        data1 = response1.json()

    print(f"Total: {data1.get('data', {}).get('total', 0)}")
    merged1 = data1.get('data', {}).get('merged_by_type', {})
    print(f"Types: {list(merged1.keys())}")

    # 显示前5条
    for cloud_type, items in merged1.items():
        print(f"\n{cloud_type} ({len(items)} 个):")
        for i, item in enumerate(items[:5], 1):
            print(f"  {i}. {item.get('note', '')[:50]}...")
        break  # 只显示第一个类型

    # 测试2: 带 refresh
    print("\n" + "=" * 80)
    print("测试2: 带 refresh=true 参数")
    print("=" * 80)

    params2 = {
        "kw": "流浪地球",
        "res": "merged_by_type",
        "src": "all",
        "cloud_types": "quark",
        "refresh": True
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response2 = await client.post(url, json=params2)
        data2 = response2.json()

    print(f"Total: {data2.get('data', {}).get('total', 0)}")
    merged2 = data2.get('data', {}).get('merged_by_type', {})
    print(f"Types: {list(merged2.keys())}")

    # 显示前5条
    for cloud_type, items in merged2.items():
        print(f"\n{cloud_type} ({len(items)} 个):")
        for i, item in enumerate(items[:5], 1):
            print(f"  {i}. {item.get('note', '')[:50]}...")
        break  # 只显示第一个类型

    # 对比
    print("\n" + "=" * 80)
    print("对比")
    print("=" * 80)
    print(f"不带 refresh: {data1.get('data', {}).get('total', 0)} 条")
    print(f"带 refresh:   {data2.get('data', {}).get('total', 0)} 条")


if __name__ == "__main__":
    asyncio.run(test_pansou())
