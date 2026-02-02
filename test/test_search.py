# -*- coding: utf-8 -*-
"""
测试搜索评分系统

搜索"凡人修仙传"并验证评分计算
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'quark_strm'))

from app.services.search_service import ResourceSearchService


async def test_search():
    """测试搜索并打印评分结果"""
    service = ResourceSearchService()

    print("=" * 80)
    print("测试搜索: 凡人修仙传")
    print("=" * 80)

    # 执行搜索
    result = await service.search(
        keyword="凡人修仙传",
        cloud_types=["quark", "aliyun"],
        page=1,
        page_size=10,
        sort_by="score"
    )

    if "error" in result:
        print(f"\n❌ 搜索失败: {result['error']}")
        return

    print(f"\n✅ 搜索成功!")
    print(f"总计结果: {result['total']}")
    print(f"当前页: {result['page']}")
    print(f"每页大小: {result['page_size']}")
    print(f"是否有更多: {result['has_more']}")

    print("\n" + "=" * 80)
    print("评分结果 (按综合评分排序)")
    print("=" * 80)

    for i, item in enumerate(result['results'], 1):
        print(f"\n【{i}】{item['title']}")
        print(f"   综合评分: {item.get('score', 0):.3f}")
        print(f"   置信度:   {item.get('confidence', 0):.3f}")
        print(f"   质量分:   {item.get('quality', 0):.3f}")
        print(f"   新鲜度:   {item.get('freshness', 0):.3f}")
        print(f"   热度:     {item.get('popularity', 0):.3f}")
        print(f"   标签:     {', '.join(item.get('tags', []))}")
        print(f"   来源:     {item['source']}")
        print(f"   发布时间: {item.get('pub_date', '未知')}")

        # 打印网盘链接
        for link in item.get('cloud_links', []):
            print(f"   [{link['type']}] {link['url'][:60]}...")

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_search())
