"""
Popularity calculator - 热度计算器

计算资源的热度得分
"""

import math


class PopularityCalculator:
    """热度计算器"""

    def calculate(self, views: int = 0) -> float:
        """
        计算热度分

        Args:
            views: 浏览次数

        Returns:
            热度分 (0-1)
        """
        if views <= 0:
            return 0.0

        # 使用log1p进行对数压缩，以200次为满分基准
        return min(1.0, math.log1p(views) / math.log1p(200))
