#!/usr/bin/env python3
"""
配置加密工具

用于加密敏感配置值的命令行工具
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.encryption import get_encrypted_config_value, ConfigEncryption


def encrypt_value(value: str, password: str = None) -> str:
    """
    加密单个值
    
    Args:
        value: 要加密的值
        password: 加密密码
        
    Returns:
        加密后的值
    """
    if not password:
        password = os.getenv('CONFIG_ENCRYPTION_PASSWORD', '')
        if not password:
            password = input("请输入加密密码: ")
    
    try:
        encrypted_value = get_encrypted_config_value(value, password)
        return encrypted_value
    except Exception as e:
        print(f"加密失败: {e}")
        return None


def interactive_encrypt():
    """交互式加密模式"""
    print("=== 智能媒体项目配置加密工具 ===")
    print("此工具可以帮助您加密敏感配置值")
    print()
    
    while True:
        value = input("请输入要加密的值 (输入 'quit' 退出): ").strip()
        if value.lower() == 'quit':
            break
        
        if not value:
            print("值不能为空，请重新输入")
            continue
        
        password = input("请输入加密密码: ").strip()
        if not password:
            print("密码不能为空，请重新输入")
            continue
        
        encrypted_value = encrypt_value(value, password)
        if encrypted_value:
            print(f"加密结果: {encrypted_value}")
            print()
        else:
            print("加密失败，请重试")
            print()


def main():
    parser = argparse.ArgumentParser(description='配置加密工具')
    parser.add_argument('--value', '-v', type=str, help='要加密的值')
    parser.add_argument('--password', '-p', type=str, help='加密密码')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_encrypt()
    elif args.value:
        if not args.password:
            args.password = os.getenv('CONFIG_ENCRYPTION_PASSWORD', '')
            if not args.password:
                args.password = input("请输入加密密码: ")
        
        encrypted_value = encrypt_value(args.value, args.password)
        if encrypted_value:
            print(f"加密结果: {encrypted_value}")
        else:
            sys.exit(1)
    else:
        print("使用方法:")
        print("  python encrypt_config.py --value 'your_sensitive_value' --password 'your_password'")
        print("  python encrypt_config.py --interactive")
        print("  python encrypt_config.py -v 'your_sensitive_value' -p 'your_password'")
        print()
        print("或者设置环境变量 CONFIG_ENCRYPTION_PASSWORD 后使用:")
        print("  export CONFIG_ENCRYPTION_PASSWORD='your_password'")
        print("  python encrypt_config.py --value 'your_sensitive_value'")


if __name__ == "__main__":
    main()