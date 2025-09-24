"""
回测结果模型
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, Text, Index
from sqlalchemy.sql import func

from ..core.database import Base

class BacktestResult(Base):
    """回测结果表"""
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String(50), nullable=False, comment="策略名称")
    symbol = Column(String(20), nullable=False, comment="交易对符号")
    timeframe = Column(String(10), nullable=False, comment="时间周期")
    start_date = Column(Date, nullable=False, comment="回测开始日期")
    end_date = Column(Date, nullable=False, comment="回测结束日期")
    initial_balance = Column(DECIMAL(20, 8), nullable=False, comment="初始资金")
    final_balance = Column(DECIMAL(20, 8), nullable=False, comment="最终资金")
    total_return = Column(DECIMAL(10, 4), nullable=False, comment="总收益率(%)")
    max_drawdown = Column(DECIMAL(10, 4), nullable=False, comment="最大回撤(%)")
    sharpe_ratio = Column(DECIMAL(10, 4), comment="夏普比率")
    win_rate = Column(DECIMAL(5, 2), nullable=False, comment="胜率(%)")
    total_trades = Column(Integer, nullable=False, comment="总交易次数")
    winning_trades = Column(Integer, default=0, comment="盈利交易次数")
    losing_trades = Column(Integer, default=0, comment="亏损交易次数")
    avg_profit = Column(DECIMAL(10, 4), comment="平均盈利")
    avg_loss = Column(DECIMAL(10, 4), comment="平均亏损")
    profit_factor = Column(DECIMAL(10, 4), comment="盈利因子")
    config = Column(Text, comment="策略配置JSON")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 创建索引
    __table_args__ = (
        Index('idx_strategy_symbol', 'strategy_name', 'symbol'),
        Index('idx_created_at', 'created_at'),
        Index('idx_total_return', 'total_return'),
    )
    
    def __repr__(self):
        return f"<BacktestResult(strategy={self.strategy_name}, symbol={self.symbol}, return={self.total_return}%)>"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'initial_balance': float(self.initial_balance),
            'final_balance': float(self.final_balance),
            'total_return': float(self.total_return),
            'max_drawdown': float(self.max_drawdown),
            'sharpe_ratio': float(self.sharpe_ratio) if self.sharpe_ratio else None,
            'win_rate': float(self.win_rate),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_profit': float(self.avg_profit) if self.avg_profit else None,
            'avg_loss': float(self.avg_loss) if self.avg_loss else None,
            'profit_factor': float(self.profit_factor) if self.profit_factor else None,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
