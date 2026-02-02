# -*- coding: utf-8 -*-
"""
测试 GET 方式请求 pansou API
"""

import httpx
import asyncio


async def test_get_request():
    base_url = "http://pansou.xzcccc.eu.org"

    # 测试 GET 方式
    print("=" * 80)
    print("测试 GET 方式请求")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        # GET 请求
        response = await client.get(
            f"{base_url}/api/search",
            params={
                "kw": "流浪地球",
                "res": "merged_by_type",
                "src": "all",
                "cloud_types": "quark"
            }
        )

    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")

    data = response.json()
    total = data.get('data', {}).get('total', 0)
    print(f"\nTotal: {total}")

    merged = data.get('data', {}).get('merged_by_type', {})
    print(f"Types: {list(merged.keys())}")

    # 显示前10条
    for cloud_type, items in merged.items():
        print(f"\n{cloud_type} ({len(items)} 个):")
        for i, item in enumerate(items[:10], 1):
            note = item.get('note', '')
            has_keyword = "流浪地球" in note
            marker = "✅" if has_keyword else "❌"
            print(f"  {marker} {i}. {note[:50]}...")
        break


if __name__ == "__main__":
    asyncio.run(test_get_request())
