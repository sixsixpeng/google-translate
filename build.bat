@echo off
chcp 65001 >nul
title 翻译工具 - 一键构建打包

echo ============================================
echo    翻译工具 - 一键构建打包
echo ============================================
echo.

:: ========== 1. 检查 Python ==========
echo [1/6] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
python --version
echo.

:: ========== 2. 创建虚拟环境 ==========
set VENV_DIR=%~dp0.venv

if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [2/6] 虚拟环境已存在，跳过创建
) else (
    echo [2/6] 创建虚拟环境...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功: %VENV_DIR%
)
echo.

:: ========== 3. 激活虚拟环境 ==========
echo [3/6] 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)
echo 虚拟环境已激活
echo.

:: ========== 4. 升级 pip ==========
echo [4/6] 升级 pip...
python -m pip install --upgrade pip -q
echo.

:: ========== 5. 安装依赖 ==========
echo [5/6] 安装项目依赖...
pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo 依赖安装完成
echo.

:: ========== 6. 打包 ==========
echo [6/6] 开始打包（nicegui-pack）...

:: 清理旧构建
if exist "%~dp0dist" rmdir /s /q "%~dp0dist"
if exist "%~dp0build" rmdir /s /q "%~dp0build"

nicegui-pack --onefile --windowed --name "翻译工具" --add-data "app;app" "%~dp0main.py"

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！请检查上方错误信息
    pause
    exit /b 1
)

echo.
echo ============================================
echo    打包完成！
echo    虚拟环境: %VENV_DIR%
echo    输出目录: %~dp0dist\
echo ============================================
echo.

:: 自动打开 dist 目录
explorer "%~dp0dist"
pause
