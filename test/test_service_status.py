# -*- coding: utf-8 -*-
"""
检查 pansou 服务状态
"""

import httpx
import asyncio


async def check_service():
    base_url = "http://pansou.xzcccc.eu.org"

    # 检查根路径
    print("=" * 80)
    print("检查服务状态")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        # 检查根路径
        try:
            print(f"\n1. GET {base_url}/")
            response = await client.get(base_url)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content length: {len(response.text)}")
            print(f"   First 200 chars: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ 错误: {e}")

        # 检查 /api/health
        try:
            print(f"\n2. GET {base_url}/api/health")
            response = await client.get(f"{base_url}/api/health")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content: {response.text[:500]}")
        except Exception as e:
            print(f"   ❌ 错误: {e}")

        # 检查 /api/search (OPTIONS)
        try:
            print(f"\n3. POST {base_url}/api/search")
            response = await client.post(
                f"{base_url}/api/search",
                json={"kw": "test"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content length: {len(response.text)}")
        except Exception as e:
            print(f"   ❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(check_service())
