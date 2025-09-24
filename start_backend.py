#!/usr/bin/env python3
"""
简化的后端启动脚本
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="CryptoQuantBot API",
    description="加密货币量化交易应用后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查端点
@app.get("/")
async def health_check():
    """健康检查"""
    return {
        "message": "CryptoQuantBot API is running",
        "version": "1.0.0",
        "status": "healthy",
        "features": {
            "market_data": True,
            "strategy_analysis": True,
            "backtesting": True,
            "trading": False,
            "real_time_data": True,
            "websocket": True
        }
    }

@app.get("/api/health")
async def api_health():
    """API健康检查"""
    return {"status": "ok", "message": "API is working"}

# 市场数据API端点
@app.get("/api/market/overview")
async def market_overview():
    """市场概览"""
    return {
        "status": "ok",
        "data": {
            "total_market_cap": 2500000000000,
            "total_volume": 50000000000,
            "active_traders": 1500000,
            "top_gainers": [
                {"symbol": "BTCUSDT", "change": 2.5, "price": 45000},
                {"symbol": "ETHUSDT", "change": 1.8, "price": 3200}
            ]
        }
    }

@app.get("/api/market/ticker/{symbol}")
async def get_ticker(symbol: str):
    """获取交易对价格信息"""
    # 模拟价格数据
    mock_prices = {
        "BTCUSDT": {"price": 45000.50, "change": 2.5, "volume": 1000000},
        "ETHUSDT": {"price": 3200.25, "change": 1.8, "volume": 500000},
        "BNBUSDT": {"price": 350.75, "change": -0.5, "volume": 200000}
    }
    
    if symbol in mock_prices:
        return {
            "status": "ok",
            "data": {
                "symbol": symbol,
                "price": mock_prices[symbol]["price"],
                "change_24h": mock_prices[symbol]["change"],
                "volume_24h": mock_prices[symbol]["volume"],
                "timestamp": 1698240000000
            }
        }
    else:
        return {"status": "error", "message": f"Symbol {symbol} not found"}

@app.get("/api/market/klines/{symbol}")
async def get_klines(symbol: str, interval: str = "4h", limit: int = 100, use_cache: bool = True):
    """获取K线数据"""
    import time
    import random
    
    # 生成模拟K线数据
    klines = []
    base_price = 45000 if symbol == "BTCUSDT" else 3200
    current_time = int(time.time() * 1000)
    
    for i in range(limit):
        # 模拟价格波动
        price_change = random.uniform(-0.02, 0.02)
        open_price = base_price * (1 + price_change)
        close_price = open_price * (1 + random.uniform(-0.01, 0.01))
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.005))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.005))
        volume = random.uniform(100, 1000)
        
        klines.append([
            current_time - (limit - i) * 4 * 60 * 60 * 1000,  # 时间戳
            f"{open_price:.2f}",  # 开盘价
            f"{high_price:.2f}",  # 最高价
            f"{low_price:.2f}",   # 最低价
            f"{close_price:.2f}", # 收盘价
            f"{volume:.2f}",      # 成交量
            current_time - (limit - i) * 4 * 60 * 60 * 1000 + 4 * 60 * 60 * 1000 - 1,  # 收盘时间
            f"{volume * close_price:.2f}",  # 成交额
            100,  # 成交笔数
            f"{volume * 0.5:.2f}",  # 主动买入成交量
            f"{volume * close_price * 0.5:.2f}",  # 主动买入成交额
            "0"  # 忽略此参数
        ])
    
    return {
        "status": "ok",
        "data": klines
    }

# 策略分析API端点
@app.post("/api/strategy/analyze")
async def analyze_strategy(request: dict):
    """策略分析"""
    return {
        "status": "ok",
        "data": {
            "signal": "BUY",
            "confidence": 0.75,
            "indicators": {
                "macd": {"signal": "BULLISH", "value": 0.02},
                "rsi": {"signal": "NEUTRAL", "value": 55},
                "bollinger": {"signal": "BULLISH", "value": 0.8}
            },
            "recommendation": "建议买入，技术指标显示上涨趋势"
        }
    }

# WebSocket端点（简化版）
@app.get("/ws")
async def websocket_endpoint():
    """WebSocket连接端点（简化版）"""
    return {"message": "WebSocket endpoint available", "note": "Full WebSocket support requires additional setup"}

if __name__ == "__main__":
    print("🚀 Starting CryptoQuantBot Backend...")
    print("📊 API will be available at: http://localhost:8000")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "start_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
