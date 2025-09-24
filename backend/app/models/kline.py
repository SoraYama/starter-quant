"""
K线数据模型
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, DateTime, Index
from sqlalchemy.sql import func

from ..core.database import Base

class KLine(Base):
    """K线数据表"""
    __tablename__ = "klines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="交易对符号")
    timeframe = Column(String(10), nullable=False, comment="时间周期")
    open_time = Column(BigInteger, nullable=False, comment="开盘时间戳")
    close_time = Column(BigInteger, nullable=False, comment="收盘时间戳")
    open_price = Column(DECIMAL(20, 8), nullable=False, comment="开盘价")
    high_price = Column(DECIMAL(20, 8), nullable=False, comment="最高价")
    low_price = Column(DECIMAL(20, 8), nullable=False, comment="最低价")
    close_price = Column(DECIMAL(20, 8), nullable=False, comment="收盘价")
    volume = Column(DECIMAL(20, 8), nullable=False, comment="交易量")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_symbol_timeframe_opentime', 'symbol', 'timeframe', 'open_time', unique=True),
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
        Index('idx_open_time', 'open_time'),
    )
    
    def __repr__(self):
        return f"<KLine(symbol={self.symbol}, timeframe={self.timeframe}, open_time={self.open_time})>"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'open_time': self.open_time,
            'close_time': self.close_time,
            'open_price': float(self.open_price),
            'high_price': float(self.high_price),
            'low_price': float(self.low_price),
            'close_price': float(self.close_price),
            'volume': float(self.volume),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_binance_kline(cls, symbol: str, timeframe: str, kline_data: list):
        """从币安K线数据创建实例"""
        return cls(
            symbol=symbol,
            timeframe=timeframe,
            open_time=int(kline_data[0]),
            close_time=int(kline_data[6]),
            open_price=Decimal(str(kline_data[1])),
            high_price=Decimal(str(kline_data[2])),
            low_price=Decimal(str(kline_data[3])),
            close_price=Decimal(str(kline_data[4])),
            volume=Decimal(str(kline_data[5]))
        )
