"""测试 pansou API 连接"""
import httpx
import json

async def test_pansou():
    """测试 pansou API"""
    base_url = "http://pansou.xzcccc.eu.org"

    # 测试健康检查
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(f"{base_url}/api/health")
            print(f"健康检查: {response.status_code}")
            print(f"响应: {response.json()}")
    except Exception as e:
        print(f"健康检查失败: {e}")
        return

    # 测试搜索
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # 使用 POST 方式
            response = await client.post(
                f"{base_url}/api/search",
                json={"kw": "测试", "res": "merged_by_type"}
            )
            print(f"搜索测试: {response.status_code}")
            data = response.json()
            print(f"搜索结果: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
    except Exception as e:
        print(f"搜索测试失败: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_pansou())
