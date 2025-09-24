"""
市场数据API路由
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from ..schemas.market import (
    KLineRequest, KLineResponse, KLineData, 
    TickerData, MarketOverview, SymbolInfo
)
from ..services.market_data import MarketDataService
from ..core.config import get_settings

router = APIRouter()

# 全局市场数据服务实例
market_service: Optional[MarketDataService] = None

async def get_market_service() -> MarketDataService:
    """获取市场数据服务依赖"""
    global market_service
    if market_service is None:
        market_service = MarketDataService()
        await market_service.initialize()
    return market_service

@router.get("/klines/{symbol}", response_model=KLineResponse)
async def get_klines(
    symbol: str,
    interval: str = Query(default="4h", description="时间间隔"),
    limit: int = Query(default=500, ge=1, le=1000, description="数据条数"),
    start_time: Optional[int] = Query(None, description="开始时间戳"),
    end_time: Optional[int] = Query(None, description="结束时间戳"),
    use_cache: bool = Query(True, description="是否使用缓存"),
    service: MarketDataService = Depends(get_market_service)
):
    """
    获取K线数据
    
    - **symbol**: 交易对符号 (如: BTCUSDT, ETHUSDT)
    - **interval**: 时间间隔 (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w)
    - **limit**: 返回数据条数 (1-1000)
    - **start_time**: 开始时间戳 (毫秒)
    - **end_time**: 结束时间戳 (毫秒)
    - **use_cache**: 是否使用数据库缓存
    """
    try:
        # 验证交易对
        supported_symbols = service.get_supported_symbols()
        if symbol.upper() not in [s.upper() for s in supported_symbols]:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported symbol. Supported symbols: {supported_symbols}"
            )
        
        # 验证时间间隔
        supported_intervals = service.get_supported_intervals()
        if interval not in supported_intervals:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported interval. Supported intervals: {supported_intervals}"
            )
        
        # 获取K线数据
        klines = await service.get_klines(
            symbol=symbol.upper(),
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            use_cache=use_cache
        )
        
        return KLineResponse(
            success=True,
            data=klines,
            count=len(klines),
            symbol=symbol.upper(),
            interval=interval
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/ticker/{symbol}")
async def get_ticker(
    symbol: str,
    service: MarketDataService = Depends(get_market_service)
):
    """
    获取24小时价格统计
    
    - **symbol**: 交易对符号 (如: BTCUSDT, ETHUSDT)
    """
    try:
        # 验证交易对
        supported_symbols = service.get_supported_symbols()
        if symbol.upper() not in [s.upper() for s in supported_symbols]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported symbol. Supported symbols: {supported_symbols}"
            )
        
        # 获取价格信息
        ticker = await service.get_ticker(symbol.upper())
        
        if ticker is None:
            raise HTTPException(status_code=404, detail="Ticker data not found")
        
        return {
            "success": True,
            "data": ticker,
            "symbol": symbol.upper()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    interval: str = Query(default="4h", description="时间间隔"),
    days: int = Query(default=30, ge=1, le=730, description="历史天数"),
    service: MarketDataService = Depends(get_market_service)
):
    """
    获取历史数据（支持大量历史数据）
    
    - **symbol**: 交易对符号 (如: BTCUSDT, ETHUSDT)
    - **interval**: 时间间隔
    - **days**: 历史天数 (1-730天，最多2年)
    """
    try:
        # 验证参数
        supported_symbols = service.get_supported_symbols()
        if symbol.upper() not in [s.upper() for s in supported_symbols]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported symbol. Supported symbols: {supported_symbols}"
            )
        
        supported_intervals = service.get_supported_intervals()
        if interval not in supported_intervals:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported interval. Supported intervals: {supported_intervals}"
            )
        
        # 获取历史数据
        klines = await service.get_historical_data(
            symbol=symbol.upper(),
            interval=interval,
            days=days
        )
        
        return {
            "success": True,
            "data": klines,
            "count": len(klines),
            "symbol": symbol.upper(),
            "interval": interval,
            "days": days,
            "start_date": (datetime.now() - timedelta(days=days)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/overview", response_model=MarketOverview)
async def get_market_overview(
    service: MarketDataService = Depends(get_market_service)
):
    """
    获取市场概览信息
    """
    try:
        overview = await service.get_market_overview()
        return overview
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/symbols")
async def get_supported_symbols(
    service: MarketDataService = Depends(get_market_service)
):
    """
    获取支持的交易对列表
    """
    try:
        symbols = service.get_supported_symbols()
        intervals = service.get_supported_intervals()
        
        return {
            "success": True,
            "symbols": symbols,
            "intervals": intervals,
            "default_interval": get_settings().binance_default_interval
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status")
async def get_market_status():
    """
    获取市场数据服务状态
    """
    try:
        global market_service
        
        if market_service is None:
            return {
                "status": "not_initialized",
                "api_mode": "unknown",
                "supported_symbols": [],
                "message": "Market service not initialized"
            }
        
        overview = await market_service.get_market_overview()
        
        return {
            "status": "running",
            "api_mode": overview.get("api_mode", "unknown"),
            "supported_symbols": overview.get("supported_symbols", []),
            "total_symbols": overview.get("total_symbols", 0),
            "last_update": overview.get("last_update"),
            "message": "Market service is running normally"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Market service error: {str(e)}"
        }

@router.post("/refresh")
async def refresh_market_data(
    symbol: Optional[str] = None,
    service: MarketDataService = Depends(get_market_service)
):
    """
    刷新市场数据缓存
    
    - **symbol**: 可选，指定要刷新的交易对，不指定则刷新所有
    """
    try:
        symbols_to_refresh = [symbol.upper()] if symbol else service.get_supported_symbols()
        
        refreshed_count = 0
        errors = []
        
        for sym in symbols_to_refresh:
            try:
                # 强制从API获取最新数据
                klines = await service.get_klines(
                    symbol=sym,
                    interval=get_settings().binance_default_interval,
                    limit=100,
                    use_cache=False
                )
                
                if klines:
                    refreshed_count += 1
                
            except Exception as e:
                errors.append(f"{sym}: {str(e)}")
        
        return {
            "success": True,
            "refreshed_symbols": refreshed_count,
            "total_symbols": len(symbols_to_refresh),
            "errors": errors,
            "message": f"Successfully refreshed {refreshed_count} symbols"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")
