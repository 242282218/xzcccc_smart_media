# -*- coding: utf-8 -*-
"""
直接测试 pansou API 返回什么
"""

import httpx
import asyncio


async def test_pansou():
    url = "http://pansou.xzcccc.eu.org/api/search"

    params = {
        "kw": "流浪地球",
        "res": "merged_by_type",
        "src": "all",
        "cloud_types": "quark"
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.post(url, json=params)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content length: {len(response.text)}")
        print(f"\nFirst 1000 chars:\n{response.text[:1000]}")


if __name__ == "__main__":
    asyncio.run(test_pansou())
