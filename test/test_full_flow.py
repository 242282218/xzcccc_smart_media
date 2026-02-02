# -*- coding: utf-8 -*-
"""
测试完整流程 - 模拟前端请求
"""

import httpx
import asyncio


def serialize_params(params):
    """模拟前端参数序列化"""
    parts = []
    for key, value in params.items():
        if value is None or value == []:
            continue
        if isinstance(value, list):
            # repeat 格式: key=value1&key=value2
            for v in value:
                parts.append(f"{key}={v}")
        else:
            parts.append(f"{key}={value}")
    return '&'.join(parts)


async def test_full_flow():
    base_url = "http://localhost:8000"

    # 测试1: 只选夸克
    print("=" * 80)
    print("测试1: 只选夸克 (cloud_types=['quark'])")
    print("=" * 80)

    params1 = {
        "keyword": "流浪地球",
        "cloud_types": ["quark"],
        "page_size": 5
    }
    query1 = serialize_params(params1)
    url1 = f"{base_url}/api/search?{query1}"
    print(f"URL: {url1}")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url1)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Filters: {data.get('filters')}")

    # 测试2: 选夸克+百度
    print("\n" + "=" * 80)
    print("测试2: 选夸克+百度 (cloud_types=['quark', 'baidu'])")
    print("=" * 80)

    params2 = {
        "keyword": "流浪地球",
        "cloud_types": ["quark", "baidu"],
        "page_size": 5
    }
    query2 = serialize_params(params2)
    url2 = f"{base_url}/api/search?{query2}"
    print(f"URL: {url2}")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url2)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Filters: {data.get('filters')}")

    # 测试3: 只选阿里云盘
    print("\n" + "=" * 80)
    print("测试3: 只选阿里云盘 (cloud_types=['aliyun'])")
    print("=" * 80)

    params3 = {
        "keyword": "流浪地球",
        "cloud_types": ["aliyun"],
        "page_size": 5
    }
    query3 = serialize_params(params3)
    url3 = f"{base_url}/api/search?{query3}"
    print(f"URL: {url3}")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url3)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Filters: {data.get('filters')}")


if __name__ == "__main__":
    asyncio.run(test_full_flow())
