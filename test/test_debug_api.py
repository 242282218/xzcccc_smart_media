# -*- coding: utf-8 -*-
"""
调试后端 API 参数接收
"""

import httpx
import asyncio


async def test_debug():
    base_url = "http://localhost:8000"

    # 测试1: 只传夸克
    print("=" * 80)
    print("测试1: cloud_types=['quark']")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{base_url}/api/search",
            params={
                "keyword": "流浪地球",
                "cloud_types": ["quark"],
                "page_size": 5
            }
        )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Filters: {data.get('filters')}")

    # 测试2: 传夸克+百度（数组格式）
    print("\n" + "=" * 80)
    print("测试2: cloud_types=['quark', 'baidu'] (数组格式)")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{base_url}/api/search",
            params={
                "keyword": "流浪地球",
                "cloud_types": ["quark", "baidu"],
                "page_size": 5
            }
        )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Filters: {data.get('filters')}")

    # 测试3: 传夸克+百度（逗号分隔字符串）
    print("\n" + "=" * 80)
    print("测试3: cloud_types='quark,baidu' (字符串格式)")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{base_url}/api/search",
            params={
                "keyword": "流浪地球",
                "cloud_types": "quark,baidu",
                "page_size": 5
            }
        )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Filters: {data.get('filters')}")


if __name__ == "__main__":
    asyncio.run(test_debug())
