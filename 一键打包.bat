@echo off
chcp 65001 >nul
cls
echo.
echo ╔══════════════════════════════════════════╗
echo ║   马里奥手势控制游戏 - 完整打包工具      ║
echo ╚══════════════════════════════════════════╝
echo.

echo [步骤 0/7] 激活Conda环境...
call conda activate mario-game
if %errorlevel% neq 0 (
    echo [错误] 无法激活mario-game环境
    echo 请确认已创建该环境：conda create -n mario-game python=3.10
    pause
    exit /b 1
)
echo [成功] 已激活mario-game环境

echo [步骤 1/7] 检查环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo [步骤 2/7] 安装PyInstaller...
pip install pyinstaller --quiet --disable-pip-version-check

echo [步骤 3/7] 清理旧文件...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist __pycache__ rmdir /s /q __pycache__ 2>nul
if exist src\__pycache__ rmdir /s /q src\__pycache__ 2>nul
echo 清理完成

echo.
echo [步骤 4/7] 打包exe（约10-30分钟）...
echo 正在编译，请耐心等待...
echo.

REM 使用配置好的spec文件进行打包
REM 使用配置好的spec文件进行打包
pyinstaller MarioHandGesture.spec --noconfirm --clean

if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败！请检查上面的错误信息。
    pause
    exit /b 1
)

if %errorlevel% neq 0 (
    echo.
    echo ╔══════════════════════════════════════════╗
    echo ║           打包失败！                     ║
    echo ╚══════════════════════════════════════════╝
    pause
    exit /b 1
)

if not exist "dist\MarioHandGesture.exe" (
    echo [错误] exe文件生成失败
    pause
    exit /b 1
)

echo.
echo [成功] exe文件已生成！

echo.
echo [步骤 5/7] 创建安装程序...
echo.

REM 检查Inno Setup
where iscc >nul 2>&1
if %errorlevel% equ 0 (
    echo 检测到Inno Setup，正在创建安装程序...
    iscc build_tools\installer.iss
    
    if exist "MarioHandGesture_Setup.exe" (
        echo [成功] 安装程序已创建！
    ) else (
        echo [提示] Inno Setup编译失败，但exe已成功打包
    )
) else (
    REM 检查NSIS
    where makensis >nul 2>&1
    if %errorlevel% equ 0 (
        echo 检测到NSIS，正在创建安装程序...
        makensis build_tools\installer.nsi
        
        if exist "MarioHandGesture_Setup.exe" (
            echo [成功] 安装程序已创建！
        ) else (
            echo [提示] NSIS编译失败，但exe已成功打包
        )
    ) else (
        echo [提示] 未检测到安装程序工具
        echo.
        echo 如需创建安装程序，请安装：
        echo   - Inno Setup: https://jrsoftware.org/isdl.php
        echo   - NSIS: https://nsis.sourceforge.io/
    )
)

echo.
echo [步骤 6/7] 验证打包结果...
echo.

REM 显示文件信息
if exist "dist\MarioHandGesture.exe" (
    echo ╔══════════════════════════════════════════╗
    echo ║          打包成功！                      ║
    echo ╚══════════════════════════════════════════╝
    echo.
    echo 输出文件：
    for %%A in (dist\MarioHandGesture.exe) do (
        echo   ✓ dist\MarioHandGesture.exe
        echo     大小: %%~zA 字节
    )
    if exist "MarioHandGesture_Setup.exe" (
        echo   ✓ MarioHandGesture_Setup.exe ^(安装程序^)
    )
    echo.
    echo ══════════════════════════════════════════════
    echo 使用方法：
    echo ══════════════════════════════════════════════
    echo.
    echo 方式1：直接运行
    echo   cd dist
    echo   MarioHandGesture.exe
    echo.
    if exist "MarioHandGesture_Setup.exe" (
echo 方式2：安装后运行
echo   MarioHandGesture_Setup.exe
echo   选择安装路径
echo   安装完成
    )
    echo.
    echo ══════════════════════════════════════════════
    echo 注意事项：
    echo ══════════════════════════════════════════════
    echo   • 文件较大（约1-2GB）
    echo   • 首次运行需要摄像头权限
    echo   • 可能被杀毒软件误报，请添加白名单
    echo   • 如遇问题，请查看 打包指南.md
    echo.
)

pause
