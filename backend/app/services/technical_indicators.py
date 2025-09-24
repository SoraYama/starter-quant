"""
技术指标计算引擎
实现MACD、RSI、布林带等技术指标的计算
"""

import logging
import numpy as np
import pandas as pd
import ta
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class TechnicalIndicatorEngine:
    """技术指标计算引擎"""
    
    def __init__(self):
        self.indicators = {}
    
    def calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """
        计算MACD指标
        
        Args:
            prices: 收盘价列表
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
        
        Returns:
            包含MACD、信号线、柱状图的字典
        """
        try:
            if len(prices) < slow + signal:
                logger.warning(f"Not enough data for MACD calculation. Need {slow + signal}, got {len(prices)}")
                return {'macd': [], 'signal': [], 'histogram': []}
            
            df = pd.DataFrame({'close': prices})
            
            # 使用ta库计算MACD
            macd = ta.trend.MACD(close=df['close'], window_fast=fast, window_slow=slow, window_sign=signal)
            
            result = {
                'macd': macd.macd().fillna(0).tolist(),
                'signal': macd.macd_signal().fillna(0).tolist(),
                'histogram': macd.macd_diff().fillna(0).tolist()
            }
            
            logger.debug(f"MACD calculated for {len(prices)} prices")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {'macd': [], 'signal': [], 'histogram': []}
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """
        计算RSI指标
        
        Args:
            prices: 收盘价列表
            period: 计算周期
        
        Returns:
            RSI值列表
        """
        try:
            if len(prices) < period + 1:
                logger.warning(f"Not enough data for RSI calculation. Need {period + 1}, got {len(prices)}")
                return []
            
            df = pd.DataFrame({'close': prices})
            rsi = ta.momentum.RSIIndicator(close=df['close'], window=period)
            
            result = rsi.rsi().fillna(50).tolist()  # 默认值50
            
            logger.debug(f"RSI calculated for {len(prices)} prices")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return []
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict:
        """
        计算布林带指标
        
        Args:
            prices: 收盘价列表
            period: 计算周期
            
            std_dev: 标准差倍数
        
        Returns:
            包含上轨、中轨、下轨、宽度的字典
        """
        try:
            if len(prices) < period:
                logger.warning(f"Not enough data for Bollinger Bands calculation. Need {period}, got {len(prices)}")
                return {'upper': [], 'middle': [], 'lower': [], 'width': []}
            
            df = pd.DataFrame({'close': prices})
            bb = ta.volatility.BollingerBands(close=df['close'], window=period, window_dev=std_dev)
            
            upper = bb.bollinger_hband().fillna(0).tolist()
            middle = bb.bollinger_mavg().fillna(0).tolist()
            lower = bb.bollinger_lband().fillna(0).tolist()
            
            # 计算布林带宽度（标准化）
            width = []
            for i in range(len(upper)):
                if middle[i] > 0:
                    w = (upper[i] - lower[i]) / middle[i] * 100
                    width.append(w)
                else:
                    width.append(0)
            
            result = {
                'upper': upper,
                'middle': middle,
                'lower': lower,
                'width': width
            }
            
            logger.debug(f"Bollinger Bands calculated for {len(prices)} prices")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {'upper': [], 'middle': [], 'lower': [], 'width': []}
    
    def calculate_all_indicators(self, klines: List[Dict], config: Dict = None) -> List[Dict]:
        """
        计算所有技术指标
        
        Args:
            klines: K线数据列表
            config: 指标配置参数
        
        Returns:
            包含所有指标的列表
        """
        try:
            if not klines:
                return []
            
            # 提取收盘价
            closes = [float(kline['close_price']) for kline in klines]
            timestamps = [kline['open_time'] for kline in klines]
            
            # 获取配置参数
            if config is None:
                config = {}
            
            macd_config = config.get('macd', {})
            rsi_config = config.get('rsi', {})
            bb_config = config.get('bollinger_bands', {})
            
            # 计算各项指标
            macd_data = self.calculate_macd(
                closes,
                fast=macd_config.get('fast_period', 12),
                slow=macd_config.get('slow_period', 26),
                signal=macd_config.get('signal_period', 9)
            )
            
            rsi_data = self.calculate_rsi(
                closes,
                period=rsi_config.get('period', 14)
            )
            
            bb_data = self.calculate_bollinger_bands(
                closes,
                period=bb_config.get('period', 20),
                std_dev=bb_config.get('std_dev', 2.0)
            )
            
            # 组合所有指标数据
            result = []
            data_length = len(closes)
            
            for i in range(data_length):
                indicators = {
                    'timestamp': timestamps[i],
                    'price': closes[i]
                }
                
                # MACD指标
                if i < len(macd_data['macd']):
                    indicators.update({
                        'macd': macd_data['macd'][i],
                        'macd_signal': macd_data['signal'][i],
                        'macd_histogram': macd_data['histogram'][i]
                    })
                
                # RSI指标
                if i < len(rsi_data):
                    indicators['rsi'] = rsi_data[i]
                
                # 布林带指标
                if i < len(bb_data['upper']):
                    indicators.update({
                        'bb_upper': bb_data['upper'][i],
                        'bb_middle': bb_data['middle'][i],
                        'bb_lower': bb_data['lower'][i],
                        'bb_width': bb_data['width'][i]
                    })
                
                result.append(indicators)
            
            logger.info(f"All indicators calculated for {data_length} data points")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating all indicators: {e}")
            return []
    
    def detect_macd_signals(self, macd_data: List[Dict]) -> List[Dict]:
        """
        检测MACD信号（金叉死叉）
        
        Args:
            macd_data: 包含MACD数据的列表
        
        Returns:
            信号列表
        """
        signals = []
        
        try:
            for i in range(1, len(macd_data)):
                current = macd_data[i]
                previous = macd_data[i-1]
                
                # 检查是否有必要的数据
                if not all(key in current for key in ['macd', 'macd_signal', 'timestamp', 'price']):
                    continue
                if not all(key in previous for key in ['macd', 'macd_signal']):
                    continue
                
                # 金叉信号（MACD线从下方穿越信号线）
                if (previous['macd'] <= previous['macd_signal'] and 
                    current['macd'] > current['macd_signal']):
                    
                    signals.append({
                        'type': 'BUY',
                        'reason': 'MACD金叉',
                        'timestamp': current['timestamp'],
                        'price': current['price'],
                        'macd': current['macd'],
                        'macd_signal': current['macd_signal']
                    })
                
                # 死叉信号（MACD线从上方穿越信号线）
                elif (previous['macd'] >= previous['macd_signal'] and 
                      current['macd'] < current['macd_signal']):
                    
                    signals.append({
                        'type': 'SELL',
                        'reason': 'MACD死叉',
                        'timestamp': current['timestamp'],
                        'price': current['price'],
                        'macd': current['macd'],
                        'macd_signal': current['macd_signal']
                    })
            
        except Exception as e:
            logger.error(f"Error detecting MACD signals: {e}")
        
        return signals
    
    def detect_rsi_signals(self, rsi_data: List[Dict], oversold: int = 30, overbought: int = 70) -> List[Dict]:
        """
        检测RSI信号（超买超卖）
        
        Args:
            rsi_data: 包含RSI数据的列表
            oversold: 超卖阈值
            overbought: 超买阈值
        
        Returns:
            信号列表
        """
        signals = []
        
        try:
            for i in range(1, len(rsi_data)):
                current = rsi_data[i]
                previous = rsi_data[i-1]
                
                if not all(key in current for key in ['rsi', 'timestamp', 'price']):
                    continue
                if 'rsi' not in previous:
                    continue
                
                # 超卖反弹信号
                if previous['rsi'] <= oversold and current['rsi'] > oversold:
                    signals.append({
                        'type': 'BUY',
                        'reason': f'RSI超卖反弹(RSI:{current["rsi"]:.2f})',
                        'timestamp': current['timestamp'],
                        'price': current['price'],
                        'rsi': current['rsi']
                    })
                
                # 超买回调信号
                elif previous['rsi'] >= overbought and current['rsi'] < overbought:
                    signals.append({
                        'type': 'SELL',
                        'reason': f'RSI超买回调(RSI:{current["rsi"]:.2f})',
                        'timestamp': current['timestamp'],
                        'price': current['price'],
                        'rsi': current['rsi']
                    })
            
        except Exception as e:
            logger.error(f"Error detecting RSI signals: {e}")
        
        return signals
    
    def detect_bollinger_signals(self, bb_data: List[Dict]) -> List[Dict]:
        """
        检测布林带信号
        
        Args:
            bb_data: 包含布林带数据的列表
        
        Returns:
            信号列表
        """
        signals = []
        
        try:
            for i in range(len(bb_data)):
                current = bb_data[i]
                
                if not all(key in current for key in ['price', 'bb_upper', 'bb_lower', 'timestamp']):
                    continue
                
                # 价格触及下轨（支撑）
                if current['price'] <= current['bb_lower']:
                    signals.append({
                        'type': 'BUY',
                        'reason': '价格触及布林带下轨',
                        'timestamp': current['timestamp'],
                        'price': current['price'],
                        'bb_lower': current['bb_lower']
                    })
                
                # 价格触及上轨（阻力）
                elif current['price'] >= current['bb_upper']:
                    signals.append({
                        'type': 'SELL',
                        'reason': '价格触及布林带上轨',
                        'timestamp': current['timestamp'],
                        'price': current['price'],
                        'bb_upper': current['bb_upper']
                    })
            
        except Exception as e:
            logger.error(f"Error detecting Bollinger signals: {e}")
        
        return signals
    
    def generate_combined_signals(self, indicators_data: List[Dict], config: Dict = None) -> List[Dict]:
        """
        生成组合信号（多指标组合）
        
        Args:
            indicators_data: 技术指标数据
            config: 信号配置
        
        Returns:
            组合信号列表
        """
        try:
            if not indicators_data:
                return []
            
            # 获取各项信号
            macd_signals = self.detect_macd_signals(indicators_data)
            rsi_signals = self.detect_rsi_signals(indicators_data)
            bb_signals = self.detect_bollinger_signals(indicators_data)
            
            # 按时间戳组织信号
            signal_map = {}
            
            for signal in macd_signals + rsi_signals + bb_signals:
                timestamp = signal['timestamp']
                if timestamp not in signal_map:
                    signal_map[timestamp] = {
                        'timestamp': timestamp,
                        'price': signal['price'],
                        'buy_signals': [],
                        'sell_signals': []
                    }
                
                if signal['type'] == 'BUY':
                    signal_map[timestamp]['buy_signals'].append(signal['reason'])
                else:
                    signal_map[timestamp]['sell_signals'].append(signal['reason'])
            
            # 生成最终信号
            combined_signals = []
            
            for timestamp, data in signal_map.items():
                buy_count = len(data['buy_signals'])
                sell_count = len(data['sell_signals'])
                
                # 信号强度判断
                if buy_count >= 2:  # 至少2个买入信号
                    combined_signals.append({
                        'type': 'BUY',
                        'timestamp': timestamp,
                        'price': data['price'],
                        'confidence': min(buy_count / 3, 1.0),
                        'reasons': data['buy_signals'],
                        'signal_count': buy_count
                    })
                elif sell_count >= 2:  # 至少2个卖出信号
                    combined_signals.append({
                        'type': 'SELL',
                        'timestamp': timestamp,
                        'price': data['price'],
                        'confidence': min(sell_count / 3, 1.0),
                        'reasons': data['sell_signals'],
                        'signal_count': sell_count
                    })
            
            logger.info(f"Generated {len(combined_signals)} combined signals")
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error generating combined signals: {e}")
            return []
