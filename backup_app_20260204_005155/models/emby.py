from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class EmbyLibrary(Base):
    """Emby媒体库表"""
    __tablename__ = "emby_libraries"
    
    id = Column(Integer, primary_key=True, index=True)
    emby_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    path = Column(String(500))
    last_sync_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    items = relationship("EmbyMediaItem", back_populates="library")

class EmbyMediaItem(Base):
    """Emby媒体项表"""
    __tablename__ = "emby_media_items"
    
    id = Column(Integer, primary_key=True, index=True)
    emby_id = Column(String(50), unique=True, index=True)
    library_id = Column(Integer, ForeignKey("emby_libraries.id"))
    name = Column(String(200))
    type = Column(String(50)) # Movie/Episode
    path = Column(String(500))
    pickcode = Column(String(100), index=True) # 关联的夸克Pickcode
    is_strm = Column(Boolean, default=False)
    sync_status = Column(String(20), default="synced")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 关系
    library = relationship("EmbyLibrary", back_populates="items")
