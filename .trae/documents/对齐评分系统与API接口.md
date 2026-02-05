## 目标
将 quark_strm 项目本身的评分逻辑集成到 `search_service.py` 中，替换当前的固定评分值

## quark_strm 评分系统核心

### 评分维度
1. **置信度 (Confidence)** - 权重 30%-80%
   - 文本相似度 (C_text): 基于 Jaccard 和 Token 匹配
   - 意图评分 (C_intent): 负面关键词过滤 + 正面关键词加分
   - 合理性评分 (C_plaus): 文件大小与标签一致性验证

2. **质量分 (Quality)** - 权重 20%-70%
   - 分辨率: 4K(25分) > 1080P(15分) > 720P(6分)
   - 视频格式: BDMV(35分) > Remux(30分) > BluRay(24分) > WebDL(18分)
   - HDR/DV: DV(20分) / HDR(10分)
   - 音频: Atmos(10分) > DTS-X(8分) > TrueHD(6分)
   - 编码: x265(4分) / x264(2分)
   - 字幕: 特效字幕(6分) / 中文字幕(3分)

3. **热度 (Popularity)** - 权重 0-10%
   - 公式: `log1p(views) / log1p(200)`

4. **新鲜度 (Freshness)** - 权重 0-5%
   - 公式: `exp(-days/60)`，60天半衰期

### 综合评分公式
```
Score = α × Conf + (1-α) × Qual + PR_gate × (0.1×P + 0.05×R)

其中:
- α: 动态权重 (0.3-0.8)，基于置信度水平
- PR_gate: 置信度门控 (0.0/0.3/1.0)
```

## 执行计划

### 1. 创建评分模块
新建 `quark_strm/app/services/scoring/` 目录：
- `__init__.py` - 模块导出
- `engine.py` - 评分引擎主类
- `confidence.py` - 置信度计算
- `quality.py` - 质量分计算
- `popularity.py` - 热度计算
- `freshness.py` - 新鲜度计算
- `tags.py` - 标签提取
- `weights.py` - 权重配置

### 2. 修改 search_service.py
- 导入评分引擎
- 在 `_transform_pansou_result()` 中调用评分计算
- 根据评分排序结果

### 3. 更新 API 文档
在 `PANSOU_API_DOC.md` 中添加评分系统说明

请确认是否执行集成？