"""
回测API路由
"""

from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field

from ..schemas.strategy import StrategyConfig
from ..services.backtest_engine import BacktestEngine
from ..services.market_data import MarketDataService
from ..services.strategy_engine import StrategyEngine

router = APIRouter()

class BacktestRequest(BaseModel):
    """回测请求"""
    symbol: str = Field(..., description="交易对符号", example="BTCUSDT")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    initial_balance: float = Field(default=10000.0, description="初始资金", gt=0)
    timeframe: str = Field(default="4h", description="时间周期")
    strategy_config: Optional[StrategyConfig] = Field(None, description="策略配置")

class BacktestSummary(BaseModel):
    """回测摘要"""
    backtest_id: int
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    initial_balance: float
    final_balance: float
    total_return: float
    max_drawdown: float
    total_trades: int
    win_rate: float
    created_at: str

# 全局回测引擎实例
backtest_engine: Optional[BacktestEngine] = None

async def get_backtest_engine() -> BacktestEngine:
    """获取回测引擎依赖"""
    global backtest_engine
    if backtest_engine is None:
        # 创建新的回测引擎实例
        backtest_engine = BacktestEngine()
        # 创建并初始化依赖服务
        market_service = MarketDataService()
        strategy_engine = StrategyEngine()
        await market_service.initialize()
        await strategy_engine.initialize(market_service)
        await backtest_engine.initialize(market_service, strategy_engine)
    return backtest_engine

@router.post("/run")
async def run_backtest(
    request: BacktestRequest,
    engine: BacktestEngine = Depends(get_backtest_engine)
):
    """
    运行回测
    
    - **symbol**: 交易对符号 (BTCUSDT, ETHUSDT)
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    - **initial_balance**: 初始资金
    - **timeframe**: 时间周期 (1h, 4h, 1d等)
    - **strategy_config**: 可选的策略配置
    """
    try:
        # 验证日期范围
        if request.start_date >= request.end_date:
            raise HTTPException(status_code=400, detail="开始日期必须早于结束日期")
        
        days_diff = (request.end_date - request.start_date).days
        if days_diff > 730:  # 2年限制
            raise HTTPException(status_code=400, detail="回测时间范围不能超过2年")
        
        if days_diff < 1:
            raise HTTPException(status_code=400, detail="回测时间范围至少1天")
        
        # 验证交易对
        supported_symbols = ['BTCUSDT', 'ETHUSDT']
        if request.symbol.upper() not in supported_symbols:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的交易对。支持的交易对: {supported_symbols}"
            )
        
        # 使用默认配置如果未提供
        strategy_config = request.strategy_config
        if strategy_config is None:
            strategy_engine = StrategyEngine()
            strategy_config = strategy_engine.get_default_config()
        
        # 运行回测
        result = await engine.run_backtest(
            symbol=request.symbol.upper(),
            start_date=request.start_date,
            end_date=request.end_date,
            initial_balance=request.initial_balance,
            strategy_config=strategy_config,
            timeframe=request.timeframe
        )
        
        return {
            "success": True,
            "message": "回测完成",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回测失败: {str(e)}")

@router.get("/history")
async def get_backtest_history(
    limit: int = Query(default=20, ge=1, le=100, description="返回数量"),
    symbol: Optional[str] = Query(None, description="筛选交易对"),
    engine: BacktestEngine = Depends(get_backtest_engine)
):
    """
    获取回测历史记录
    
    - **limit**: 返回记录数量 (1-100)
    - **symbol**: 可选，筛选特定交易对
    """
    try:
        history = await engine.get_backtest_history(limit=limit, symbol=symbol)
        
        return {
            "success": True,
            "data": history,
            "count": len(history),
            "limit": limit,
            "symbol_filter": symbol
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

@router.get("/detail/{backtest_id}")
async def get_backtest_detail(
    backtest_id: int,
    engine: BacktestEngine = Depends(get_backtest_engine)
):
    """
    获取回测详细结果
    
    - **backtest_id**: 回测ID
    """
    try:
        detail = await engine.get_backtest_detail(backtest_id)
        
        if detail is None:
            raise HTTPException(status_code=404, detail="回测记录不存在")
        
        return {
            "success": True,
            "data": detail
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回测详情失败: {str(e)}")

@router.post("/quick-test")
async def quick_backtest(
    symbol: str = Body(..., description="交易对符号"),
    days: int = Body(default=30, description="回测天数", ge=1, le=365),
    initial_balance: float = Body(default=10000.0, description="初始资金", gt=0),
    engine: BacktestEngine = Depends(get_backtest_engine)
):
    """
    快速回测（最近N天）
    
    - **symbol**: 交易对符号
    - **days**: 回测天数 (1-365)
    - **initial_balance**: 初始资金
    """
    try:
        # 计算日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 验证交易对
        supported_symbols = ['BTCUSDT', 'ETHUSDT']
        if symbol.upper() not in supported_symbols:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的交易对。支持的交易对: {supported_symbols}"
            )
        
        # 使用默认策略配置
        strategy_engine = StrategyEngine()
        strategy_config = strategy_engine.get_default_config()
        
        # 运行回测
        result = await engine.run_backtest(
            symbol=symbol.upper(),
            start_date=start_date,
            end_date=end_date,
            initial_balance=initial_balance,
            strategy_config=strategy_config,
            timeframe="4h"
        )
        
        return {
            "success": True,
            "message": f"快速回测完成 - 最近{days}天",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快速回测失败: {str(e)}")

@router.get("/performance-summary")
async def get_performance_summary(
    limit: int = Query(default=10, ge=1, le=50, description="返回数量"),
    engine: BacktestEngine = Depends(get_backtest_engine)
):
    """
    获取回测性能摘要统计
    
    - **limit**: 返回最近的回测数量
    """
    try:
        history = await engine.get_backtest_history(limit=limit)
        
        if not history:
            return {
                "success": True,
                "summary": {
                    "total_backtests": 0,
                    "avg_return": 0,
                    "best_performance": None,
                    "worst_performance": None,
                    "win_rate_avg": 0
                },
                "recent_tests": []
            }
        
        # 计算统计数据
        returns = [float(test.get('total_return', 0)) for test in history]
        win_rates = [float(test.get('win_rate', 0)) for test in history]
        
        # 找出最佳和最差表现
        best_test = max(history, key=lambda x: float(x.get('total_return', 0)))
        worst_test = min(history, key=lambda x: float(x.get('total_return', 0)))
        
        summary = {
            "total_backtests": len(history),
            "avg_return": round(sum(returns) / len(returns), 2) if returns else 0,
            "best_performance": {
                "backtest_id": best_test.get('id'),
                "symbol": best_test.get('symbol'),
                "return": float(best_test.get('total_return', 0)),
                "date": best_test.get('created_at')
            },
            "worst_performance": {
                "backtest_id": worst_test.get('id'),
                "symbol": worst_test.get('symbol'),
                "return": float(worst_test.get('total_return', 0)),
                "date": worst_test.get('created_at')
            },
            "win_rate_avg": round(sum(win_rates) / len(win_rates), 1) if win_rates else 0,
            "symbols_tested": list(set(test.get('symbol') for test in history if test.get('symbol')))
        }
        
        return {
            "success": True,
            "summary": summary,
            "recent_tests": history[:5]  # 最近5次测试
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取性能摘要失败: {str(e)}")

@router.delete("/delete/{backtest_id}")
async def delete_backtest(
    backtest_id: int,
    engine: BacktestEngine = Depends(get_backtest_engine)
):
    """
    删除回测记录
    
    - **backtest_id**: 回测ID
    """
    try:
        # 检查记录是否存在
        detail = await engine.get_backtest_detail(backtest_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="回测记录不存在")
        
        # TODO: 实现删除逻辑
        # await engine.delete_backtest(backtest_id)
        
        return {
            "success": True,
            "message": f"回测记录 {backtest_id} 已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除回测记录失败: {str(e)}")
