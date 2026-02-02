# -*- coding: utf-8 -*-
"""
测试多网盘类型搜索
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'quark_strm'))

from app.services.search_service import ResourceSearchService


async def test_multi_cloud():
    service = ResourceSearchService()

    # 测试1: 只搜索夸克
    print("=" * 80)
    print("测试1: 只搜索夸克 (cloud_types=['quark'])")
    print("=" * 80)

    result1 = await service.search(
        keyword="流浪地球",
        cloud_types=["quark"],
        page=1,
        page_size=10
    )

    print(f"总计: {result1['total']}")
    cloud_type_count = {}
    for item in result1['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
    print(f"网盘类型分布: {cloud_type_count}")

    # 测试2: 搜索夸克+百度
    print("\n" + "=" * 80)
    print("测试2: 搜索夸克+百度 (cloud_types=['quark', 'baidu'])")
    print("=" * 80)

    result2 = await service.search(
        keyword="流浪地球",
        cloud_types=["quark", "baidu"],
        page=1,
        page_size=10
    )

    print(f"总计: {result2['total']}")
    cloud_type_count = {}
    for item in result2['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
    print(f"网盘类型分布: {cloud_type_count}")

    # 测试3: 搜索阿里云盘
    print("\n" + "=" * 80)
    print("测试3: 搜索阿里云盘 (cloud_types=['aliyun'])")
    print("=" * 80)

    result3 = await service.search(
        keyword="流浪地球",
        cloud_types=["aliyun"],
        page=1,
        page_size=10
    )

    print(f"总计: {result3['total']}")
    cloud_type_count = {}
    for item in result3['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
    print(f"网盘类型分布: {cloud_type_count}")

    # 测试4: 搜索所有网盘
    print("\n" + "=" * 80)
    print("测试4: 搜索所有网盘 (cloud_types=['quark', 'baidu', 'aliyun', 'tianyi'])")
    print("=" * 80)

    result4 = await service.search(
        keyword="流浪地球",
        cloud_types=["quark", "baidu", "aliyun", "tianyi"],
        page=1,
        page_size=10
    )

    print(f"总计: {result4['total']}")
    cloud_type_count = {}
    for item in result4['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1
    print(f"网盘类型分布: {cloud_type_count}")

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_multi_cloud())
