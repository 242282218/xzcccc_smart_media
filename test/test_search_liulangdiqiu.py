# -*- coding: utf-8 -*-
"""
测试搜索"流浪地球"并查看置信度分布
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
    print("测试搜索: 流浪地球")
    print("=" * 80)

    # 搜索流浪地球（不过滤，查看原始结果）
    result = await service.search(
        keyword="流浪地球",
        page=1,
        page_size=100
    )

    if "error" in result:
        print(f"❌ 搜索失败: {result['error']}")
        return

    print(f"✅ 搜索成功!")
    print(f"总计结果: {result['total']}")

    # 统计置信度分布
    confidence_ranges = {
        '0.0-0.1': 0,
        '0.1-0.2': 0,
        '0.2-0.3': 0,
        '0.3-0.5': 0,
        '0.5-0.7': 0,
        '0.7-1.0': 0,
    }

    for item in result['results']:
        conf = item.get('confidence', 0)
        if conf < 0.1:
            confidence_ranges['0.0-0.1'] += 1
        elif conf < 0.2:
            confidence_ranges['0.1-0.2'] += 1
        elif conf < 0.3:
            confidence_ranges['0.2-0.3'] += 1
        elif conf < 0.5:
            confidence_ranges['0.3-0.5'] += 1
        elif conf < 0.7:
            confidence_ranges['0.5-0.7'] += 1
        else:
            confidence_ranges['0.7-1.0'] += 1

    print("\n置信度分布:")
    for range_name, count in confidence_ranges.items():
        print(f"  {range_name}: {count} 个")

    # 显示置信度最高的前10条
    sorted_results = sorted(result['results'], key=lambda x: x.get('confidence', 0), reverse=True)

    print("\n置信度最高的前10条:")
    for i, item in enumerate(sorted_results[:10], 1):
        cloud_types = [link['type'] for link in item.get('cloud_links', [])]
        score = item.get('score', 0)
        confidence = item.get('confidence', 0)
        print(f"  {i}. [{', '.join(cloud_types)}] 评分:{score:.3f} 置信度:{confidence:.3f}")
        print(f"     标题: {item['title'][:60]}...")
        print()

    print("=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_search())
