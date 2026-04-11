@echo off
chcp 65001 >nul
title 翻译工具 - 一键构建打包

echo ============================================
echo    翻译工具 - 一键构建打包
echo ============================================
echo.

set VENV_DIR=%~dp0.venv

:: 创建虚拟环境（已存在则跳过）
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [1/5] 创建虚拟环境...
    python -m venv "%VENV_DIR%"
) else (
    echo [1/5] 虚拟环境已存在，跳过创建
)

:: 激活虚拟环境
echo [2/5] 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"

:: 升级 pip
echo [3/5] 升级 pip...
python -m pip install --upgrade pip -q

:: 安装依赖
echo [4/5] 安装项目依赖...
pip install -r "%~dp0requirements.txt" -q

:: 打包
echo [5/5] 开始打包...
if exist "%~dp0dist" rmdir /s /q "%~dp0dist"
if exist "%~dp0build" rmdir /s /q "%~dp0build"

nicegui-pack --onefile --windowed --name "翻译工具" --icon "%~dp0assets\icon.ico" --add-data "app;app" --add-data "assets;assets" "%~dp0main.py"

echo.
echo ============================================
echo    打包完成！输出目录: %~dp0dist\
echo ============================================
echo.

explorer "%~dp0dist"
pause
