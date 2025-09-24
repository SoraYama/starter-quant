"""
币安API客户端服务
支持公开数据模式和完整功能模式的灵活切换
"""

import asyncio
import logging
import time
from typing import List, Dict, Optional, Any
import aiohttp
import json
from binance import AsyncClient
from binance.exceptions import BinanceAPIException

from ..core.config import get_binance_config

logger = logging.getLogger(__name__)

class BinanceClient:
    """币安API客户端"""
    
    def __init__(self):
        self.config = get_binance_config()
        self.mode = self.config['mode']
        self.client: Optional[AsyncClient] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = self.config.get('base_url', 'https://api.binance.com')
        
        logger.info(f"Initializing Binance client in {self.mode} mode")
    
    async def initialize(self):
        """初始化客户端"""
        try:
            if self.mode == "FULL_MODE":
                # 完整功能模式：使用API密钥
                self.client = await AsyncClient.create(
                    api_key=self.config['api_key'],
                    api_secret=self.config['api_secret'],
                    testnet=self.config.get('testnet', False)
                )
                logger.info("Binance client initialized with API credentials")
            else:
                # 公开数据模式：仅使用HTTP请求
                self.session = aiohttp.ClientSession()
                logger.info("Binance client initialized in public data mode")
            
            # 测试连接
            await self._test_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            raise
    
    async def close(self):
        """关闭客户端连接"""
        try:
            if self.client:
                await self.client.close_connection()
            if self.session:
                await self.session.close()
            logger.info("Binance client connections closed")
        except Exception as e:
            logger.error(f"Error closing Binance client: {e}")
    
    async def _test_connection(self):
        """测试连接"""
        try:
            if self.mode == "FULL_MODE":
                # 测试API连接
                await self.client.ping()
                account_info = await self.client.get_account()
                logger.info(f"API connection test successful. Account status: {account_info.get('accountType', 'Unknown')}")
            else:
                # 测试公开API连接
                url = f"{self.base_url}/api/v3/ping"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        logger.info("Public API connection test successful")
                    else:
                        raise Exception(f"Public API test failed with status {response.status}")
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            raise
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500, 
                        start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[List]:
        """获取K线数据"""
        try:
            if self.mode == "FULL_MODE" and self.client:
                # 使用python-binance客户端
                klines = await self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit,
                    startTime=start_time,
                    endTime=end_time
                )
                return klines
            else:
                # 使用公开API
                url = f"{self.base_url}/api/v3/klines"
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'limit': limit
                }
                if start_time:
                    params['startTime'] = start_time
                if end_time:
                    params['endTime'] = end_time
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to get klines for {symbol}: {e}")
            raise
    
    async def get_ticker_24hr(self, symbol: str) -> Dict:
        """获取24小时价格统计"""
        try:
            if self.mode == "FULL_MODE" and self.client:
                ticker = await self.client.get_ticker(symbol=symbol)
                return ticker
            else:
                url = f"{self.base_url}/api/v3/ticker/24hr"
                params = {'symbol': symbol}
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ticker request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to get ticker for {symbol}: {e}")
            raise
    
    async def get_symbol_ticker(self, symbol: str) -> Dict:
        """获取最新价格"""
        try:
            if self.mode == "FULL_MODE" and self.client:
                ticker = await self.client.get_symbol_ticker(symbol=symbol)
                return ticker
            else:
                url = f"{self.base_url}/api/v3/ticker/price"
                params = {'symbol': symbol}
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Price request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            raise
    
    async def get_exchange_info(self) -> Dict:
        """获取交易所信息"""
        try:
            if self.mode == "FULL_MODE" and self.client:
                info = await self.client.get_exchange_info()
                return info
            else:
                url = f"{self.base_url}/api/v3/exchangeInfo"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Exchange info request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to get exchange info: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict:
        """获取订单簿深度"""
        try:
            if self.mode == "FULL_MODE" and self.client:
                depth = await self.client.get_order_book(symbol=symbol, limit=limit)
                return depth
            else:
                url = f"{self.base_url}/api/v3/depth"
                params = {'symbol': symbol, 'limit': limit}
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Orderbook request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to get orderbook for {symbol}: {e}")
            raise
    
    async def get_historical_klines(self, symbol: str, interval: str, 
                                  start_str: str, end_str: Optional[str] = None) -> List[List]:
        """获取历史K线数据（支持大量数据获取）"""
        try:
            if self.mode == "FULL_MODE" and self.client:
                klines = await self.client.get_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    start_str=start_str,
                    end_str=end_str
                )
                return klines
            else:
                # 公开API模式下，需要分批获取大量历史数据
                return await self._get_historical_klines_public(symbol, interval, start_str, end_str)
                
        except Exception as e:
            logger.error(f"Failed to get historical klines for {symbol}: {e}")
            raise
    
    async def _get_historical_klines_public(self, symbol: str, interval: str, 
                                          start_str: str, end_str: Optional[str] = None) -> List[List]:
        """公开API模式下获取历史数据"""
        all_klines = []
        limit = 1000  # 每次请求最大1000条
        
        # 转换时间字符串为时间戳
        start_time = int(time.mktime(time.strptime(start_str, "%d %b %Y")) * 1000)
        end_time = int(time.mktime(time.strptime(end_str, "%d %b %Y")) * 1000) if end_str else int(time.time() * 1000)
        
        current_time = start_time
        
        while current_time < end_time:
            try:
                klines = await self.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit,
                    start_time=current_time,
                    end_time=min(current_time + limit * self._get_interval_ms(interval), end_time)
                )
                
                if not klines:
                    break
                
                all_klines.extend(klines)
                current_time = klines[-1][6] + 1  # 下一批从最后一个K线的结束时间+1开始
                
                # 避免请求频率过高
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error fetching historical data batch: {e}")
                break
        
        return all_klines
    
    def _get_interval_ms(self, interval: str) -> int:
        """获取时间间隔对应的毫秒数"""
        interval_map = {
            '1m': 60 * 1000,
            '3m': 3 * 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '2h': 2 * 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '6h': 6 * 60 * 60 * 1000,
            '8h': 8 * 60 * 60 * 1000,
            '12h': 12 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
            '3d': 3 * 24 * 60 * 60 * 1000,
            '1w': 7 * 24 * 60 * 60 * 1000,
            '1M': 30 * 24 * 60 * 60 * 1000,
        }
        return interval_map.get(interval, 60 * 60 * 1000)  # 默认1小时
    
    def is_full_mode(self) -> bool:
        """是否为完整功能模式"""
        return self.mode == "FULL_MODE"
    
    def get_supported_symbols(self) -> List[str]:
        """获取支持的交易对列表"""
        return self.config.get('symbols', ['BTCUSDT', 'ETHUSDT'])
