import re
import asyncio
from typing import Optional, Dict, Any

class MediaParser:
    """媒体文件名解析器"""
    
    # 常见中文命名模式
    PATTERNS = [
        # [标题][年份][分辨率]
        r'^\[(?P<title>[^\]]+)\]\s*\[?(?P<year>\d{4})\]?\s*\[?(?P<resolution>\d+[pP])\]?',
        
        # 标题.年份.分辨率 (宽容匹配)
        # 例子: 流浪地球2.2023.1080p.mp4
        r'^(?P<title>[\u4e00-\u9fa5\w\.\s\-\(\)]+?)[\.\s](?P<year>\d{4})[\.\s].*?(?P<resolution>\d{3,4}[pP])?',
        
        # 剧集: 剧名.S01E02 / 剧名.第01集
        r'^(?P<title>[\u4e00-\u9fa5\w\.\s]+?)[\.\s]?[Ss](?P<season>\d+)[Ee](?P<episode>\d+)',
        
        # 标准英文: Movie.Name.2023.1080p
        r'^(?P<title>[\w\.\s]+?)[\.\s](?P<year>\d{4})[\.\s].*?(?P<resolution>\d{3,4}[pP])?',
    ]
    
    @classmethod
    def parse(cls, filename: str) -> Dict[str, Any]:
        """
        使用正则解析文件名 (同步，快速)
        """
        info = {
            "title": filename, 
            "original_title": filename,
            "year": None, 
            "season": None, 
            "episode": None,
            "resolution": None,
            "ai_parsed": False,
            "source": "regex"
        }
        
        # Remove extension
        if '.' in filename:
            name_without_ext = filename.rsplit('.', 1)[0]
        else:
            name_without_ext = filename
            
        for pattern in cls.PATTERNS:
            match = re.match(pattern, name_without_ext)
            if match:
                data = match.groupdict()
                if "title" in data:
                    info["title"] = data["title"].replace('.', ' ').strip()
                    info["original_title"] = info["title"]
                if "year" in data and data["year"]:
                    info["year"] = int(data["year"])
                if "season" in data and data["season"]:
                    info["season"] = int(data["season"])
                if "episode" in data and data["episode"]:
                    info["episode"] = int(data["episode"])
                if "resolution" in data and data["resolution"]:
                    info["resolution"] = data["resolution"]
                return info
                
        # Simple fallback for year if present anywhere
        year_match = re.search(r'(19|20)\d{2}', name_without_ext)
        if year_match:
            info["year"] = int(year_match.group(0))
            
        return info

    @classmethod
    async def parse_with_ai(cls, filename: str, force: bool = False) -> Dict[str, Any]:
        """
        带AI增强的解析 (异步，较慢但准确)
        :param force: 是否强制使用AI
        """
        # 1. 先进行正则解析
        info = cls.parse(filename)
        
        # 2. 判断是否需要 AI 介入
        # 如果强制开启，或者正则解析结果不理想 (例如缺年份，或者完全没匹配到模式)
        needs_ai = force or (not info.get("year") and not info.get("season"))
        
        if not needs_ai:
            return info
            
        # 3. 调用 AI 解析
        from app.services.ai_parser_service import get_ai_parser_service
        ai_service = get_ai_parser_service()
        
        if not ai_service.api_key:
            return info
            
        ai_result = await ai_service.parse_filename(filename)
        
        if ai_result:
            # 合并结果 (优先使用 AI 结果)
            info["title"] = ai_result.title
            if ai_result.original_title:
                info["original_title"] = ai_result.original_title
            if ai_result.year:
                info["year"] = ai_result.year
            if ai_result.season is not None:
                info["season"] = ai_result.season
            if ai_result.episode is not None:
                info["episode"] = ai_result.episode
                
            info["ai_parsed"] = True
            info["source"] = "ai"
            info["confidence"] = ai_result.confidence
            
        return info
