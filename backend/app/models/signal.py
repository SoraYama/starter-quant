"""
交易信号模型
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, DateTime, Text, Index
from sqlalchemy.sql import func

from ..core.database import Base

class Signal(Base):
    """交易信号表"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="交易对符号")
    signal_type = Column(String(10), nullable=False, comment="信号类型: BUY/SELL")
    price = Column(DECIMAL(20, 8), nullable=False, comment="信号价格")
    timestamp = Column(BigInteger, nullable=False, comment="信号时间戳")
    indicators = Column(Text, comment="指标数据JSON")
    confidence = Column(DECIMAL(3, 2), comment="信号置信度(0-1)")
    strategy_name = Column(String(50), comment="策略名称")
    timeframe = Column(String(10), comment="时间周期")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 创建索引
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_signal_type', 'signal_type'),
        Index('idx_strategy_name', 'strategy_name'),
    )
    
    def __repr__(self):
        return f"<Signal(symbol={self.symbol}, type={self.signal_type}, price={self.price})>"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'price': float(self.price),
            'timestamp': self.timestamp,
            'indicators': self.indicators,
            'confidence': float(self.confidence) if self.confidence else None,
            'strategy_name': self.strategy_name,
            'timeframe': self.timeframe,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
