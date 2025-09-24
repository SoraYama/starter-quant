"""
交易API路由（模拟交易和账户管理）
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.config import get_settings, detect_api_mode

router = APIRouter()

class AccountInfo(BaseModel):
    """账户信息"""
    account_type: str = Field(..., description="账户类型")
    total_balance: float = Field(..., description="总余额")
    available_balance: float = Field(..., description="可用余额")
    locked_balance: float = Field(..., description="锁定余额")
    positions: List[Dict] = Field(default=[], description="持仓列表")
    api_mode: str = Field(..., description="API模式")

class OrderRequest(BaseModel):
    """下单请求"""
    symbol: str = Field(..., description="交易对符号")
    side: str = Field(..., description="交易方向: BUY/SELL")
    quantity: float = Field(..., description="交易数量", gt=0)
    price: Optional[float] = Field(None, description="价格（限价单）")
    order_type: str = Field(default="MARKET", description="订单类型: MARKET/LIMIT")

class OrderResponse(BaseModel):
    """订单响应"""
    order_id: str = Field(..., description="订单ID")
    symbol: str = Field(..., description="交易对符号")
    side: str = Field(..., description="交易方向")
    quantity: float = Field(..., description="交易数量")
    price: float = Field(..., description="成交价格")
    status: str = Field(..., description="订单状态")
    timestamp: int = Field(..., description="时间戳")

@router.get("/account", response_model=AccountInfo)
async def get_account_info():
    """
    获取账户信息
    
    注意：当前为演示模式，返回模拟数据
    """
    try:
        api_mode = detect_api_mode()
        settings = get_settings()
        
        if api_mode == "FULL_MODE":
            # 完整功能模式：可以获取真实账户信息
            # TODO: 集成真实的币安账户API
            return AccountInfo(
                account_type="SPOT",
                total_balance=10000.0,
                available_balance=8500.0,
                locked_balance=1500.0,
                positions=[
                    {
                        "symbol": "BTCUSDT",
                        "quantity": 0.05,
                        "avg_price": 45000.0,
                        "unrealized_pnl": 250.0
                    }
                ],
                api_mode="FULL_MODE"
            )
        else:
            # 公开数据模式：返回演示数据
            return AccountInfo(
                account_type="DEMO",
                total_balance=10000.0,
                available_balance=10000.0,
                locked_balance=0.0,
                positions=[],
                api_mode="PUBLIC_MODE"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账户信息失败: {str(e)}")

@router.post("/order", response_model=OrderResponse)
async def place_order(request: OrderRequest):
    """
    下单交易
    
    注意：当前为演示模式，不会执行真实交易
    
    - **symbol**: 交易对符号 (BTCUSDT, ETHUSDT)
    - **side**: 交易方向 (BUY, SELL)  
    - **quantity**: 交易数量
    - **price**: 价格（限价单时必填）
    - **order_type**: 订单类型 (MARKET, LIMIT)
    """
    try:
        api_mode = detect_api_mode()
        
        # 验证交易对
        supported_symbols = ['BTCUSDT', 'ETHUSDT']
        if request.symbol.upper() not in supported_symbols:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的交易对。支持的交易对: {supported_symbols}"
            )
        
        # 验证订单参数
        if request.side.upper() not in ['BUY', 'SELL']:
            raise HTTPException(status_code=400, detail="交易方向必须是 BUY 或 SELL")
        
        if request.order_type.upper() not in ['MARKET', 'LIMIT']:
            raise HTTPException(status_code=400, detail="订单类型必须是 MARKET 或 LIMIT")
        
        if request.order_type.upper() == 'LIMIT' and request.price is None:
            raise HTTPException(status_code=400, detail="限价单必须指定价格")
        
        if api_mode == "PUBLIC_MODE":
            # 公开数据模式：模拟下单
            return OrderResponse(
                order_id=f"DEMO_{int(datetime.now().timestamp())}",
                symbol=request.symbol.upper(),
                side=request.side.upper(),
                quantity=request.quantity,
                price=request.price or 50000.0,  # 模拟价格
                status="DEMO_FILLED",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
        else:
            # 完整功能模式：真实下单
            # TODO: 集成真实的币安交易API
            raise HTTPException(
                status_code=501,
                detail="真实交易功能尚未实现，请先配置币安API密钥"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下单失败: {str(e)}")

@router.get("/orders")
async def get_order_history(
    symbol: Optional[str] = Query(None, description="筛选交易对"),
    limit: int = Query(default=20, ge=1, le=100, description="返回数量")
):
    """
    获取订单历史
    
    - **symbol**: 可选，筛选特定交易对
    - **limit**: 返回订单数量 (1-100)
    """
    try:
        api_mode = detect_api_mode()
        
        if api_mode == "PUBLIC_MODE":
            # 演示模式：返回模拟订单历史
            demo_orders = [
                {
                    "order_id": f"DEMO_{i}",
                    "symbol": "BTCUSDT" if i % 2 == 0 else "ETHUSDT",
                    "side": "BUY" if i % 3 == 0 else "SELL",
                    "quantity": round(0.01 + (i * 0.005), 6),
                    "price": 45000 + (i * 100),
                    "status": "FILLED",
                    "timestamp": int((datetime.now().timestamp() - i * 3600) * 1000)
                }
                for i in range(min(limit, 10))
            ]
            
            # 按交易对筛选
            if symbol:
                demo_orders = [order for order in demo_orders if order["symbol"] == symbol.upper()]
            
            return {
                "success": True,
                "orders": demo_orders,
                "count": len(demo_orders),
                "api_mode": api_mode
            }
        else:
            # 完整功能模式：获取真实订单历史
            # TODO: 集成真实的币安订单历史API
            return {
                "success": True,
                "orders": [],
                "count": 0,
                "api_mode": api_mode,
                "message": "请配置币安API密钥以获取真实订单历史"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单历史失败: {str(e)}")

@router.get("/positions")
async def get_positions():
    """
    获取当前持仓
    """
    try:
        api_mode = detect_api_mode()
        
        if api_mode == "PUBLIC_MODE":
            # 演示模式：返回模拟持仓
            demo_positions = [
                {
                    "symbol": "BTCUSDT",
                    "side": "LONG",
                    "quantity": 0.05,
                    "avg_price": 45000.0,
                    "current_price": 46000.0,
                    "unrealized_pnl": 50.0,
                    "pnl_percentage": 2.22,
                    "entry_time": int((datetime.now().timestamp() - 86400) * 1000)
                }
            ]
            
            return {
                "success": True,
                "positions": demo_positions,
                "count": len(demo_positions),
                "api_mode": api_mode
            }
        else:
            # 完整功能模式：获取真实持仓
            # TODO: 集成真实的币安持仓API
            return {
                "success": True,
                "positions": [],
                "count": 0,
                "api_mode": api_mode,
                "message": "请配置币安API密钥以获取真实持仓信息"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取持仓失败: {str(e)}")

@router.post("/cancel-order/{order_id}")
async def cancel_order(order_id: str):
    """
    取消订单
    
    - **order_id**: 订单ID
    """
    try:
        api_mode = detect_api_mode()
        
        if api_mode == "PUBLIC_MODE":
            # 演示模式：模拟取消订单
            return {
                "success": True,
                "order_id": order_id,
                "status": "CANCELLED",
                "message": "演示订单已取消",
                "api_mode": api_mode
            }
        else:
            # 完整功能模式：真实取消订单
            # TODO: 集成真实的币安取消订单API
            raise HTTPException(
                status_code=501,
                detail="真实取消订单功能尚未实现，请先配置币安API密钥"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消订单失败: {str(e)}")

@router.get("/trading-status")
async def get_trading_status():
    """
    获取交易状态和配置信息
    """
    try:
        api_mode = detect_api_mode()
        settings = get_settings()
        
        return {
            "success": True,
            "api_mode": api_mode,
            "trading_enabled": api_mode == "FULL_MODE",
            "supported_symbols": settings.binance_symbols,
            "features": {
                "spot_trading": api_mode == "FULL_MODE",
                "futures_trading": False,  # 未实现
                "margin_trading": False,  # 未实现
                "demo_trading": True
            },
            "risk_management": {
                "max_position_size": settings.trading_max_position_size,
                "stop_loss_percent": settings.trading_stop_loss_percent,
                "take_profit_percent": settings.trading_take_profit_percent
            },
            "message": "完整交易功能需要配置币安API密钥" if api_mode == "PUBLIC_MODE" else "交易功能已启用"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易状态失败: {str(e)}")

@router.post("/simulate-trade")
async def simulate_trade(
    symbol: str = Body(..., description="交易对符号"),
    side: str = Body(..., description="交易方向"),
    quantity: float = Body(..., description="交易数量"),
    current_price: float = Body(..., description="当前价格")
):
    """
    模拟交易（用于回测和策略验证）
    
    - **symbol**: 交易对符号
    - **side**: 交易方向 (BUY/SELL)
    - **quantity**: 交易数量
    - **current_price**: 当前价格
    """
    try:
        settings = get_settings()
        
        # 计算交易成本
        trade_value = quantity * current_price
        commission = trade_value * settings.backtest_commission
        slippage = trade_value * settings.backtest_slippage
        total_cost = commission + slippage
        
        # 计算净交易金额
        if side.upper() == "BUY":
            net_amount = trade_value + total_cost
        else:
            net_amount = trade_value - total_cost
        
        return {
            "success": True,
            "simulation": {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "quantity": quantity,
                "price": current_price,
                "trade_value": trade_value,
                "commission": commission,
                "slippage": slippage,
                "total_cost": total_cost,
                "net_amount": net_amount
            },
            "estimated_fees": {
                "commission_rate": settings.backtest_commission,
                "slippage_rate": settings.backtest_slippage,
                "total_fee_rate": settings.backtest_commission + settings.backtest_slippage
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模拟交易计算失败: {str(e)}")
