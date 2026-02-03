import asyncio
import uuid
import os
import aiohttp
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.logging import get_logger
from app.core.retry import retry_on_transient, TransientError
from app.core.db_utils import AsyncBatchProcessor, batch_get_models_by_ids
from app.models.scrape import ScrapeJob, ScrapeItem
from app.services.tmdb_service import get_tmdb_service, TMDBService
from app.services.notification_service import get_notification_service, NotificationService, NotificationType
from app.services.quark_service import QuarkService
from app.services.nfo_generator import NFOGenerator
from app.utils.media_parser import MediaParser
from app.services.emby_service import get_emby_service
from app.core.validators import validate_path

logger = get_logger(__name__)

class ScrapeService:
    """媒体刮削服务"""
    
    _instance = None
    
    def __init__(
        self,
        tmdb_service: Optional[TMDBService] = None,
        notification_service: Optional[NotificationService] = None,
        emby_service: Optional[Any] = None,
        db_session_factory=SessionLocal,
    ):
        # Try to use global TMDB service if initialized, otherwise None (lazy loading)
        from app.services.tmdb_service import _global_tmdb_service
        self.tmdb_service = tmdb_service or _global_tmdb_service
        self.notification_service = notification_service or get_notification_service()
        self.emby_service = emby_service or get_emby_service()
        self.db_session_factory = db_session_factory
        # 任务锁，简单的并发控制
        self._active_jobs = {}
        
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = ScrapeService()
        return cls._instance

    async def create_job(
        self,
        target_path: str,
        media_type: str = "auto",
        options: Dict[str, Any] = None
    ) -> ScrapeJob:
        """创建刮削任务"""
        target_path = validate_path(target_path, "target_path")
        job_id = str(uuid.uuid4())
        
        db = self.db_session_factory()
        try:
            job = ScrapeJob(
                job_id=job_id,
                target_path=target_path,
                media_type=media_type,
                status="pending",
                options=options or {}
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            return job
        finally:
            db.close()

    async def start_job(self, job_id: str) -> bool:
        """启动刮削任务"""
        if job_id in self._active_jobs:
            logger.warning(f"Job {job_id} is already running")
            return False
            
        db = self.db_session_factory()
        try:
            job = db.query(ScrapeJob).filter(ScrapeJob.job_id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
                
            if job.status == "running":
                return True
                
            # Update status
            job.status = "running"
            job.started_at = datetime.now()
            db.commit()
            
            # Start async processing
            task = asyncio.create_task(self._process_job(job_id))
            self._active_jobs[job_id] = task
            return True
            
        finally:
            db.close()

    async def _process_job(self, job_id: str):
        """处理任务 (后台运行)"""
        logger.info(f"Starting scrape job {job_id}")
        
        await self.notification_service.send_notification(
            type=NotificationType.TASK_STARTED,
            title="开始刮削任务",
            content=f"任务ID: {job_id}"
        )
        
        db = self.db_session_factory()
        job = db.query(ScrapeJob).filter(ScrapeJob.job_id == job_id).first()
        if not job:
            return

        try:
            # 1. 扫描文件（使用流式处理避免内存峰值）
            files_to_process = self._scan_directory(job.target_path)
            
            job.total_items = len(files_to_process)
            db.commit()
            
            # 使用批处理优化数据库操作
            batch_processor = AsyncBatchProcessor(batch_size=50, delay=0.1)
            
            async def process_file_batch(file_batch):
                """处理文件批次"""
                batch_items = []
                batch_results = []
                
                # 批量创建Item记录
                for file_path in file_batch:
                    # Check cancellation
                    if job.status == "cancelled":
                        break
                        
                    filename = os.path.basename(file_path)
                    
                    item = ScrapeItem(
                        job_id=job_id,
                        file_path=file_path,
                        file_name=filename,
                        status="running"
                    )
                    batch_items.append(item)
                    db.add(item)
                
                if batch_items:
                    db.commit()
                    
                    # 批量处理刮削
                    for item in batch_items:
                        try:
                            success = await self._scrape_single_item(item, job.options)
                            
                            if success:
                                item.status = "scraped"
                                job.success_items += 1
                            else:
                                item.status = "failed"
                                job.failed_items += 1
                            
                            job.processed_items += 1
                            batch_results.append(success)
                            
                        except Exception as e:
                            logger.error(f"Error scraping item {item.file_name}: {e}")
                            item.status = "failed"
                            item.error_message = str(e)
                            job.failed_items += 1
                            job.processed_items += 1
                            batch_results.append(False)
                        
                        # 小延迟避免API速率限制
                        await asyncio.sleep(0.1)
                    
                    db.commit()
                
                return batch_results
            
            # 分批处理所有文件
            await batch_processor.process_items_batched(
                files_to_process,
                process_file_batch
            )

            job.status = "completed"
            job.completed_at = datetime.now()
            
            await self.notification_service.send_notification(
                type=NotificationType.TASK_COMPLETED,
                title="刮削任务完成",
                content=f"成功: {job.success_items}, 失败: {job.failed_items}"
            )
            
            # 触发Emby库刷新
            try:
                emby_library_id = job.options.get("emby_library_id")
                refresh_success = await self.emby_service.refresh_library(emby_library_id)
                if refresh_success:
                    logger.info("Emby library refresh triggered successfully after scrape job")
                else:
                    logger.warning("Failed to trigger Emby library refresh after scrape job")
            except Exception as e:
                logger.error(f"Error triggering Emby refresh: {e}")

        except Exception as e:
            logger.error(f"Scrape job failed: {e}")
            job.status = "failed"
            job.error_message = str(e)
            
            await self.notification_service.send_notification(
                type=NotificationType.TASK_FAILED,
                title="刮削任务失败",
                content=str(e)
            )
        finally:
            if job_id in self._active_jobs:
                del self._active_jobs[job_id]
            db.commit()
            db.close()

    def _scan_directory(self, path: str) -> List[str]:
        """扫描本地目录获取媒体文件"""
        media_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.strm'}
        files = []
        if not os.path.exists(path):
            return []
            
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in media_extensions:
                    files.append(os.path.join(root, filename))
        return files

    @retry_on_transient()
    async def _download_image(self, url: str, save_path: str) -> bool:
        """下载图片"""
        if not url:
            return False
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status in {408, 429} or resp.status >= 500:
                        raise TransientError(f"Download transient error: {resp.status}")
                    if resp.status == 200:
                        content = await resp.read()
                        with open(save_path, "wb") as f:
                            f.write(content)
                        return True
        except TransientError:
            raise
        except aiohttp.ClientError as e:
            raise
        except Exception as e:
            logger.error(f"Failed to download image {url}: {e}")
            return False

    async def _scrape_single_item(self, item: ScrapeItem, options: dict) -> bool:
        """刮削单个项目"""
        # Ensure TMDB Service is available
        tmdb = self.tmdb_service
        if not tmdb:
            from app.core.config_manager import ConfigManager
            from app.services.cache_service import get_cache_service
            config = ConfigManager()
            api_key = config.get("api_keys.tmdb_api_key") or config.get("tmdb.api_key")
            if api_key:
                 tmdb = get_tmdb_service(api_key=api_key, cache_service=get_cache_service())
                 self.tmdb_service = tmdb
            
        if not tmdb:
            raise Exception("TMDB Service unavailable. Please configure API Key.")

        # Parse filename
        info = MediaParser.parse(item.file_name)
        
        # Decide media type
        media_type = "movie"
        if options.get("media_type") == "tv":
             media_type = "tv"
        elif options.get("media_type") == "movie":
             media_type = "movie"
        elif info.get("season") is not None or info.get("episode") is not None:
             media_type = "tv"
             
        item.media_type = media_type
            
        # Search
        file_dir = os.path.dirname(item.file_path)
        base_name = os.path.splitext(item.file_name)[0]
        
        if media_type == "movie":
            search_res = await tmdb.search_movie(info["title"], year=info["year"])
            if not search_res.results:
                 # Retry without year if failed
                 if info["year"]:
                    search_res = await tmdb.search_movie(info["title"])
                    
            if not search_res.results:
                item.error_message = "No match found in TMDB"
                return False
                
            match = search_res.results[0] # Best match
            item.tmdb_id = match.id
            item.title = match.title
            item.original_title = match.original_title
            item.year = int(match.release_date[:4]) if match.release_date else None
            
            # Get Detail using global cache if possible
            detail = await tmdb.get_movie_detail(match.id)
            
            # Generate NFO
            nfo_xml = NFOGenerator.generate_movie_nfo(detail)
            nfo_path = os.path.join(file_dir, f"{base_name}.nfo")
            
            # Write NFO
            if options.get("force_overwrite") or not os.path.exists(nfo_path):
                with open(nfo_path, "w", encoding="utf-8") as f:
                    f.write(nfo_xml)
                item.nfo_path = nfo_path
                
            # Images
            if options.get("download_images", True):
                if detail.poster_path:
                    poster_url = tmdb.get_poster_url(detail.poster_path)
                    poster_path = os.path.join(file_dir, f"{base_name}-poster.jpg")
                    if await self._download_image(poster_url, poster_path):
                        item.poster_path = poster_path
                        
                if detail.backdrop_path:
                    fanart_url = tmdb.get_backdrop_url(detail.backdrop_path)
                    fanart_path = os.path.join(file_dir, f"{base_name}-fanart.jpg")
                    if await self._download_image(fanart_url, fanart_path):
                        item.fanart_path = fanart_path
                        
        elif media_type == "tv":
            search_res = await tmdb.search_tv(info["title"], first_air_date_year=info["year"])
            if not search_res.results:
                item.error_message = "No TV show match found"
                return False
                
            show_match = search_res.results[0]
            item.tmdb_id = show_match.id
            item.title = show_match.name
            
            # If season/episode known
            if info.get("season") and info.get("episode"):
                 episode = await tmdb.get_tv_episode(show_match.id, info["season"], info["episode"])
                 item.season = episode.season_number
                 item.episode = episode.episode_number
                 item.title = episode.name or item.title
                 
                 nfo_xml = NFOGenerator.generate_episode_nfo(episode)
                 nfo_path = os.path.join(file_dir, f"{base_name}.nfo")
                 
                 if options.get("force_overwrite") or not os.path.exists(nfo_path):
                     with open(nfo_path, "w", encoding="utf-8") as f:
                         f.write(nfo_xml)
                 item.nfo_path = nfo_path
                 
                 # Episode thumb
                 if episode.still_path and options.get("download_images", True):
                      thumb_url = tmdb.get_image_url(episode.still_path, "w300")
                      thumb_path = os.path.join(file_dir, f"{base_name}-thumb.jpg")
                      await self._download_image(thumb_url, thumb_path)
            else:
                pass

        return True

def get_scrape_service():
    return ScrapeService.get_instance()
