"""
CryptoQuantBot - 加密货币量化交易应用主程序
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from app.core.config import get_settings
from app.core.database import init_database
from app.api import market, strategy, backtest, trading
from app.services.websocket_manager import websocket_manager
from app.services.market_data import MarketDataService
from app.services.strategy_engine import StrategyEngine
from app.services.backtest_engine import BacktestEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局服务实例
market_service: MarketDataService = None
strategy_engine: StrategyEngine = None
backtest_engine: BacktestEngine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global market_service, strategy_engine, backtest_engine

    # 启动时初始化
    logger.info("🚀 Starting CryptoQuantBot...")

    try:
        # 初始化数据库
        await init_database()
        logger.info("✅ Database initialized")

        # 初始化市场数据服务
        market_service = MarketDataService()
        await market_service.initialize()
        logger.info("✅ Market data service initialized")

        # 初始化策略引擎
        strategy_engine = StrategyEngine()
        await strategy_engine.initialize(market_service)
        logger.info("✅ Strategy engine initialized")

        # 初始化回测引擎
        backtest_engine = BacktestEngine()
        await backtest_engine.initialize(market_service, strategy_engine)
        logger.info("✅ Backtest engine initialized")

        # 启动实时数据更新
        await market_service.start_real_time_data()
        logger.info("✅ Real-time data updates started")

        # 启动WebSocket管理器
        websocket_manager.is_running = True
        logger.info("✅ WebSocket manager started")

        logger.info("🎉 CryptoQuantBot started successfully!")

        yield

    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise

    # 关闭时清理
    logger.info("🛑 Shutting down CryptoQuantBot...")

    try:
        # 关闭服务
        if market_service:
            await market_service.close()

        # 关闭WebSocket连接
        await websocket_manager.close_all()

        logger.info("✅ CryptoQuantBot shutdown complete")

    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# 创建FastAPI应用
app = FastAPI(
    title="CryptoQuantBot API",
    description="加密货币量化交易应用后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(market.router, prefix="/api/market", tags=["市场数据"])
app.include_router(strategy.router, prefix="/api/strategy", tags=["策略分析"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["回测"])
app.include_router(trading.router, prefix="/api/trading", tags=["交易"])

# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    client_id = None
    try:
        # 从查询参数获取客户端ID
        client_id = websocket.query_params.get('client_id')

        await websocket_manager.connect(websocket, client_id)
        logger.info(f"WebSocket client connected: {client_id}")

        while True:
            try:
                # 接收客户端消息
                message = await websocket.receive_text()
                await websocket_manager.handle_message(websocket, message)

            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {client_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
                await websocket_manager.send_personal_message({
                    'type': 'error',
                    'message': str(e)
                }, websocket)

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        await websocket_manager.disconnect(websocket)

# 健康检查端点
@app.get("/")
async def health_check():
    """健康检查"""
    settings = get_settings()

    return {
        "message": "CryptoQuantBot API is running",
        "version": "1.0.0",
        "status": "healthy",
        "api_mode": settings.binance_api_mode,
        "supported_symbols": settings.binance_symbols,
        "default_interval": settings.binance_default_interval,
        "features": {
            "market_data": True,
            "strategy_analysis": True,
            "backtesting": True,
            "trading": settings.binance_api_mode == "FULL_MODE",
            "real_time_data": True,
            "websocket": True
        }
    }

# WebSocket状态端点
@app.get("/api/websocket/status")
async def websocket_status():
    """获取WebSocket连接状态"""
    stats = websocket_manager.get_connection_stats()
    return {
        "status": "running" if websocket_manager.is_running else "stopped",
        "stats": stats
    }

# 系统状态端点
@app.get("/api/system/status")
async def system_status():
    """获取系统状态"""
    global market_service, strategy_engine, backtest_engine

    return {
        "system": {
            "status": "running",
            "version": "1.0.0"
        },
        "services": {
            "market_data": market_service is not None,
            "strategy_engine": strategy_engine is not None,
            "backtest_engine": backtest_engine is not None,
            "websocket": websocket_manager.is_running
        },
        "websocket": websocket_manager.get_connection_stats(),
        "settings": {
            "api_mode": get_settings().binance_api_mode,
            "symbols": get_settings().binance_symbols,
            "interval": get_settings().binance_default_interval
        }
    }

# 静态文件服务（生产环境）
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # 开发环境下static目录可能不存在
    pass

if __name__ == "__main__":
    settings = get_settings()
    from app.core.config import detect_api_mode

    api_mode = detect_api_mode()
    logger.info(f"Starting server in {api_mode} mode")
    logger.info(f"Supported symbols: {settings.binance_symbols}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
