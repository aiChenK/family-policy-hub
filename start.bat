@echo off
chcp 65001 > nul
setlocal

:: 切换至当前脚本所在目录
cd /d "%~dp0"

echo =================================================
echo   🏠 正在启动家庭保险管理系统 (Windows)...
echo =================================================

:: 检测 Python 是否可用 (优先检测 python, 其次 py, 再次 python3)
set "PY_CMD="

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=python"
    goto :FOUND
)

py -3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=py -3"
    goto :FOUND
)

python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=python3"
    goto :FOUND
)

:NOT_FOUND
echo ❌ 错误: 未检测到系统安装的 Python，请先安装 Python 3 (https://www.python.org/)。
echo 注意: 安装时请务必勾选 "Add python.exe to PATH" (添加到系统环境变量)。
echo.
pause
exit /b 1

:FOUND
echo 正在使用命令: %PY_CMD%
echo 启动服务中，启动后请在浏览器访问 http://localhost:8088
echo 按 Ctrl+C 可停止服务
echo -------------------------------------------------

if not exist "frontend\dist" (
    where npm >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo 📦 首次检测到未构建前端，正在自动编译前端资源...
        call npm --prefix frontend install
        call npm --prefix frontend run build
    )
)

%PY_CMD% backend\main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 服务异常退出，请查看上方报错信息。
    pause
)
