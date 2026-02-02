# -*- coding: utf-8 -*-
"""
对比不同参数组合
"""

import httpx
import asyncio


async def test_pansou():
    url = "http://pansou.xzcccc.eu.org/api/search"

    # 测试不同参数组合
    test_cases = [
        {
            "name": "只传 kw",
            "params": {"kw": "流浪地球"}
        },
        {
            "name": "kw + res=results",
            "params": {"kw": "流浪地球", "res": "results"}
        },
        {
            "name": "kw + res=merged_by_type",
            "params": {"kw": "流浪地球", "res": "merged_by_type"}
        },
        {
            "name": "完整参数（当前代码）",
            "params": {
                "kw": "流浪地球",
                "res": "merged_by_type",
                "src": "all",
                "cloud_types": "quark",
                "refresh": True
            }
        },
        {
            "name": "cloud_types 用数组",
            "params": {
                "kw": "流浪地球",
                "res": "merged_by_type",
                "src": "all",
                "cloud_types": ["quark"],
                "refresh": True
            }
        },
    ]

    for test in test_cases:
        print("=" * 80)
        print(f"测试: {test['name']}")
        print(f"参数: {test['params']}")
        print("=" * 80)

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.post(url, json=test['params'])
            data = response.json()

        total = data.get('data', {}).get('total', 0)
        print(f"Total: {total}")

        merged = data.get('data', {}).get('merged_by_type', {})
        if merged:
            first_type = list(merged.keys())[0]
            items = merged[first_type]
            print(f"First type '{first_type}' ({len(items)} 个):")
            for i, item in enumerate(items[:3], 1):
                print(f"  {i}. {item.get('note', '')[:40]}...")

        print()


if __name__ == "__main__":
    asyncio.run(test_pansou())
