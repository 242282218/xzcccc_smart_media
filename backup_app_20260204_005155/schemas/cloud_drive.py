from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CloudDriveBase(BaseModel):
    name: str = Field(..., description="账号名称")
    drive_type: str = Field(..., description="网盘类型: quark, 115")
    remark: Optional[str] = None

class CloudDriveCreate(CloudDriveBase):
    cookie: str = Field(..., description="Cookie字符串")

class CloudDriveUpdate(BaseModel):
    name: Optional[str] = None
    cookie: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[str] = None

class CloudDriveResponse(CloudDriveBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    last_check: Optional[datetime]
    created_at: datetime
    updated_at: datetime
