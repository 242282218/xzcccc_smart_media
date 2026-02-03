"""
配置加密模块

提供敏感配置项的加密和解密功能
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ConfigEncryption:
    """
    配置加密器，使用Fernet对称加密算法
    """
    
    def __init__(self, password: str = None):
        """
        初始化加密器
        
        Args:
            password: 用于生成加密密钥的密码，如果未提供则从环境变量获取
        """
        if password is None:
            password = os.getenv('CONFIG_ENCRYPTION_PASSWORD', '')
        
        if not password:
            raise ValueError("加密密码不能为空，请设置 CONFIG_ENCRYPTION_PASSWORD 环境变量")
        
        self.key = self._derive_key(password.encode())
        self.cipher_suite = Fernet(self.key)
    
    def _derive_key(self, password: bytes) -> bytes:
        """
        从密码派生加密密钥
        
        Args:
            password: 密码字节
            
        Returns:
            加密密钥字节
        """
        salt = b'static_salt_for_smart_media_config_encryption'  # 在生产环境中应使用随机盐
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密明文
        
        Args:
            plaintext: 待加密的明文
            
        Returns:
            加密后的字符串（Base64编码）
        """
        ciphertext = self.cipher_suite.encrypt(plaintext.encode())
        return base64.b64encode(ciphertext).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        解密密文
        
        Args:
            encrypted_text: 待解密的字符串（Base64编码）
            
        Returns:
            解密后的明文
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")


def get_encrypted_config_value(config_value: str, encryption_password: str = None) -> str:
    """
    加密配置值
    
    Args:
        config_value: 配置值
        encryption_password: 加密密码
        
    Returns:
        加密后的配置值
    """
    if not config_value:
        return config_value
    
    try:
        encryptor = ConfigEncryption(encryption_password)
        return f"encrypted:{encryptor.encrypt(config_value)}"
    except Exception:
        # 如果加密失败，返回原始值（这在某些情况下可能是必要的）
        return config_value


def get_decrypted_config_value(encrypted_config_value: str, encryption_password: str = None) -> str:
    """
    解密配置值
    
    Args:
        encrypted_config_value: 加密的配置值
        encryption_password: 加密密码
        
    Returns:
        解密后的配置值
    """
    if not encrypted_config_value or not encrypted_config_value.startswith("encrypted:"):
        return encrypted_config_value
    
    try:
        encrypted_part = encrypted_config_value[10:]  # 移除 "encrypted:" 前缀
        encryptor = ConfigEncryption(encryption_password)
        return encryptor.decrypt(encrypted_part)
    except Exception:
        # 如果解密失败，抛出异常
        raise ValueError("无法解密配置值，请检查加密密码是否正确")


# 示例使用
if __name__ == "__main__":
    # 示例：如何使用加密功能
    password = "my_secure_password_for_config"
    encryptor = ConfigEncryption(password)
    
    # 加密
    secret_data = "my_secret_api_key"
    encrypted = encryptor.encrypt(secret_data)
    print(f"加密后: {encrypted}")
    
    # 解密
    decrypted = encryptor.decrypt(encrypted)
    print(f"解密后: {decrypted}")