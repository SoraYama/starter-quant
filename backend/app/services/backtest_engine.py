"""
回测引擎
支持策略回测和性能分析
"""

import asyncio
import logging
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass

from ..core.config import get_settings
from ..core.database import get_db
from ..models.backtest import BacktestResult
from ..models.trade import Trade
from ..schemas.strategy import StrategyConfig
from ..schemas.market import KLineData
from ..services.market_data import MarketDataService
from ..services.strategy_engine import StrategyEngine

logger = logging.getLogger(__name__)

@dataclass
class BacktestTrade:
    """回测交易记录"""
    timestamp: int
    symbol: str
    side: str  # BUY/SELL
    quantity: float
    price: float
    commission: float
    reason: str

@dataclass 
class BacktestPosition:
    """回测持仓"""
    symbol: str
    quantity: float
    avg_price: float
    unrealized_pnl: float
    entry_time: int

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self):
        self.settings = get_settings()
        self.market_service: Optional[MarketDataService] = None
        self.strategy_engine: Optional[StrategyEngine] = None
        
    async def initialize(self, market_service: MarketDataService, strategy_engine: StrategyEngine):
        """初始化回测引擎"""
        self.market_service = market_service
        self.strategy_engine = strategy_engine
        logger.info("Backtest engine initialized")
    
    async def run_backtest(self, symbol: str, start_date: date, end_date: date,
                          initial_balance: float, strategy_config: StrategyConfig,
                          timeframe: str = "4h") -> Dict:
        """
        运行回测
        
        Args:
            symbol: 交易对符号
            start_date: 开始日期
            end_date: 结束日期  
            initial_balance: 初始资金
            strategy_config: 策略配置
            timeframe: 时间周期
        
        Returns:
            回测结果
        """
        try:
            logger.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
            
            # 获取历史数据
            days = (end_date - start_date).days
            if days > self.settings.backtest_max_history_days:
                raise Exception(f"Backtest period too long. Maximum {self.settings.backtest_max_history_days} days")
            
            klines = await self._get_backtest_data(symbol, start_date, end_date, timeframe)
            if not klines:
                raise Exception(f"No historical data available for {symbol}")
            
            # 运行策略分析
            analysis_result = await self.strategy_engine.analyze_symbol(
                symbol=symbol,
                timeframe=timeframe,
                limit=len(klines),
                config=strategy_config
            )
            
            if not analysis_result['success']:
                raise Exception(f"Strategy analysis failed: {analysis_result.get('error')}")
            
            # 执行回测交易模拟
            backtest_result = await self._simulate_trading(
                klines=klines,
                signals=analysis_result['signals'],
                initial_balance=initial_balance,
                strategy_config=strategy_config,
                symbol=symbol
            )
            
            # 计算性能指标
            performance_metrics = self._calculate_performance_metrics(
                backtest_result['trades'],
                backtest_result['balance_history'],
                initial_balance
            )
            
            # 保存回测结果
            result_id = await self._save_backtest_result(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                initial_balance=initial_balance,
                final_balance=backtest_result['final_balance'],
                trades=backtest_result['trades'],
                performance_metrics=performance_metrics,
                strategy_config=strategy_config
            )
            
            # 组装完整结果
            complete_result = {
                'backtest_id': result_id,
                'symbol': symbol,
                'timeframe': timeframe,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'initial_balance': initial_balance,
                'final_balance': backtest_result['final_balance'],
                'total_trades': len(backtest_result['trades']),
                'balance_history': backtest_result['balance_history'],
                'trades': [trade.__dict__ for trade in backtest_result['trades']],
                'performance_metrics': performance_metrics,
                'strategy_config': strategy_config.dict(),
                'data_points': len(klines),
                'backtest_time': datetime.now().isoformat()
            }
            
            logger.info(f"Backtest completed for {symbol}: {performance_metrics['total_return']:.2f}% return")
            return complete_result
            
        except Exception as e:
            logger.error(f"Backtest failed for {symbol}: {e}")
            raise
    
    async def _get_backtest_data(self, symbol: str, start_date: date, end_date: date, 
                               timeframe: str) -> List[KLineData]:
        """获取回测历史数据"""
        try:
            days = (end_date - start_date).days + 1
            
            # 获取历史数据
            klines = await self.market_service.get_historical_data(
                symbol=symbol,
                interval=timeframe,
                days=days
            )
            
            if not klines:
                # 如果没有历史数据，尝试从当前数据获取
                logger.warning(f"No historical data found, trying current data for {symbol}")
                klines = await self.market_service.get_klines(
                    symbol=symbol,
                    interval=timeframe,
                    limit=1000
                )
            
            # 过滤时间范围
            start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
            end_timestamp = int(datetime.combine(end_date, datetime.max.time()).timestamp() * 1000)
            
            filtered_klines = [
                kline for kline in klines
                if start_timestamp <= kline.open_time <= end_timestamp
            ]
            
            logger.info(f"Retrieved {len(filtered_klines)} klines for backtest")
            return filtered_klines
            
        except Exception as e:
            logger.error(f"Error getting backtest data: {e}")
            return []
    
    async def _simulate_trading(self, klines: List[KLineData], signals: List,
                              initial_balance: float, strategy_config: StrategyConfig,
                              symbol: str) -> Dict:
        """
        模拟交易执行
        
        Args:
            klines: K线数据
            signals: 交易信号
            initial_balance: 初始资金
            strategy_config: 策略配置
            symbol: 交易对符号
        
        Returns:
            模拟交易结果
        """
        try:
            balance = initial_balance
            position: Optional[BacktestPosition] = None
            trades = []
            balance_history = []
            
            # 创建价格字典用于快速查找
            price_dict = {kline.open_time: kline.close_price for kline in klines}
            
            # 按时间排序信号
            sorted_signals = sorted(signals, key=lambda x: x.timestamp)
            
            for signal in sorted_signals:
                signal_time = signal.timestamp
                signal_price = price_dict.get(signal_time)
                
                if signal_price is None:
                    continue
                
                # 执行交易逻辑
                if signal.signal_type == 'BUY' and position is None:
                    # 开多仓
                    quantity = (balance * strategy_config.max_position_size) / signal_price
                    commission = quantity * signal_price * self.settings.backtest_commission
                    
                    if balance >= (quantity * signal_price + commission):
                        position = BacktestPosition(
                            symbol=symbol,
                            quantity=quantity,
                            avg_price=signal_price,
                            unrealized_pnl=0,
                            entry_time=signal_time
                        )
                        
                        balance -= (quantity * signal_price + commission)
                        
                        trade = BacktestTrade(
                            timestamp=signal_time,
                            symbol=symbol,
                            side='BUY',
                            quantity=quantity,
                            price=signal_price,
                            commission=commission,
                            reason=getattr(signal, 'reason', 'Strategy signal')
                        )
                        trades.append(trade)
                        
                        logger.debug(f"BUY: {quantity:.6f} {symbol} at {signal_price}")
                
                elif signal.signal_type == 'SELL' and position is not None:
                    # 平仓
                    sell_value = position.quantity * signal_price
                    commission = sell_value * self.settings.backtest_commission
                    pnl = sell_value - (position.quantity * position.avg_price) - commission
                    
                    balance += sell_value - commission
                    
                    trade = BacktestTrade(
                        timestamp=signal_time,
                        symbol=symbol,
                        side='SELL',
                        quantity=position.quantity,
                        price=signal_price,
                        commission=commission,
                        reason=getattr(signal, 'reason', 'Strategy signal')
                    )
                    trades.append(trade)
                    
                    logger.debug(f"SELL: {position.quantity:.6f} {symbol} at {signal_price}, PnL: {pnl:.2f}")
                    
                    position = None
                
                # 记录账户余额历史
                current_value = balance
                if position:
                    current_value += position.quantity * signal_price
                
                balance_history.append({
                    'timestamp': signal_time,
                    'balance': balance,
                    'position_value': position.quantity * signal_price if position else 0,
                    'total_value': current_value
                })
            
            # 如果还有持仓，按最后价格平仓
            final_balance = balance
            if position and klines:
                last_price = klines[-1].close_price
                final_balance += position.quantity * last_price
                
                # 添加最终平仓交易
                commission = position.quantity * last_price * self.settings.backtest_commission
                final_balance -= commission
                
                trade = BacktestTrade(
                    timestamp=klines[-1].open_time,
                    symbol=symbol,
                    side='SELL',
                    quantity=position.quantity,
                    price=last_price,
                    commission=commission,
                    reason='Final position close'
                )
                trades.append(trade)
            
            return {
                'final_balance': final_balance,
                'trades': trades,
                'balance_history': balance_history
            }
            
        except Exception as e:
            logger.error(f"Error in trading simulation: {e}")
            raise
    
    def _calculate_performance_metrics(self, trades: List[BacktestTrade], 
                                     balance_history: List[Dict], initial_balance: float) -> Dict:
        """计算回测性能指标"""
        try:
            if not trades:
                return {
                    'total_return': 0.0,
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0,
                    'win_rate': 0.0,
                    'profit_factor': 0.0,
                    'avg_profit': 0.0,
                    'avg_loss': 0.0,
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0
                }
            
            # 计算交易对盈亏
            trade_pairs = []
            buy_trades = []
            
            for trade in trades:
                if trade.side == 'BUY':
                    buy_trades.append(trade)
                elif trade.side == 'SELL' and buy_trades:
                    buy_trade = buy_trades.pop(0)  # FIFO
                    pnl = (trade.price - buy_trade.price) * trade.quantity - trade.commission - buy_trade.commission
                    trade_pairs.append({
                        'pnl': pnl,
                        'return_pct': (pnl / (buy_trade.price * buy_trade.quantity)) * 100,
                        'hold_time': trade.timestamp - buy_trade.timestamp
                    })
            
            if not trade_pairs:
                return {
                    'total_return': 0.0,
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0,
                    'win_rate': 0.0,
                    'profit_factor': 0.0,
                    'avg_profit': 0.0,
                    'avg_loss': 0.0,
                    'total_trades': len(trades),
                    'winning_trades': 0,
                    'losing_trades': 0
                }
            
            # 基本统计
            total_pnl = sum(pair['pnl'] for pair in trade_pairs)
            final_balance = initial_balance + total_pnl
            total_return = (total_pnl / initial_balance) * 100
            
            # 盈亏交易统计
            winning_trades = [pair for pair in trade_pairs if pair['pnl'] > 0]
            losing_trades = [pair for pair in trade_pairs if pair['pnl'] < 0]
            
            win_rate = (len(winning_trades) / len(trade_pairs)) * 100 if trade_pairs else 0
            
            avg_profit = sum(pair['pnl'] for pair in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(pair['pnl'] for pair in losing_trades) / len(losing_trades) if losing_trades else 0
            
            # 盈利因子
            gross_profit = sum(pair['pnl'] for pair in winning_trades)
            gross_loss = abs(sum(pair['pnl'] for pair in losing_trades))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            # 最大回撤
            max_drawdown = 0.0
            peak_value = initial_balance
            
            for record in balance_history:
                current_value = record['total_value']
                if current_value > peak_value:
                    peak_value = current_value
                
                drawdown = ((peak_value - current_value) / peak_value) * 100
                max_drawdown = max(max_drawdown, drawdown)
            
            # 夏普比率 (简化计算)
            if len(trade_pairs) > 1:
                returns = [pair['return_pct'] for pair in trade_pairs]
                avg_return = sum(returns) / len(returns)
                volatility = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
                sharpe_ratio = (avg_return / volatility) if volatility > 0 else 0
            else:
                sharpe_ratio = 0
            
            return {
                'total_return': round(total_return, 4),
                'max_drawdown': round(max_drawdown, 4),
                'sharpe_ratio': round(sharpe_ratio, 4),
                'win_rate': round(win_rate, 2),
                'profit_factor': round(profit_factor, 4),
                'avg_profit': round(avg_profit, 4),
                'avg_loss': round(avg_loss, 4),
                'total_trades': len(trade_pairs),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'gross_profit': round(gross_profit, 4),
                'gross_loss': round(gross_loss, 4),
                'final_balance': round(final_balance, 4)
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    async def _save_backtest_result(self, symbol: str, timeframe: str, start_date: date, 
                                  end_date: date, initial_balance: float, final_balance: float,
                                  trades: List[BacktestTrade], performance_metrics: Dict,
                                  strategy_config: StrategyConfig) -> int:
        """保存回测结果到数据库"""
        try:
            async for session in get_db():
                # 创建回测结果记录
                backtest_result = BacktestResult(
                    strategy_name=strategy_config.name,
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date,
                    initial_balance=Decimal(str(initial_balance)),
                    final_balance=Decimal(str(final_balance)),
                    total_return=Decimal(str(performance_metrics.get('total_return', 0))),
                    max_drawdown=Decimal(str(performance_metrics.get('max_drawdown', 0))),
                    sharpe_ratio=Decimal(str(performance_metrics.get('sharpe_ratio', 0))) if performance_metrics.get('sharpe_ratio') else None,
                    win_rate=Decimal(str(performance_metrics.get('win_rate', 0))),
                    total_trades=performance_metrics.get('total_trades', 0),
                    winning_trades=performance_metrics.get('winning_trades', 0),
                    losing_trades=performance_metrics.get('losing_trades', 0),
                    avg_profit=Decimal(str(performance_metrics.get('avg_profit', 0))) if performance_metrics.get('avg_profit') else None,
                    avg_loss=Decimal(str(performance_metrics.get('avg_loss', 0))) if performance_metrics.get('avg_loss') else None,
                    profit_factor=Decimal(str(performance_metrics.get('profit_factor', 0))) if performance_metrics.get('profit_factor') else None,
                    config=json.dumps(strategy_config.dict())
                )
                
                session.add(backtest_result)
                await session.flush()  # 获取ID
                
                # 保存交易记录
                for trade in trades:
                    trade_record = Trade(
                        backtest_id=backtest_result.id,
                        symbol=trade.symbol,
                        side=trade.side,
                        quantity=Decimal(str(trade.quantity)),
                        price=Decimal(str(trade.price)),
                        timestamp=trade.timestamp,
                        pnl=None,  # 在交易对中计算
                        commission=Decimal(str(trade.commission)),
                        strategy_name=strategy_config.name
                    )
                    session.add(trade_record)
                
                await session.commit()
                
                logger.info(f"Backtest result saved with ID: {backtest_result.id}")
                return backtest_result.id
                
        except Exception as e:
            logger.error(f"Error saving backtest result: {e}")
            raise
    
    async def get_backtest_history(self, limit: int = 20, symbol: Optional[str] = None) -> List[Dict]:
        """获取回测历史"""
        try:
            async for session in get_db():
                from sqlalchemy import select, desc
                
                query = select(BacktestResult).order_by(desc(BacktestResult.created_at)).limit(limit)
                
                if symbol:
                    query = query.where(BacktestResult.symbol == symbol.upper())
                
                result = await session.execute(query)
                backtest_results = result.scalars().all()
                
                return [result.to_dict() for result in backtest_results]
                
        except Exception as e:
            logger.error(f"Error getting backtest history: {e}")
            return []
    
    async def get_backtest_detail(self, backtest_id: int) -> Optional[Dict]:
        """获取回测详情"""
        try:
            async for session in get_db():
                from sqlalchemy import select
                
                # 获取回测结果
                result = await session.execute(
                    select(BacktestResult).where(BacktestResult.id == backtest_id)
                )
                backtest_result = result.scalar()
                
                if not backtest_result:
                    return None
                
                # 获取交易记录
                trades_result = await session.execute(
                    select(Trade).where(Trade.backtest_id == backtest_id)
                )
                trades = trades_result.scalars().all()
                
                # 组装详情
                detail = backtest_result.to_dict()
                detail['trades'] = [trade.to_dict() for trade in trades]
                
                return detail
                
        except Exception as e:
            logger.error(f"Error getting backtest detail: {e}")
            return None
