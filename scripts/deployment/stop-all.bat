@echo off
setlocal EnableDelayedExpansion
title Quark STRM Stopper
echo ==========================================
echo    Quark STRM Stopper
echo ==========================================
echo.

set "STOPPED_COUNT=0"

:: ============================================
:: Main Script Start
:: ============================================

echo [1/2] Stopping Node.js (frontend) processes...
for /f "tokens=2" %%a in ('tasklist ^| findstr /I "node.exe"') do (
    set "pid=%%a"
    echo [i] Stopping Node.js process (PID: !pid!)...
    taskkill /F /PID !pid! >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Node.js process stopped
        set /a "STOPPED_COUNT+=1"
    ) else (
        echo [Error] Failed to stop process !pid!
    )
)
echo.

echo [2/2] Stopping Python (backend) processes...
for /f "tokens=2" %%a in ('tasklist ^| findstr /I "python.exe"') do (
    set "pid=%%a"
    echo [i] Stopping Python process (PID: !pid!)...
    taskkill /F /PID !pid! >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Python process stopped
        set /a "STOPPED_COUNT+=1"
    ) else (
        echo [Error] Failed to stop process !pid!
    )
)
echo.

echo ==========================================
if %STOPPED_COUNT% gtr 0 (
    echo    Stopped %STOPPED_COUNT% process(es) successfully!
) else (
    echo    No running processes found.
)
echo ==========================================
echo.

pause
exit /b 0
