"""
策略相关的Pydantic模式
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TechnicalIndicators(BaseModel):
    """技术指标数据"""
    timestamp: int = Field(..., description="时间戳")
    macd: Optional[float] = Field(None, description="MACD值")
    macd_signal: Optional[float] = Field(None, description="MACD信号线")
    macd_histogram: Optional[float] = Field(None, description="MACD柱状图")
    rsi: Optional[float] = Field(None, description="RSI值")
    bb_upper: Optional[float] = Field(None, description="布林带上轨")
    bb_middle: Optional[float] = Field(None, description="布林带中轨")
    bb_lower: Optional[float] = Field(None, description="布林带下轨")
    bb_width: Optional[float] = Field(None, description="布林带宽度")

class SignalData(BaseModel):
    """交易信号数据"""
    symbol: str = Field(..., description="交易对符号")
    signal_type: str = Field(..., description="信号类型: BUY/SELL")
    price: float = Field(..., description="信号价格")
    timestamp: int = Field(..., description="信号时间戳")
    confidence: Optional[float] = Field(None, description="信号置信度")
    indicators: Optional[TechnicalIndicators] = Field(None, description="技术指标数据")
    strategy_name: str = Field(..., description="策略名称")
    timeframe: str = Field(..., description="时间周期")
    reason: Optional[str] = Field(None, description="信号原因")

class StrategyConfig(BaseModel):
    """策略配置"""
    name: str = Field(..., description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    
    # MACD参数
    macd_fast_period: int = Field(default=12, description="MACD快线周期")
    macd_slow_period: int = Field(default=26, description="MACD慢线周期")
    macd_signal_period: int = Field(default=9, description="MACD信号线周期")
    
    # RSI参数
    rsi_period: int = Field(default=14, description="RSI周期")
    rsi_oversold: int = Field(default=30, description="RSI超卖阈值")
    rsi_overbought: int = Field(default=70, description="RSI超买阈值")
    
    # 布林带参数
    bb_period: int = Field(default=20, description="布林带周期")
    bb_std_dev: float = Field(default=2.0, description="布林带标准差")
    
    # 风险管理
    stop_loss_percent: float = Field(default=2.0, description="止损百分比")
    take_profit_percent: float = Field(default=4.0, description="止盈百分比")
    max_position_size: float = Field(default=0.1, description="最大仓位比例")

class StrategySignalRequest(BaseModel):
    """策略信号请求"""
    symbol: str = Field(..., description="交易对符号")
    timeframe: str = Field(default="4h", description="时间周期")
    limit: int = Field(default=100, description="K线数据条数")
    config: Optional[StrategyConfig] = Field(None, description="策略配置")

class StrategySignalResponse(BaseModel):
    """策略信号响应"""
    success: bool = Field(..., description="请求是否成功")
    signals: List[SignalData] = Field(..., description="信号列表")
    indicators: List[TechnicalIndicators] = Field(..., description="技术指标列表")
    symbol: str = Field(..., description="交易对符号")
    timeframe: str = Field(..., description="时间周期")
    strategy_config: StrategyConfig = Field(..., description="使用的策略配置")

class StrategyStatus(BaseModel):
    """策略状态"""
    name: str = Field(..., description="策略名称")
    status: str = Field(..., description="状态: RUNNING/STOPPED/ERROR")
    symbol: str = Field(..., description="交易对符号")
    timeframe: str = Field(..., description="时间周期")
    last_signal: Optional[SignalData] = Field(None, description="最后信号")
    total_signals: int = Field(default=0, description="总信号数")
    started_at: Optional[datetime] = Field(None, description="启动时间")
    error_message: Optional[str] = Field(None, description="错误信息")

class StrategyList(BaseModel):
    """策略列表"""
    strategies: List[StrategyStatus] = Field(..., description="策略状态列表")
    total_count: int = Field(..., description="总策略数")
