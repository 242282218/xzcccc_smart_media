#!/bin/bash

# 备份脚本
# 用法: ./backup.sh

set -e

# 配置
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="quark_strm.db"
CONFIG_FILE="config.yaml"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
if [ -f "$DB_FILE" ]; then
    echo "Backing up database..."
    cp "$DB_FILE" "$BACKUP_DIR/quark_strm_$DATE.db"
else
    echo "Warning: Database file not found."
fi

# 备份配置文件
if [ -f "$CONFIG_FILE" ]; then
    echo "Backing up config..."
    cp "$CONFIG_FILE" "$BACKUP_DIR/config_$DATE.yaml"
else
    echo "Warning: Config file not found."
fi

# 清理旧备份 (保留 7 天)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "quark_strm_*.db" -mtime +7 -delete
find "$BACKUP_DIR" -name "config_*.yaml" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR"
ls -lh "$BACKUP_DIR" | grep "$DATE"
