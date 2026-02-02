# -*- coding: utf-8 -*-
"""
测试重启后的 pansou 服务
"""

import httpx
import asyncio


async def test_after_restart():
    base_url = "http://pansou.xzcccc.eu.org"

    # 1. 健康检查
    print("=" * 80)
    print("1. 健康检查")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        try:
            response = await client.get(f"{base_url}/api/health")
            print(f"Status: {response.status_code}")
            print(f"Response length: {len(response.text)}")
            
            # 尝试解析 JSON
            try:
                health = response.json()
                print(f"Health: {health}")
            except:
                print(f"Response text: {response.text[:500]}")
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")

    # 2. 测试搜索 - 流浪地球
    print("\n" + "=" * 80)
    print("2. 测试搜索: 流浪地球")
    print("=" * 80)

    search_url = f"{base_url}/api/search"
    params = {
        "kw": "流浪地球",
        "res": "merged_by_type",
        "src": "all",
        "cloud_types": "quark"
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.post(search_url, json=params)
        data = response.json()

    total = data.get('data', {}).get('total', 0)
    print(f"Total: {total}")

    merged = data.get('data', {}).get('merged_by_type', {})
    print(f"Types: {list(merged.keys())}")

    # 显示前10条
    for cloud_type, items in merged.items():
        print(f"\n{cloud_type} ({len(items)} 个):")
        for i, item in enumerate(items[:10], 1):
            note = item.get('note', '')
            has_keyword = "流浪地球" in note or "流浪" in note or "地球" in note
            marker = "✅" if has_keyword else "❌"
            print(f"  {marker} {i}. {note[:50]}...")
        break  # 只显示第一个类型

    # 3. 测试搜索 - 三体
    print("\n" + "=" * 80)
    print("3. 测试搜索: 三体")
    print("=" * 80)

    params2 = {
        "kw": "三体",
        "res": "merged_by_type",
        "src": "all",
        "cloud_types": "quark"
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.post(search_url, json=params2)
        data = response.json()

    total2 = data.get('data', {}).get('total', 0)
    print(f"Total: {total2}")

    merged2 = data.get('data', {}).get('merged_by_type', {})
    print(f"Types: {list(merged2.keys())}")

    # 显示前10条
    for cloud_type, items in merged2.items():
        print(f"\n{cloud_type} ({len(items)} 个):")
        for i, item in enumerate(items[:10], 1):
            note = item.get('note', '')
            has_keyword = "三体" in note
            marker = "✅" if has_keyword else "❌"
            print(f"  {marker} {i}. {note[:50]}...")
        break

    # 4. 对比
    print("\n" + "=" * 80)
    print("4. 对比")
    print("=" * 80)
    print(f"流浪地球: {total} 条")
    print(f"三体:     {total2} 条")

    if total == total2 == 5130:
        print("\n⚠️ 警告: 两个关键词返回相同数量的结果，搜索可能仍有问题！")
    else:
        print("\n✅ 正常: 不同关键词返回不同数量的结果")


if __name__ == "__main__":
    asyncio.run(test_after_restart())
