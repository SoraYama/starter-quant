"""
策略引擎服务
负责技术指标计算和交易信号生成
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from ..core.config import get_settings
from ..schemas.strategy import StrategyConfig, SignalData, TechnicalIndicators
from ..schemas.market import KLineData
from ..services.technical_indicators import TechnicalIndicatorEngine
from ..services.market_data import MarketDataService

logger = logging.getLogger(__name__)

class StrategyEngine:
    """策略引擎"""
    
    def __init__(self):
        self.settings = get_settings()
        self.indicator_engine = TechnicalIndicatorEngine()
        self.market_service: Optional[MarketDataService] = None
        self.default_config = self._create_default_config()
    
    def _create_default_config(self) -> StrategyConfig:
        """创建默认策略配置"""
        return StrategyConfig(
            name="Multi-Indicator Strategy",
            description="MACD + RSI + Bollinger Bands组合策略",
            macd_fast_period=self.settings.macd_fast_period,
            macd_slow_period=self.settings.macd_slow_period,
            macd_signal_period=self.settings.macd_signal_period,
            rsi_period=self.settings.rsi_period,
            rsi_oversold=self.settings.rsi_oversold,
            rsi_overbought=self.settings.rsi_overbought,
            bb_period=self.settings.bb_period,
            bb_std_dev=self.settings.bb_std_dev,
            stop_loss_percent=self.settings.trading_stop_loss_percent,
            take_profit_percent=self.settings.trading_take_profit_percent,
            max_position_size=self.settings.trading_max_position_size
        )
    
    async def initialize(self, market_service: MarketDataService):
        """初始化策略引擎"""
        self.market_service = market_service
        logger.info("Strategy engine initialized")
    
    async def analyze_symbol(self, symbol: str, timeframe: str = "4h", 
                           limit: int = 200, config: Optional[StrategyConfig] = None) -> Dict:
        """
        分析交易对并生成信号
        
        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            limit: K线数据条数
            config: 策略配置
        
        Returns:
            分析结果包含技术指标和信号
        """
        try:
            if not self.market_service:
                raise Exception("Market service not initialized")
            
            if config is None:
                config = self.default_config
            
            # 获取K线数据
            klines = await self.market_service.get_klines(
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )
            
            if not klines:
                raise Exception(f"No kline data available for {symbol}")
            
            # 转换为指标计算所需的格式
            kline_dicts = [
                {
                    'open_time': kline.open_time,
                    'close_price': kline.close_price,
                    'high_price': kline.high_price,
                    'low_price': kline.low_price,
                    'volume': kline.volume
                }
                for kline in klines
            ]
            
            # 计算技术指标
            indicators_data = self.indicator_engine.calculate_all_indicators(
                kline_dicts,
                config={
                    'macd': {
                        'fast_period': config.macd_fast_period,
                        'slow_period': config.macd_slow_period,
                        'signal_period': config.macd_signal_period
                    },
                    'rsi': {
                        'period': config.rsi_period
                    },
                    'bollinger_bands': {
                        'period': config.bb_period,
                        'std_dev': config.bb_std_dev
                    }
                }
            )
            
            # 生成交易信号
            signals = self.indicator_engine.generate_combined_signals(indicators_data)
            
            # 转换为API响应格式
            formatted_indicators = []
            for ind_data in indicators_data:
                indicators = TechnicalIndicators(
                    timestamp=ind_data['timestamp'],
                    macd=ind_data.get('macd'),
                    macd_signal=ind_data.get('macd_signal'),
                    macd_histogram=ind_data.get('macd_histogram'),
                    rsi=ind_data.get('rsi'),
                    bb_upper=ind_data.get('bb_upper'),
                    bb_middle=ind_data.get('bb_middle'),
                    bb_lower=ind_data.get('bb_lower'),
                    bb_width=ind_data.get('bb_width')
                )
                formatted_indicators.append(indicators)
            
            # 转换信号格式
            formatted_signals = []
            for signal in signals:
                signal_data = SignalData(
                    symbol=symbol,
                    signal_type=signal['type'],
                    price=signal['price'],
                    timestamp=signal['timestamp'],
                    confidence=signal.get('confidence'),
                    strategy_name=config.name,
                    timeframe=timeframe,
                    reason="; ".join(signal.get('reasons', []))
                )
                formatted_signals.append(signal_data)
            
            result = {
                'success': True,
                'symbol': symbol,
                'timeframe': timeframe,
                'indicators': formatted_indicators,
                'signals': formatted_signals,
                'signal_count': len(formatted_signals),
                'data_points': len(indicators_data),
                'config': config,
                'analysis_time': datetime.now().isoformat()
            }
            
            logger.info(f"Analysis completed for {symbol}: {len(formatted_signals)} signals generated")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {
                'success': False,
                'symbol': symbol,
                'timeframe': timeframe,
                'error': str(e),
                'indicators': [],
                'signals': [],
                'signal_count': 0,
                'data_points': 0
            }
    
    async def get_latest_signals(self, symbol: str, timeframe: str = "4h", 
                               config: Optional[StrategyConfig] = None) -> List[SignalData]:
        """
        获取最新的交易信号
        
        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            config: 策略配置
        
        Returns:
            最新信号列表
        """
        try:
            result = await self.analyze_symbol(symbol, timeframe, limit=100, config=config)
            
            if result['success']:
                # 返回最近10个信号
                signals = result['signals']
                return signals[-10:] if len(signals) > 10 else signals
            else:
                logger.error(f"Failed to get signals for {symbol}: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting latest signals for {symbol}: {e}")
            return []
    
    async def get_current_indicators(self, symbol: str, timeframe: str = "4h",
                                   config: Optional[StrategyConfig] = None) -> Optional[TechnicalIndicators]:
        """
        获取当前最新的技术指标值
        
        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            config: 策略配置
        
        Returns:
            最新技术指标
        """
        try:
            result = await self.analyze_symbol(symbol, timeframe, limit=50, config=config)
            
            if result['success'] and result['indicators']:
                # 返回最新的指标值
                return result['indicators'][-1]
            else:
                logger.error(f"Failed to get indicators for {symbol}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error getting current indicators for {symbol}: {e}")
            return None
    
    async def evaluate_signal_strength(self, symbol: str, timeframe: str = "4h",
                                     config: Optional[StrategyConfig] = None) -> Dict:
        """
        评估信号强度
        
        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            config: 策略配置
        
        Returns:
            信号强度评估结果
        """
        try:
            result = await self.analyze_symbol(symbol, timeframe, limit=100, config=config)
            
            if not result['success']:
                return {'strength': 'unknown', 'confidence': 0, 'signals': []}
            
            recent_signals = result['signals'][-5:]  # 最近5个信号
            
            if not recent_signals:
                return {'strength': 'neutral', 'confidence': 0, 'signals': []}
            
            # 计算信号强度
            buy_count = sum(1 for s in recent_signals if s.signal_type == 'BUY')
            sell_count = sum(1 for s in recent_signals if s.signal_type == 'SELL')
            
            # 计算平均置信度
            confidences = [s.confidence for s in recent_signals if s.confidence is not None]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # 判断信号强度
            if buy_count > sell_count * 2:
                strength = 'strong_buy'
            elif buy_count > sell_count:
                strength = 'buy'
            elif sell_count > buy_count * 2:
                strength = 'strong_sell'
            elif sell_count > buy_count:
                strength = 'sell'
            else:
                strength = 'neutral'
            
            return {
                'strength': strength,
                'confidence': avg_confidence,
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'total_signals': len(recent_signals),
                'latest_signal': recent_signals[-1] if recent_signals else None,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating signal strength for {symbol}: {e}")
            return {'strength': 'unknown', 'confidence': 0, 'error': str(e)}
    
    async def batch_analyze(self, symbols: List[str], timeframe: str = "4h",
                          config: Optional[StrategyConfig] = None) -> Dict[str, Dict]:
        """
        批量分析多个交易对
        
        Args:
            symbols: 交易对符号列表
            timeframe: 时间周期
            config: 策略配置
        
        Returns:
            每个交易对的分析结果
        """
        try:
            results = {}
            
            # 并发分析多个交易对
            tasks = []
            for symbol in symbols:
                task = asyncio.create_task(
                    self.analyze_symbol(symbol, timeframe, limit=100, config=config)
                )
                tasks.append((symbol, task))
            
            # 等待所有任务完成
            for symbol, task in tasks:
                try:
                    result = await task
                    results[symbol] = result
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} in batch: {e}")
                    results[symbol] = {
                        'success': False,
                        'symbol': symbol,
                        'error': str(e)
                    }
            
            logger.info(f"Batch analysis completed for {len(symbols)} symbols")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return {}
    
    def get_default_config(self) -> StrategyConfig:
        """获取默认配置"""
        return self.default_config
    
    def validate_config(self, config: StrategyConfig) -> bool:
        """验证策略配置"""
        try:
            # 验证MACD参数
            if config.macd_fast_period >= config.macd_slow_period:
                return False
            
            # 验证RSI参数
            if not (1 <= config.rsi_period <= 100):
                return False
            if not (0 <= config.rsi_oversold < config.rsi_overbought <= 100):
                return False
            
            # 验证布林带参数
            if not (1 <= config.bb_period <= 200):
                return False
            if not (0.1 <= config.bb_std_dev <= 5.0):
                return False
            
            # 验证风险管理参数
            if not (0 < config.stop_loss_percent <= 50):
                return False
            if not (0 < config.take_profit_percent <= 100):
                return False
            if not (0 < config.max_position_size <= 1):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return False
