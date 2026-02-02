# -*- coding: utf-8 -*-
"""
直接测试后端 API 的多网盘搜索
"""

import httpx
import asyncio


async def test_api():
    base_url = "http://localhost:8000"  # 本地后端服务

    # 测试1: 只搜索夸克
    print("=" * 80)
    print("测试1: 只搜索夸克")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(
            f"{base_url}/api/search",
            params={
                "keyword": "流浪地球",
                "cloud_types": ["quark"],
                "page_size": 10
            }
        )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total', 0)}")
        cloud_type_count = {}
        for item in data.get('results', []):
            for link in item.get('cloud_links', []):
                ct = link.get('type', 'unknown')
                cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
        print(f"网盘类型分布: {cloud_type_count}")
    else:
        print(f"Error: {response.text}")

    # 测试2: 搜索夸克+百度
    print("\n" + "=" * 80)
    print("测试2: 搜索夸克+百度")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(
            f"{base_url}/api/search",
            params={
                "keyword": "流浪地球",
                "cloud_types": ["quark", "baidu"],
                "page_size": 10
            }
        )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total', 0)}")
        cloud_type_count = {}
        for item in data.get('results', []):
            for link in item.get('cloud_links', []):
                ct = link.get('type', 'unknown')
                cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
        print(f"网盘类型分布: {cloud_type_count}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    asyncio.run(test_api())
