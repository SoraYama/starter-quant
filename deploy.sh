#!/bin/bash

# CryptoQuantBot 部署脚本 (Linux/Mac)
# 一键部署加密货币量化交易应用

set -e

echo "🚀 CryptoQuantBot 部署脚本启动..."
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    OS="$(uname -s)"
    case "${OS}" in
        Linux*)     MACHINE=Linux;;
        Darwin*)    MACHINE=Mac;;
        *)          MACHINE="UNKNOWN:${OS}"
    esac
    log_info "检测到操作系统: ${MACHINE}"
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        echo "安装链接: https://docs.docker.com/get-docker/"
        exit 1
    fi
    log_success "Docker 已安装: $(docker --version)"
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        echo "安装链接: https://docs.docker.com/compose/install/"
        exit 1
    fi
    log_success "Docker Compose 已安装: $(docker-compose --version)"
    
    # 检查Node.js (可选)
    if command -v node &> /dev/null; then
        log_success "Node.js 已安装: $(node --version)"
    else
        log_warning "Node.js 未安装，将使用 Docker 环境"
    fi
    
    # 检查Python (可选)
    if command -v python3 &> /dev/null; then
        log_success "Python3 已安装: $(python3 --version)"
    else
        log_warning "Python3 未安装，将使用 Docker 环境"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p data/db
    mkdir -p data/logs
    mkdir -p data/backups
    mkdir -p static
    
    log_success "目录创建完成"
}

# 设置环境变量
setup_environment() {
    log_info "设置环境变量..."
    
    # 如果不存在.env文件，创建默认配置
    if [ ! -f .env ]; then
        cat > .env << EOF
# CryptoQuantBot 环境配置
NODE_ENV=production
PYTHONPATH=/app

# 数据库配置
DATABASE_URL=sqlite:///./data/crypto_bot.db

# Redis配置
REDIS_URL=redis://redis:6379

# 币安API配置 (可选)
BINANCE_API_MODE=PUBLIC_MODE
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_TESTNET=true

# 支持的交易对
BINANCE_SYMBOLS=BTCUSDT,ETHUSDT
BINANCE_DEFAULT_INTERVAL=4h

# 服务端口
BACKEND_PORT=8000
FRONTEND_PORT=3000
EOF
        log_success "创建默认 .env 配置文件"
    else
        log_info "使用现有 .env 配置文件"
    fi
}

# 构建和启动服务
deploy_services() {
    log_info "构建和启动服务..."
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建 Docker 镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    log_info "启动服务..."
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待后端服务
    local backend_ready=false
    local frontend_ready=false
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if ! $backend_ready && curl -sf http://localhost:8000/ >/dev/null 2>&1; then
            log_success "后端服务已就绪"
            backend_ready=true
        fi
        
        if ! $frontend_ready && curl -sf http://localhost:3000/ >/dev/null 2>&1; then
            log_success "前端服务已就绪"
            frontend_ready=true
        fi
        
        if $backend_ready && $frontend_ready; then
            break
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo ""
    
    if ! $backend_ready; then
        log_warning "后端服务启动超时，请检查日志"
    fi
    
    if ! $frontend_ready; then
        log_warning "前端服务启动超时，请检查日志"
    fi
}

# 显示部署结果
show_deployment_info() {
    log_info "部署完成信息:"
    echo "================================"
    
    echo "📊 应用访问地址:"
    echo "   前端界面: http://localhost:3000"
    echo "   后端API:  http://localhost:8000"
    echo "   API文档:  http://localhost:8000/docs"
    echo ""
    
    echo "🔧 管理命令:"
    echo "   查看状态: docker-compose ps"
    echo "   查看日志: docker-compose logs -f"
    echo "   停止服务: docker-compose down"
    echo "   重启服务: docker-compose restart"
    echo ""
    
    echo "📁 数据目录:"
    echo "   数据库: ./data/db/"
    echo "   日志: ./data/logs/"
    echo "   备份: ./data/backups/"
    echo ""
    
    echo "⚙️  配置文件:"
    echo "   环境变量: .env"
    echo "   后端配置: backend/config.yaml"
    echo "   API密钥指南: ../binance_api_guide.md"
    echo ""
    
    # 显示服务状态
    echo "📋 当前服务状态:"
    docker-compose ps
    
    echo ""
    echo "🎉 CryptoQuantBot 部署完成!"
    echo "   请访问 http://localhost:3000 开始使用"
}

# 主函数
main() {
    echo "CryptoQuantBot - 加密货币量化交易应用"
    echo "支持平台: Linux, macOS"
    echo ""
    
    # 执行部署步骤
    check_requirements
    create_directories
    setup_environment
    deploy_services
    wait_for_services
    show_deployment_info
    
    log_success "部署脚本执行完成!"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请查看上面的错误信息"' ERR

# 执行主函数
main "$@"
