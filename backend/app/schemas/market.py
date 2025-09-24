"""
市场数据相关的Pydantic模式
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class KLineData(BaseModel):
    """K线数据模式"""
    symbol: str = Field(..., description="交易对符号")
    timeframe: str = Field(..., description="时间周期")
    open_time: int = Field(..., description="开盘时间戳")
    close_time: int = Field(..., description="收盘时间戳")
    open_price: float = Field(..., description="开盘价")
    high_price: float = Field(..., description="最高价")
    low_price: float = Field(..., description="最低价")
    close_price: float = Field(..., description="收盘价")
    volume: float = Field(..., description="交易量")

class KLineRequest(BaseModel):
    """K线数据请求"""
    symbol: str = Field(..., description="交易对符号", example="BTCUSDT")
    interval: str = Field(default="4h", description="时间间隔", example="4h")
    limit: int = Field(default=500, description="数据条数", ge=1, le=1000)
    start_time: Optional[int] = Field(None, description="开始时间戳")
    end_time: Optional[int] = Field(None, description="结束时间戳")

class KLineResponse(BaseModel):
    """K线数据响应"""
    success: bool = Field(..., description="请求是否成功")
    data: List[KLineData] = Field(..., description="K线数据列表")
    count: int = Field(..., description="数据条数")
    symbol: str = Field(..., description="交易对符号")
    interval: str = Field(..., description="时间间隔")

class TickerData(BaseModel):
    """Ticker数据模式"""
    symbol: str = Field(..., description="交易对符号")
    price: float = Field(..., description="最新价格")
    price_change: float = Field(..., description="价格变化")
    price_change_percent: float = Field(..., description="价格变化百分比")
    high_price: float = Field(..., description="24小时最高价")
    low_price: float = Field(..., description="24小时最低价")
    volume: float = Field(..., description="24小时交易量")
    quote_volume: float = Field(..., description="24小时交易额")
    open_price: float = Field(..., description="24小时开盘价")
    prev_close_price: float = Field(..., description="前收盘价")
    bid_price: float = Field(..., description="买一价")
    ask_price: float = Field(..., description="卖一价")
    timestamp: int = Field(..., description="时间戳")

class MarketDepth(BaseModel):
    """市场深度数据"""
    symbol: str = Field(..., description="交易对符号")
    bids: List[List[float]] = Field(..., description="买单深度")
    asks: List[List[float]] = Field(..., description="卖单深度")
    timestamp: int = Field(..., description="时间戳")

class SymbolInfo(BaseModel):
    """交易对信息"""
    symbol: str = Field(..., description="交易对符号")
    base_asset: str = Field(..., description="基础资产")
    quote_asset: str = Field(..., description="计价资产")
    status: str = Field(..., description="交易状态")
    min_qty: float = Field(..., description="最小交易数量")
    max_qty: float = Field(..., description="最大交易数量")
    step_size: float = Field(..., description="数量精度")
    min_price: float = Field(..., description="最小价格")
    max_price: float = Field(..., description="最大价格")
    tick_size: float = Field(..., description="价格精度")

class MarketOverview(BaseModel):
    """市场概览"""
    total_symbols: int = Field(..., description="总交易对数量")
    active_symbols: int = Field(..., description="活跃交易对数量")
    supported_symbols: List[str] = Field(..., description="支持的交易对列表")
    api_mode: str = Field(..., description="API模式: PUBLIC_MODE/FULL_MODE")
    last_update: datetime = Field(..., description="最后更新时间")
