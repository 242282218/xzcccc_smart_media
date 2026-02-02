# -*- coding: utf-8 -*-
"""
测试仪表盘 API
"""

import httpx
import asyncio


async def test_dashboard():
    base_url = "http://localhost:8000"

    # 测试仪表盘统计
    print("=" * 80)
    print("测试仪表盘统计 API")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{base_url}/api/dashboard/stats")

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
    else:
        print(f"Error: {response.text}")

    # 测试趋势数据
    print("\n" + "=" * 80)
    print("测试趋势数据 API")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{base_url}/api/dashboard/trends?days=7")

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    asyncio.run(test_dashboard())
