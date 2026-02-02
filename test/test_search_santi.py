# -*- coding: utf-8 -*-
"""
测试搜索"三体"并验证限制条件

1. 验证默认只搜索夸克网盘
2. 验证大小过滤（1GB）
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'quark_strm'))

from app.services.search_service import ResourceSearchService


async def test_search():
    """测试搜索并打印结果"""
    service = ResourceSearchService()

    print("=" * 80)
    print("测试搜索: 三体")
    print("=" * 80)

    # 测试1: 默认搜索（应该只返回夸克资源）
    print("\n【测试1】默认搜索（不指定cloud_types）")
    print("-" * 80)
    result1 = await service.search(
        keyword="三体",
        page=1,
        page_size=10
    )

    if "error" in result1:
        print(f"❌ 搜索失败: {result1['error']}")
        return

    print(f"✅ 搜索成功!")
    print(f"总计结果: {result1['total']}")
    print(f"筛选条件: {result1.get('filters', {})}")

    # 检查网盘类型分布
    cloud_type_count = {}
    for item in result1['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count[ct] = cloud_type_count.get(ct, 0) + 1

    print(f"网盘类型分布: {cloud_type_count}")

    # 显示前5条结果
    print("\n前5条结果:")
    for i, item in enumerate(result1['results'][:5], 1):
        cloud_types = [link['type'] for link in item.get('cloud_links', [])]
        print(f"  {i}. {item['title'][:50]}... [{', '.join(cloud_types)}]")

    # 测试2: 开启大小过滤（1GB = 1073741824 字节）
    print("\n" + "=" * 80)
    print("【测试2】开启大小过滤（最小1GB）")
    print("-" * 80)

    result2 = await service.search(
        keyword="三体",
        page=1,
        page_size=10,
        min_file_size=1073741824  # 1GB
    )

    if "error" in result2:
        print(f"❌ 搜索失败: {result2['error']}")
        return

    print(f"✅ 搜索成功!")
    print(f"总计结果: {result2['total']}")
    print(f"筛选条件: {result2.get('filters', {})}")

    # 显示带大小的结果
    print("\n带文件大小的结果:")
    count_with_size = 0
    for i, item in enumerate(result2['results'][:10], 1):
        size_info = ""
        if 'file_size_human' in item:
            size_info = f" [{item['file_size_human']}]"
            count_with_size += 1

        cloud_types = [link['type'] for link in item.get('cloud_links', [])]
        print(f"  {i}. {item['title'][:40]}... [{', '.join(cloud_types)}]{size_info}")

    print(f"\n成功获取大小的资源数: {count_with_size}")

    # 测试3: 搜索所有网盘类型
    print("\n" + "=" * 80)
    print("【测试3】搜索所有网盘类型")
    print("-" * 80)

    result3 = await service.search(
        keyword="三体",
        cloud_types=["quark", "baidu", "aliyun"],
        page=1,
        page_size=10
    )

    if "error" in result3:
        print(f"❌ 搜索失败: {result3['error']}")
        return

    print(f"✅ 搜索成功!")
    print(f"总计结果: {result3['total']}")
    print(f"筛选条件: {result3.get('filters', {})}")

    # 检查网盘类型分布
    cloud_type_count3 = {}
    for item in result3['results']:
        for link in item.get('cloud_links', []):
            ct = link.get('type', 'unknown')
            cloud_type_count3[ct] = cloud_type_count3.get(ct, 0) + 1

    print(f"网盘类型分布: {cloud_type_count3}")

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_search())
