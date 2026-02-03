"""
统一错误处理和日志脱敏模块

提供标准化的错误响应格式和敏感信息脱敏功能
"""
import re
import uuid
import traceback
from typing import Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


class ErrorCode(str, Enum):
    """错误代码枚举"""
    # 验证错误
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    
    # 认证授权错误
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    
    # 资源错误
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    
    # 数据库错误
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    
    # 网络错误
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    
    # 业务逻辑错误
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    
    # 系统错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # 第三方服务错误
    THIRD_PARTY_ERROR = "THIRD_PARTY_ERROR"
    API_RATE_LIMIT = "API_RATE_LIMIT"


class ErrorResponse(BaseModel):
    """标准化错误响应模型"""
    error_code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str
    request_id: Optional[str] = None
    documentation_url: Optional[str] = None


class SuccessResponse(BaseModel):
    """标准化成功响应模型"""
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None


class LogSanitizer:
    """日志脱敏工具类"""
    
    # 敏感信息模式定义
    SENSITIVE_PATTERNS = {
        # 邮箱地址
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        
        # 手机号码（中国格式）
        'phone': r'\b1[3-9]\d{9}\b|\b\d{3}-\d{4}-\d{4}\b',
        
        # API密钥（32位以上的十六进制字符串）
        'api_key': r'\b[A-Fa-f0-9]{32,}\b',
        
        # 密码字段
        'password': r'["\']password["\']\s*[:=]\s*["\'][^"\']*["\']',
        
        # JWT Token
        'jwt_token': r'\beyJ[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\b',
        
        # Cookie值
        'cookie': r'(?:^|;\s*)(?:auth|session|token)=([^;]+)',
        
        # IP地址
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        
        # 身份证号
        'id_card': r'\b\d{17}[\dXx]\b|\b\d{15}\b',
        
        # 银行卡号
        'bank_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4,7}\b'
    }
    
    # 脱敏替换规则
    MASK_REPLACEMENTS = {
        'email': '[EMAIL_MASKED]',
        'phone': '[PHONE_MASKED]', 
        'api_key': '[API_KEY_MASKED]',
        'password': '"password":"[PASSWORD_MASKED]"',
        'jwt_token': '[JWT_TOKEN_MASKED]',
        'cookie': '[COOKIE_VALUE_MASKED]',
        'ip_address': '[IP_ADDRESS_MASKED]',
        'id_card': '[ID_CARD_MASKED]',
        'bank_card': '[BANK_CARD_MASKED]'
    }
    
    @classmethod
    def sanitize(cls, message: Union[str, Dict, Any], level: str = 'info') -> Union[str, Dict, Any]:
        """
        脱敏日志消息
        
        Args:
            message: 待脱敏的消息
            level: 日志级别，debug级别可能保留更多信息
            
        Returns:
            脱敏后的消息
        """
        # debug级别可能需要更多原始信息用于调试
        if level == 'debug':
            # 只脱敏最关键的敏感信息
            critical_patterns = ['password', 'api_key', 'jwt_token']
            patterns_to_use = {k: v for k, v in cls.SENSITIVE_PATTERNS.items() 
                             if k in critical_patterns}
        else:
            patterns_to_use = cls.SENSITIVE_PATTERNS
        
        if isinstance(message, dict):
            return {k: cls.sanitize(v, level) for k, v in message.items()}
        
        if isinstance(message, str):
            sanitized = message
            for pattern_name, pattern in patterns_to_use.items():
                try:
                    sanitized = re.sub(
                        pattern,
                        cls.MASK_REPLACEMENTS[pattern_name],
                        sanitized,
                        flags=re.IGNORECASE
                    )
                except Exception as e:
                    logger.warning(f"Pattern sanitization failed for {pattern_name}: {e}")
            
            return sanitized
        
        return message
    
    @classmethod
    def sanitize_headers(cls, headers: Dict[str, str]) -> Dict[str, str]:
        """
        脱敏HTTP头部信息
        
        Args:
            headers: HTTP头部字典
            
        Returns:
            脱敏后的头部字典
        """
        sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token'
        }
        
        sanitized = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if key_lower in sensitive_headers:
                sanitized[key] = '[HEADER_VALUE_MASKED]'
            else:
                sanitized[key] = value
        
        return sanitized


class ErrorHandler:
    """统一错误处理器"""
    
    # 错误代码到HTTP状态码的映射
    ERROR_CODE_TO_STATUS = {
        ErrorCode.VALIDATION_ERROR: 422,
        ErrorCode.INVALID_INPUT: 400,
        ErrorCode.AUTHENTICATION_ERROR: 401,
        ErrorCode.AUTHORIZATION_ERROR: 403,
        ErrorCode.TOKEN_EXPIRED: 401,
        ErrorCode.NOT_FOUND: 404,
        ErrorCode.ALREADY_EXISTS: 409,
        ErrorCode.DATABASE_ERROR: 500,
        ErrorCode.DATABASE_CONNECTION_ERROR: 503,
        ErrorCode.NETWORK_ERROR: 502,
        ErrorCode.TIMEOUT_ERROR: 408,
        ErrorCode.BUSINESS_LOGIC_ERROR: 400,
        ErrorCode.OPERATION_NOT_ALLOWED: 403,
        ErrorCode.INTERNAL_ERROR: 500,
        ErrorCode.SERVICE_UNAVAILABLE: 503,
        ErrorCode.THIRD_PARTY_ERROR: 502,
        ErrorCode.API_RATE_LIMIT: 429
    }
    
    @staticmethod
    def create_error_response(
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> JSONResponse:
        """
        创建标准化错误响应
        
        Args:
            error_code: 错误代码
            message: 错误消息
            details: 详细信息
            request_id: 请求ID
            status_code: HTTP状态码（可选，会根据error_code自动推断）
            
        Returns:
            FastAPI JSON响应对象
        """
        if status_code is None:
            status_code = ErrorHandler.ERROR_CODE_TO_STATUS.get(error_code, 500)
        
        error_response = ErrorResponse(
            error_code=error_code,
            message=message,
            details=details,
            timestamp=datetime.utcnow().isoformat(),
            request_id=request_id or str(uuid.uuid4()),
            documentation_url=f"https://docs.example.com/errors/{error_code}"
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error_response.dict()
        )
    
    @staticmethod
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        全局异常处理器
        
        Args:
            request: FastAPI请求对象
            exc: 异常对象
            
        Returns:
            错误响应
        """
        request_id = str(uuid.uuid4())
        
        # 记录详细的错误日志（内部使用，包含脱敏）
        logger.error(
            f"Global exception handler | "
            f"Request ID: {request_id} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"Headers: {LogSanitizer.sanitize_headers(dict(request.headers))} | "
            f"Error: {LogSanitizer.sanitize(str(exc), 'error')} | "
            f"Traceback: {LogSanitizer.sanitize(traceback.format_exc(), 'error')}"
        )
        
        # 根据异常类型返回不同的响应
        if isinstance(exc, HTTPException):
            return ErrorHandler.create_error_response(
                error_code=ErrorCode.BUSINESS_LOGIC_ERROR,
                message=exc.detail,
                request_id=request_id,
                status_code=exc.status_code
            )
        
        elif isinstance(exc, ValueError) or isinstance(exc, TypeError):
            return ErrorHandler.create_error_response(
                error_code=ErrorCode.INVALID_INPUT,
                message="Invalid input parameters",
                details={"error": str(exc)},
                request_id=request_id,
                status_code=400
            )
        
        elif isinstance(exc, PermissionError):
            return ErrorHandler.create_error_response(
                error_code=ErrorCode.AUTHORIZATION_ERROR,
                message="Insufficient permissions",
                request_id=request_id,
                status_code=403
            )
        
        else:
            # 未知内部错误
            return ErrorHandler.create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Internal server error occurred",
                details={"error_type": type(exc).__name__},
                request_id=request_id,
                status_code=500
            )


# 便捷函数
def create_success_response(
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建标准化成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        request_id: 请求ID
        
    Returns:
        成功响应字典
    """
    response = SuccessResponse(
        success=True,
        data=data,
        message=message,
        timestamp=datetime.utcnow().isoformat(),
        request_id=request_id or str(uuid.uuid4())
    )
    return response.dict()


def sanitize_log(message: Union[str, Dict, Any], level: str = 'info') -> Union[str, Dict, Any]:
    """
    便捷的日志脱敏函数
    
    Args:
        message: 待脱敏的消息
        level: 日志级别
        
    Returns:
        脱敏后的消息
    """
    return LogSanitizer.sanitize(message, level)


def handle_api_exception(
    error_code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    便捷的API异常处理函数
    
    Args:
        error_code: 错误代码
        message: 错误消息
        details: 详细信息
        request_id: 请求ID
        
    Returns:
        错误响应
    """
    return ErrorHandler.create_error_response(error_code, message, details, request_id)