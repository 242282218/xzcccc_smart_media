@echo off
setlocal EnableDelayedExpansion
title Quark STRM Launcher
echo ==========================================
echo    Quark STRM Launcher
echo ==========================================
echo.

set BACKEND_PORT=8000
set FRONTEND_PORT=5173
set BACKEND_DIR=%~dp0..
set FRONTEND_DIR=%~dp0..\web

:: ============================================
:: Main Script Start
:: ============================================

echo [1/4] Checking backend port...
:check_backend_port
netstat -ano | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [i] Port %BACKEND_PORT% is occupied, switching to backup port...
    if %BACKEND_PORT% equ 8000 set BACKEND_PORT=8001
    if %BACKEND_PORT% equ 8001 set BACKEND_PORT=8002
    if %BACKEND_PORT% equ 8002 set BACKEND_PORT=8080
    if %BACKEND_PORT% equ 8080 set BACKEND_PORT=8081
    if %BACKEND_PORT% equ 8081 (
        echo [Error] All backend ports are occupied
        pause
        exit /b 1
    )
    goto :check_backend_port
)
echo [OK] Backend will use port: %BACKEND_PORT%
echo.

echo [2/4] Checking frontend port...
:check_frontend_port
netstat -ano | findstr ":%FRONTEND_PORT%" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [i] Port %FRONTEND_PORT% is occupied, switching to backup port...
    if %FRONTEND_PORT% equ 3000 set FRONTEND_PORT=3001
    if %FRONTEND_PORT% equ 3001 set FRONTEND_PORT=3002
    if %FRONTEND_PORT% equ 3002 set FRONTEND_PORT=8080
    if %FRONTEND_PORT% equ 8080 set FRONTEND_PORT=8081
    if %FRONTEND_PORT% equ 8081 (
        echo [Error] All frontend ports are occupied
        pause
        exit /b 1
    )
    goto :check_frontend_port
)
echo [OK] Frontend will use port: %FRONTEND_PORT%
echo.

echo [3/4] Checking Python dependencies...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [Warning] Python dependencies not installed, installing...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [Error] Dependency installation failed
        echo [i] Please manually run: pip install -r requirements.txt
        pause
        exit /b 1
    )
)
echo [OK] Python dependencies check passed
echo.

echo [4/4] Checking Node modules...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [Warning] Frontend dependencies not installed, installing...
    cd /d "%FRONTEND_DIR%"
    call npm install
    if %errorlevel% neq 0 (
        echo [Error] npm install failed
        echo [i] Please manually run: cd web && npm install
        pause
        exit /b 1
    )
    cd /d "%BACKEND_DIR%"
)
echo [OK] Node modules check passed
echo.

echo ==========================================
echo    Starting Services...
echo ==========================================
echo.

echo [i] Starting backend service on port %BACKEND_PORT%...
start "Quark STRM Backend" cmd /k "cd /d "%BACKEND_DIR%" && echo Backend starting on port %BACKEND_PORT%... && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"
timeout /t 3 /nobreak >nul
echo [OK] Backend service started
echo.

echo [i] Starting frontend service on port %FRONTEND_PORT%...
start "Quark STRM Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && echo Frontend starting on port %FRONTEND_PORT%... && npm run dev -- --port %FRONTEND_PORT%"
timeout /t 2 /nobreak >nul
echo [OK] Frontend service started
echo.

echo ==========================================
echo    All services started successfully!
echo ==========================================
echo.
echo Access URLs:
echo   - Frontend: http://localhost:%FRONTEND_PORT%
echo   - Backend API: http://localhost:%BACKEND_PORT%
echo   - API Docs: http://localhost:%BACKEND_PORT%/docs
echo.
echo Default login:
echo   - Username: admin
echo   - Password: admin
echo.
echo To stop services:
echo   - Run: stop-all.bat
echo   - Or close the service windows
echo.
echo ==========================================
echo.

echo Press any key to open browser...
pause >nul
start http://localhost:%FRONTEND_PORT%

exit /b 0
