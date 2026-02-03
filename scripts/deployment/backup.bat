@echo off
setlocal

:: 配置
set BACKUP_DIR=backups
set DB_FILE=quark_strm.db
set CONFIG_FILE=config.yaml

:: 获取时间戳
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

:: 创建备份目录
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: 备份数据库
if exist "%DB_FILE%" (
    echo Backing up database...
    copy "%DB_FILE%" "%BACKUP_DIR%\quark_strm_%TIMESTAMP%.db"
) else (
    echo Warning: Database file not found.
)

:: 备份配置文件
if exist "%CONFIG_FILE%" (
    echo Backing up config...
    copy "%CONFIG_FILE%" "%BACKUP_DIR%\config_%TIMESTAMP%.yaml"
) else (
    echo Warning: Config file not found.
)

:: 清理旧备份 (PowerShell)
echo Cleaning up old backups (older than 7 days)...
powershell -Command "Get-ChildItem -Path '%BACKUP_DIR%' -Recurse | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item"

echo Backup completed.
dir "%BACKUP_DIR%" | findstr "%TIMESTAMP%"
endlocal
