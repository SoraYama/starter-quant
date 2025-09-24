"""
策略分析API路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from datetime import datetime

from ..schemas.strategy import (
    StrategyConfig, StrategySignalRequest, StrategySignalResponse,
    SignalData, TechnicalIndicators, StrategyStatus
)
from ..services.strategy_engine import StrategyEngine
from ..services.market_data import MarketDataService

router = APIRouter()

# 全局策略引擎实例
strategy_engine: Optional[StrategyEngine] = None

async def get_strategy_engine() -> StrategyEngine:
    """获取策略引擎依赖"""
    global strategy_engine
    if strategy_engine is None:
        # 创建新的策略引擎实例
        strategy_engine = StrategyEngine()
        # 创建并初始化市场数据服务
        market_service = MarketDataService()
        await market_service.initialize()
        await strategy_engine.initialize(market_service)
    return strategy_engine

@router.post("/analyze", response_model=StrategySignalResponse)
async def analyze_symbol(
    request: StrategySignalRequest,
    engine: StrategyEngine = Depends(get_strategy_engine)
):
    """
    分析交易对并生成技术指标和信号
    
    - **symbol**: 交易对符号 (如: BTCUSDT, ETHUSDT)
    - **timeframe**: 时间周期 (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w)
    - **limit**: K线数据条数 (50-1000)
    - **config**: 可选的策略配置参数
    """
    try:
        # 验证配置
        config = request.config or engine.get_default_config()
        if not engine.validate_config(config):
            raise HTTPException(status_code=400, detail="Invalid strategy configuration")
        
        # 执行分析
        result = await engine.analyze_symbol(
            symbol=request.symbol.upper(),
            timeframe=request.timeframe,
            limit=request.limit,
            config=config
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Analysis failed'))
        
        return StrategySignalResponse(
            success=True,
            signals=result['signals'],
            indicators=result['indicators'],
            symbol=result['symbol'],
            timeframe=result['timeframe'],
            strategy_config=result['config']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.get("/signals/{symbol}")
async def get_latest_signals(
    symbol: str,
    timeframe: str = Query(default="4h", description="时间周期"),
    limit: int = Query(default=10, ge=1, le=50, description="信号数量"),
    engine: StrategyEngine = Depends(get_strategy_engine)
):
    """
    获取最新的交易信号
    
    - **symbol**: 交易对符号
    - **timeframe**: 时间周期
    - **limit**: 返回信号数量
    """
    try:
        signals = await engine.get_latest_signals(
            symbol=symbol.upper(),
            timeframe=timeframe
        )
        
        # 限制返回数量
        limited_signals = signals[-limit:] if len(signals) > limit else signals
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "signals": limited_signals,
            "total_count": len(limited_signals),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting signals: {str(e)}")

@router.get("/indicators/{symbol}")
async def get_current_indicators(
    symbol: str,
    timeframe: str = Query(default="4h", description="时间周期"),
    engine: StrategyEngine = Depends(get_strategy_engine)
):
    """
    获取当前技术指标值
    
    - **symbol**: 交易对符号
    - **timeframe**: 时间周期
    """
    try:
        indicators = await engine.get_current_indicators(
            symbol=symbol.upper(),
            timeframe=timeframe
        )
        
        if indicators is None:
            raise HTTPException(status_code=404, detail="Indicators not found")
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicators": indicators,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting indicators: {str(e)}")

@router.get("/strength/{symbol}")
async def evaluate_signal_strength(
    symbol: str,
    timeframe: str = Query(default="4h", description="时间周期"),
    engine: StrategyEngine = Depends(get_strategy_engine)
):
    """
    评估交易信号强度
    
    - **symbol**: 交易对符号
    - **timeframe**: 时间周期
    
    返回信号强度: strong_buy, buy, neutral, sell, strong_sell
    """
    try:
        evaluation = await engine.evaluate_signal_strength(
            symbol=symbol.upper(),
            timeframe=timeframe
        )
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            **evaluation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating strength: {str(e)}")

@router.post("/batch-analyze")
async def batch_analyze_symbols(
    symbols: List[str] = Body(..., description="交易对符号列表"),
    timeframe: str = Body(default="4h", description="时间周期"),
    config: Optional[StrategyConfig] = Body(None, description="策略配置"),
    engine: StrategyEngine = Depends(get_strategy_engine)
):
    """
    批量分析多个交易对
    
    - **symbols**: 交易对符号列表
    - **timeframe**: 时间周期
    - **config**: 可选的策略配置
    """
    try:
        if len(symbols) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed")
        
        # 验证配置
        if config and not engine.validate_config(config):
            raise HTTPException(status_code=400, detail="Invalid strategy configuration")
        
        # 批量分析
        results = await engine.batch_analyze(
            symbols=[s.upper() for s in symbols],
            timeframe=timeframe,
            config=config
        )
        
        # 统计结果
        success_count = sum(1 for r in results.values() if r.get('success', False))
        total_signals = sum(r.get('signal_count', 0) for r in results.values())
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "total_symbols": len(symbols),
                "successful_analysis": success_count,
                "failed_analysis": len(symbols) - success_count,
                "total_signals": total_signals
            },
            "timeframe": timeframe,
            "analysis_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis error: {str(e)}")

@router.get("/config/default")
async def get_default_config(
    engine: StrategyEngine = Depends(get_strategy_engine)
):
    """
    获取默认策略配置
    """
    try:
        config = engine.get_default_config()
        return {
            "success": True,
            "config": config,
            "description": "Default multi-indicator strategy configuration"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting config: {str(e)}")

@router.post("/config/validate")
async def validate_config(
    config: StrategyConfig,
    engine: StrategyEngine = Depends(get_strategy_engine)
):
    """
    验证策略配置
    """
    try:
        is_valid = engine.validate_config(config)
        
        return {
            "success": True,
            "valid": is_valid,
            "config": config,
            "message": "Configuration is valid" if is_valid else "Configuration validation failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config validation error: {str(e)}")

@router.get("/overview")
async def get_strategy_overview(
    engine: StrategyEngine = Depends(get_strategy_engine)
):
    """
    获取策略引擎概览
    """
    try:
        config = engine.get_default_config()
        
        return {
            "success": True,
            "strategy_name": config.name,
            "description": config.description,
            "supported_indicators": [
                "MACD (Moving Average Convergence Divergence)",
                "RSI (Relative Strength Index)", 
                "Bollinger Bands"
            ],
            "signal_types": ["BUY", "SELL"],
            "timeframes": ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w"],
            "default_config": config,
            "features": [
                "Multi-indicator signal combination",
                "Configurable parameters",
                "Signal strength evaluation",
                "Batch analysis support",
                "Real-time indicator calculation"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting overview: {str(e)}")
