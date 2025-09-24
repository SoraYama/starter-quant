"""
交易记录模型
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..core.database import Base

class Trade(Base):
    """交易记录表"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    backtest_id = Column(Integer, ForeignKey('backtest_results.id'), comment="回测ID")
    symbol = Column(String(20), nullable=False, comment="交易对符号")
    side = Column(String(10), nullable=False, comment="交易方向: BUY/SELL")
    quantity = Column(DECIMAL(20, 8), nullable=False, comment="交易数量")
    price = Column(DECIMAL(20, 8), nullable=False, comment="交易价格")
    timestamp = Column(BigInteger, nullable=False, comment="交易时间戳")
    pnl = Column(DECIMAL(20, 8), comment="盈亏")
    commission = Column(DECIMAL(20, 8), comment="手续费")
    strategy_name = Column(String(50), comment="策略名称")
    signal_id = Column(Integer, comment="关联信号ID")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 外键关系
    backtest = relationship("BacktestResult", back_populates="trades")
    
    # 创建索引
    __table_args__ = (
        Index('idx_backtest_id', 'backtest_id'),
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_side', 'side'),
    )
    
    def __repr__(self):
        return f"<Trade(symbol={self.symbol}, side={self.side}, quantity={self.quantity}, price={self.price})>"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'backtest_id': self.backtest_id,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': float(self.quantity),
            'price': float(self.price),
            'timestamp': self.timestamp,
            'pnl': float(self.pnl) if self.pnl else None,
            'commission': float(self.commission) if self.commission else None,
            'strategy_name': self.strategy_name,
            'signal_id': self.signal_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 更新BacktestResult模型以添加关系
from .backtest import BacktestResult
BacktestResult.trades = relationship("Trade", back_populates="backtest")
