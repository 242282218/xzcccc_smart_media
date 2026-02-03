"""
quark_api_package SDK配置

集成packages目录下的所有SDK包
"""

import os
import sys
from pathlib import Path
from typing import Optional, Any

# 添加SDK路径
SDK_PATH = Path(r"C:\Users\24228\Desktop\smart_media\quark_api_package")
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

# 先导入logger
from app.core.logging import get_logger
from app.services.config_service import get_config_service

logger = get_logger(__name__)

# SDK导入
SDK_AVAILABLE = False
QuarkClient = None
AsyncQuarkClient = None
SDKQuarkConfig = None
RenameEngine = None

try:
    from packages.quark_sdk import QuarkClient, AsyncQuarkClient
    from packages.quark_sdk.core.config import QuarkConfig as SDKQuarkConfig
    SDK_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Quark SDK导入失败: {e}")

try:
    from packages.rename import RenameEngine
except ImportError as e:
    logger.warning(f"RenameEngine导入失败: {e}")
    RenameEngine = None

if not SDK_AVAILABLE:
    logger.warning("SDK不可用，部分功能将受限")


def get_api_keys():
    """
    从配置文件获取API密钥

    Args:
        无

    Returns:
        dict: 包含 ai_api_key 和 tmdb_api_key 的字典

    Side Effects:
        从 ConfigService 读取配置
    """
    try:
        config_service = get_config_service()
        config = config_service.get_config()
        # 从ConfigService获取API密钥
        ai_api_key = (
            config.zhipu.api_key if getattr(config, "zhipu", None) else None
        ) or (config.api_keys.ai_api_key if config.api_keys else None)
        tmdb_api_key = (
            config.tmdb.api_key if getattr(config, "tmdb", None) else None
        ) or (config.api_keys.tmdb_api_key if config.api_keys else None)
        return {
            'ai_api_key': ai_api_key,
            'tmdb_api_key': tmdb_api_key
        }
    except Exception as e:
        logger.warning(f"无法从配置文件读取API密钥: {e}")
        return {}


class SDKConfig:
    """SDK配置管理"""

    def __init__(self):
        # 从配置文件读取API密钥
        api_keys = get_api_keys()
        
        self.quark_cookie = os.getenv("QUARK_COOKIE", "")
        # 优先从配置文件读取，其次环境变量
        self.tmdb_api_key = api_keys.get('tmdb_api_key') or os.getenv("TMDB_API_KEY", "")
        self.ai_api_key = api_keys.get('ai_api_key') or os.getenv("AI_API_KEY", "")
        
        logger.info(f"SDK配置初始化完成，TMDB API密钥: {'已配置' if self.tmdb_api_key else '未配置'}")
        logger.info(f"AI API密钥: {'已配置' if self.ai_api_key else '未配置'}")

    def is_available(self) -> bool:
        """检查SDK是否可用"""
        return SDK_AVAILABLE

    def get_quark_config(self) -> Optional[SDKQuarkConfig]:
        """获取夸克SDK配置"""
        if not SDK_AVAILABLE:
            return None
        return SDKQuarkConfig(
            api__base_url="https://drive.quark.cn",
            api__timeout=30.0,
            request__max_retries=3,
            request__retry_delay=1.0,
        )

    def create_quark_client(self, cookie: Optional[str] = None) -> Optional[QuarkClient]:
        """创建同步夸克客户端"""
        if not SDK_AVAILABLE:
            return None
        config = self.get_quark_config()
        if config is None:
            return None
        return QuarkClient(
            config=config,
            cookie_string=cookie or self.quark_cookie
        )

    def create_async_quark_client(self, cookie: Optional[str] = None) -> Optional[AsyncQuarkClient]:
        """创建异步夸克客户端"""
        if not SDK_AVAILABLE:
            return None
        config = self.get_quark_config()
        if config is None:
            return None
        return AsyncQuarkClient(
            config=config,
            cookie_string=cookie or self.quark_cookie
        )

    def create_search_service(self) -> Optional[Any]:
        """
        创建搜索服务

        注意：原搜索服务已弃用，功能由 pansou HTTP API 服务替代
        参考: quark_strm/app/services/search_service.py

        Returns:
            None: 搜索服务已通过 pansou 服务实现
        """
        logger.info("搜索服务已通过 pansou HTTP API 实现，无需创建本地服务")
        return None

    def create_rename_engine(self) -> Optional[Any]:
        """创建重命名引擎"""
        if not SDK_AVAILABLE:
            logger.warning("SDK不可用，无法创建重命名引擎")
            return None

        if RenameEngine is None:
            logger.warning("RenameEngine未导入")
            return None

        try:
            return RenameEngine(
                tmdb_api_key=self.tmdb_api_key,
                ai_api_key=self.ai_api_key,
                dry_run=True  # 默认预览模式
            )
        except Exception as e:
            logger.error(f"创建重命名引擎失败: {e}")
            return None


# 全局配置实例
sdk_config = SDKConfig()
