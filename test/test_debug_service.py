# -*- coding: utf-8 -*-
"""
直接测试搜索服务，查看参数传递
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'quark_strm'))

from app.services.search_service import ResourceSearchService


async def test_debug():
    service = ResourceSearchService()

    # 测试1: 只搜索夸克
    print("=" * 80)
    print("测试1: cloud_types=['quark']")
    print("=" * 80)

    result1 = await service.search(
        keyword="流浪地球",
        cloud_types=["quark"],
        page=1,
        page_size=5
    )

    print(f"Total: {result1['total']}")
    print(f"Filters: {result1.get('filters')}")
    cloud_type_count = {}
    for item in result1['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
    print(f"结果网盘类型分布: {cloud_type_count}")

    # 测试2: 搜索夸克+百度
    print("\n" + "=" * 80)
    print("测试2: cloud_types=['quark', 'baidu']")
    print("=" * 80)

    result2 = await service.search(
        keyword="流浪地球",
        cloud_types=["quark", "baidu"],
        page=1,
        page_size=5
    )

    print(f"Total: {result2['total']}")
    print(f"Filters: {result2.get('filters')}")
    cloud_type_count = {}
    for item in result2['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
    print(f"结果网盘类型分布: {cloud_type_count}")

    # 测试3: 搜索阿里云盘
    print("\n" + "=" * 80)
    print("测试3: cloud_types=['aliyun']")
    print("=" * 80)

    result3 = await service.search(
        keyword="流浪地球",
        cloud_types=["aliyun"],
        page=1,
        page_size=5
    )

    print(f"Total: {result3['total']}")
    print(f"Filters: {result3.get('filters')}")
    cloud_type_count = {}
    for item in result3['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
    print(f"结果网盘类型分布: {cloud_type_count}")


if __name__ == "__main__":
    asyncio.run(test_debug())
