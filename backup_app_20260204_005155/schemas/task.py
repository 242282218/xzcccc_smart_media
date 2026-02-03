from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    task_type: str = Field(..., description="任务类型: strm_generation, scrape, file_sync")
    priority: str = Field("normal", description="优先级")
    params: Dict[str, Any] = Field(default_factory=dict, description="任务参数")

class TaskCreate(TaskBase):
    pass

class TaskLog(BaseModel):
    ts: float
    level: str
    message: str

class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    progress: int
    total_items: int
    processed_items: int
    error_message: Optional[str]
    logs: List[Any] = []
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
