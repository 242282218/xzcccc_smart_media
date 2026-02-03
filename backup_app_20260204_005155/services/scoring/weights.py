"""
Scoring weights - 评分权重配置

定义各维度评分的权重
"""

from dataclasses import dataclass


@dataclass
class ScoringWeights:
    """评分权重配置"""

    confidence: float = 0.7
    quality: float = 0.3
    popularity: float = 0.1
    freshness: float = 0.05
