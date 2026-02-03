import aiohttp
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass
from app.core.config_manager import ConfigManager
from app.core.logging import get_logger
from app.core.retry import retry_on_transient, TransientError

logger = get_logger(__name__)

@dataclass
class AIParseResult:
    """AI解析结果"""
    title: str
    original_title: Optional[str] = None
    year: Optional[int] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    media_type: str = "movie"  # movie/tv
    confidence: float = 0.0

class AIParserService:
    """AI辅助解析服务 (Zhipu AI)"""
    
    SYSTEM_PROMPT = """你是一个专业的媒体文件名解析助手。
用户会给你一个媒体文件名，你需要从中提取以下信息：
1. title: 中文标题（如果原名是英文，请翻译成中文；如果包含中文则保留）
2. original_title: 原始标题（通常是英文部分）
3. year: 年份（4位数字，如2023）
4. media_type: 类型（"movie" 或 "tv"）
5. season: 季数（仅电视剧，数字，如1）
6. episode: 集数（仅电视剧，数字，如15）

请以JSON格式返回，严格遵守JSON语法，不要包含markdown代码块标记或其他文字。

示例输入: "The.Wandering.Earth.2.2023.BluRay.1080p.mkv"
示例输出: {"title": "流浪地球2", "original_title": "The Wandering Earth 2", "year": 2023, "media_type": "movie", "season": null, "episode": null}

示例输入: "三体.Three-Body.S01E15.2023.WEB-DL.4K.H265.AAC-AUDIOVIDEO.mp4"
示例输出: {"title": "三体", "original_title": "Three-Body", "year": 2023, "media_type": "tv", "season": 1, "episode": 15}
"""

    _instance = None

    def __init__(self):
        config = ConfigManager()
        # 优先读取配置中的密钥，不再使用硬编码
        self.api_key = (
            config.get("zhipu.api_key")
            or config.get("api_keys.ai_api_key")
            or config.get("ai.api_key", "")
        )
        self.model = config.get("ai.model", "glm-4.7-flash")
        self.base_url = config.get("ai.base_url", "https://open.bigmodel.cn/api/paas/v4")
        self.timeout = config.get("ai.timeout", 30)
        
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = AIParserService()
        return cls._instance
        
    @retry_on_transient()
    async def _post_request(self, url: str, headers: dict, payload: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status in {408, 429} or resp.status >= 500:
                    raise TransientError(f"AI API transient error: {resp.status}")
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"AI API error: {resp.status} - {text}")
                    return {}
                return await resp.json()

    async def parse_filename(self, filename: str) -> Optional[AIParseResult]:
        """使用AI解析文件名"""
        if not self.api_key:
            logger.warning("AI API key not configured")
            return None
            
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"请解析这个文件名: {filename}"}
            ],
            "max_tokens": 512,
            "temperature": 0.1,  # 低温度保证输出稳定
            "stream": False
        }
        
        try:
            data = await self._post_request(url, headers, payload)
            if not data or "choices" not in data or not data["choices"]:
                return None

            content = data["choices"][0]["message"]["content"]

            # 清理可能存在的 markdown 标记
            content = content.replace("```json", "").replace("```", "").strip()

            try:
                result = json.loads(content)
                return AIParseResult(
                    title=result.get("title", ""),
                    original_title=result.get("original_title"),
                    year=result.get("year"),
                    season=result.get("season"),
                    episode=result.get("episode"),
                    media_type=result.get("media_type", "movie"),
                    confidence=0.95  # AI解析通常比较准确
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to decode AI response JSON: {content}")
                return None
        except Exception as e:
            logger.error(f"AI parse error for {filename}: {e}")
            return None

def get_ai_parser_service() -> AIParserService:
    return AIParserService.get_instance()
