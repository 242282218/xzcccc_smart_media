## 执行计划

重启后测试 pansou 服务是否正常工作：

1. 测试健康检查接口
2. 测试搜索"流浪地球"
3. 对比重启前后的结果

## 命令

```bash
# 1. 健康检查
curl -s http://pansou.xzcccc.eu.org/api/health

# 2. 测试搜索
python test_pansou_direct.py
```

## 预期结果

- 健康检查正常
- 搜索返回与关键词相关的结果（不是固定的5130条）

请确认是否执行？