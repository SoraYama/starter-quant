@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM CryptoQuantBot 部署脚本 (Windows)
REM 一键部署加密货币量化交易应用

echo 🚀 CryptoQuantBot 部署脚本启动...
echo ================================
echo.

REM 检查系统要求
echo [INFO] 检查系统要求...
echo [INFO] 检测到操作系统: Windows

REM 检查Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker 未安装，请先安装 Docker Desktop
    echo 下载链接: https://docs.docker.com/desktop/windows/install/
    pause
    exit /b 1
)
echo [SUCCESS] Docker 已安装

REM 检查Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose 未安装，请先安装 Docker Compose
    echo 安装链接: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)
echo [SUCCESS] Docker Compose 已安装

REM 检查Node.js (可选)
node --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Node.js 未安装，将使用 Docker 环境
) else (
    echo [SUCCESS] Node.js 已安装
)

REM 检查Python (可选)
python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python 未安装，将使用 Docker 环境
) else (
    echo [SUCCESS] Python 已安装
)

echo.

REM 创建必要目录
echo [INFO] 创建必要目录...
if not exist "data\db" mkdir data\db
if not exist "data\logs" mkdir data\logs
if not exist "data\backups" mkdir data\backups
if not exist "static" mkdir static
echo [SUCCESS] 目录创建完成

REM 设置环境变量
echo [INFO] 设置环境变量...
if not exist ".env" (
    (
    echo # CryptoQuantBot 环境配置
    echo NODE_ENV=production
    echo PYTHONPATH=/app
    echo.
    echo # 数据库配置
    echo DATABASE_URL=sqlite:///./data/crypto_bot.db
    echo.
    echo # Redis配置
    echo REDIS_URL=redis://redis:6379
    echo.
    echo # 币安API配置 ^(可选^)
    echo BINANCE_API_MODE=PUBLIC_MODE
    echo BINANCE_API_KEY=
    echo BINANCE_API_SECRET=
    echo BINANCE_TESTNET=true
    echo.
    echo # 支持的交易对
    echo BINANCE_SYMBOLS=BTCUSDT,ETHUSDT
    echo BINANCE_DEFAULT_INTERVAL=4h
    echo.
    echo # 服务端口
    echo BACKEND_PORT=8000
    echo FRONTEND_PORT=3000
    ) > .env
    echo [SUCCESS] 创建默认 .env 配置文件
) else (
    echo [INFO] 使用现有 .env 配置文件
)

echo.

REM 构建和启动服务
echo [INFO] 构建和启动服务...

REM 停止现有服务
echo [INFO] 停止现有服务...
docker-compose down 2>nul

REM 构建镜像
echo [INFO] 构建 Docker 镜像...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Docker 镜像构建失败
    pause
    exit /b 1
)

REM 启动服务
echo [INFO] 启动服务...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] 服务启动失败
    pause
    exit /b 1
)
echo [SUCCESS] 服务启动完成

echo.

REM 等待服务就绪
echo [INFO] 等待服务就绪...
set /a attempt=0
set /a max_attempts=30
set backend_ready=false
set frontend_ready=false

:wait_loop
if !attempt! geq !max_attempts! goto :wait_done

REM 检查后端服务
if "!backend_ready!"=="false" (
    curl -sf http://localhost:8000/ >nul 2>&1
    if not errorlevel 1 (
        echo [SUCCESS] 后端服务已就绪
        set backend_ready=true
    )
)

REM 检查前端服务
if "!frontend_ready!"=="false" (
    curl -sf http://localhost:3000/ >nul 2>&1
    if not errorlevel 1 (
        echo [SUCCESS] 前端服务已就绪
        set frontend_ready=true
    )
)

if "!backend_ready!"=="true" if "!frontend_ready!"=="true" goto :wait_done

echo|set /p=.
timeout /t 2 /nobreak >nul
set /a attempt+=1
goto :wait_loop

:wait_done
echo.

if "!backend_ready!"=="false" (
    echo [WARNING] 后端服务启动超时，请检查日志
)

if "!frontend_ready!"=="false" (
    echo [WARNING] 前端服务启动超时，请检查日志
)

echo.

REM 显示部署结果
echo [INFO] 部署完成信息:
echo ================================
echo.
echo 📊 应用访问地址:
echo    前端界面: http://localhost:3000
echo    后端API:  http://localhost:8000
echo    API文档:  http://localhost:8000/docs
echo.
echo 🔧 管理命令:
echo    查看状态: docker-compose ps
echo    查看日志: docker-compose logs -f
echo    停止服务: docker-compose down
echo    重启服务: docker-compose restart
echo.
echo 📁 数据目录:
echo    数据库: .\data\db\
echo    日志: .\data\logs\
echo    备份: .\data\backups\
echo.
echo ⚙️  配置文件:
echo    环境变量: .env
echo    后端配置: backend\config.yaml
echo    API密钥指南: ..\binance_api_guide.md
echo.
echo 📋 当前服务状态:
docker-compose ps
echo.
echo 🎉 CryptoQuantBot 部署完成!
echo    请访问 http://localhost:3000 开始使用
echo.

pause
