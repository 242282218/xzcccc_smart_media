# -*- coding: utf-8 -*-
"""
测试 FastAPI 解析重复参数
"""

import httpx
import asyncio


async def test_fastapi():
    base_url = "http://localhost:8000"

    # 测试1: 使用重复参数格式（正确格式）
    print("=" * 80)
    print("测试1: 重复参数格式 cloud_types=quark&cloud_types=baidu")
    print("=" * 80)

    # 手动构建 URL
    url = f"{base_url}/api/search?keyword=%E6%B5%81%E6%B5%AA%E5%9C%B0%E7%90%83&cloud_types=quark&cloud_types=baidu&page_size=5"
    print(f"URL: {url}")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Filters: {data.get('filters')}")
    else:
        print(f"Error: {response.text}")

    # 测试2: 使用逗号分隔格式
    print("\n" + "=" * 80)
    print("测试2: 逗号分隔格式 cloud_types=quark,baidu")
    print("=" * 80)

    url = f"{base_url}/api/search?keyword=%E6%B5%81%E6%B5%AA%E5%9C%B0%E7%90%83&cloud_types=quark,baidu&page_size=5"
    print(f"URL: {url}")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Filters: {data.get('filters')}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    asyncio.run(test_fastapi())
