"""
市场数据服务
负责管理K线数据的获取、存储和缓存
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.config import get_settings
from ..models.kline import KLine
from ..schemas.market import KLineData
from .binance_client import BinanceClient

logger = logging.getLogger(__name__)

class MarketDataService:
    """市场数据服务"""

    def __init__(self):
        self.settings = get_settings()
        self.binance_client: Optional[BinanceClient] = None
        self.symbols = self.settings.binance_symbols
        self.default_interval = self.settings.binance_default_interval
        self._real_time_tasks = {}
        self._is_running = False

    async def initialize(self):
        """初始化服务"""
        try:
            self.binance_client = BinanceClient()
            await self.binance_client.initialize()

            logger.info("Market data service initialized successfully")
        except Exception as e:
            logger.warning(f"Market data service initialization failed, but continuing: {e}")
            # 创建一个模拟的客户端，避免后续调用出错
            self.binance_client = None

    async def close(self):
        """关闭服务"""
        try:
            self._is_running = False

            # 停止所有实时数据任务
            for task in self._real_time_tasks.values():
                if not task.done():
                    task.cancel()

            if self.binance_client:
                await self.binance_client.close()

            logger.info("Market data service closed")
        except Exception as e:
            logger.error(f"Error closing market data service: {e}")

    async def get_klines(self, symbol: str, interval: str, limit: int = 500,
                        start_time: Optional[int] = None, end_time: Optional[int] = None,
                        use_cache: bool = True) -> List[KLineData]:
        """
        获取K线数据（优先从缓存获取）

        Args:
            symbol: 交易对符号
            interval: 时间间隔
            limit: 数据条数
            start_time: 开始时间戳
            end_time: 结束时间戳
            use_cache: 是否使用缓存

        Returns:
            K线数据列表
        """
        try:
            klines = []

            if use_cache:
                # 首先尝试从数据库获取缓存数据
                klines = await self._get_klines_from_db(symbol, interval, limit, start_time, end_time)

            # 如果缓存数据不足，从API获取
            if not klines or len(klines) < limit:
                logger.info(f"Fetching {symbol} {interval} data from API (cache insufficient)")
                klines = await self._get_klines_from_api(symbol, interval, limit, start_time, end_time)

                # 保存到数据库
                if klines:
                    await self._save_klines_to_db(klines, symbol, interval)

            logger.info(f"Retrieved {len(klines)} klines for {symbol} {interval}")
            return klines

        except Exception as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            logger.warning(f"Returning mock kline data for {symbol}")
            return self._get_mock_klines(symbol, interval, limit)

    async def _get_klines_from_db(self, symbol: str, interval: str, limit: int,
                                 start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[KLineData]:
        """从数据库获取K线数据"""
        try:
            async for session in get_db():
                query = select(KLine).where(
                    and_(
                        KLine.symbol == symbol,
                        KLine.timeframe == interval
                    )
                )

                if start_time:
                    query = query.where(KLine.open_time >= start_time)
                if end_time:
                    query = query.where(KLine.open_time <= end_time)

                query = query.order_by(KLine.open_time.desc()).limit(limit)
                result = await session.execute(query)
                klines = result.scalars().all()

                # 转换为KLineData格式
                data = []
                for kline in reversed(klines):  # 反转以获得正确的时间顺序
                    data.append(KLineData(
                        symbol=kline.symbol,
                        timeframe=kline.timeframe,
                        open_time=kline.open_time,
                        close_time=kline.close_time,
                        open_price=float(kline.open_price),
                        high_price=float(kline.high_price),
                        low_price=float(kline.low_price),
                        close_price=float(kline.close_price),
                        volume=float(kline.volume)
                    ))

                logger.debug(f"Retrieved {len(data)} klines from database")
                return data

        except Exception as e:
            logger.error(f"Error getting klines from database: {e}")
            return []

    async def _get_klines_from_api(self, symbol: str, interval: str, limit: int,
                                  start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[KLineData]:
        """从API获取K线数据"""
        try:
            if not self.binance_client:
                raise Exception("Binance client not initialized")

            raw_klines = await self.binance_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                start_time=start_time,
                end_time=end_time
            )

            # 转换为KLineData格式
            data = []
            for kline in raw_klines:
                data.append(KLineData(
                    symbol=symbol,
                    timeframe=interval,
                    open_time=int(kline[0]),
                    close_time=int(kline[6]),
                    open_price=float(kline[1]),
                    high_price=float(kline[2]),
                    low_price=float(kline[3]),
                    close_price=float(kline[4]),
                    volume=float(kline[5])
                ))

            logger.debug(f"Retrieved {len(data)} klines from API")
            return data

        except Exception as e:
            logger.error(f"Error getting klines from API: {e}")
            raise e  # 重新抛出异常，让上层处理

    async def _save_klines_to_db(self, klines: List[KLineData], symbol: str, interval: str):
        """保存K线数据到数据库"""
        try:
            async for session in get_db():
                for kline_data in klines:
                    # 检查是否已存在
                    existing = await session.execute(
                        select(KLine).where(
                            and_(
                                KLine.symbol == symbol,
                                KLine.timeframe == interval,
                                KLine.open_time == kline_data.open_time
                            )
                        )
                    )

                    if not existing.scalar():
                        # 创建新记录
                        kline = KLine.from_binance_kline(
                            symbol=symbol,
                            timeframe=interval,
                            kline_data=[
                                kline_data.open_time,
                                str(kline_data.open_price),
                                str(kline_data.high_price),
                                str(kline_data.low_price),
                                str(kline_data.close_price),
                                str(kline_data.volume),
                                kline_data.close_time
                            ]
                        )
                        session.add(kline)

                await session.commit()
                logger.debug(f"Saved {len(klines)} klines to database")

        except Exception as e:
            logger.error(f"Error saving klines to database: {e}")

    async def get_historical_data(self, symbol: str, interval: str, days: int = 30) -> List[KLineData]:
        """
        获取历史数据

        Args:
            symbol: 交易对符号
            interval: 时间间隔
            days: 历史天数

        Returns:
            历史K线数据
        """
        try:
            # 计算时间范围
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

            # 获取大量历史数据
            if not self.binance_client:
                raise Exception("Binance client not initialized")

            if self.binance_client.is_full_mode():
                # 完整模式：使用历史数据API
                start_str = (datetime.now() - timedelta(days=days)).strftime("%d %b %Y")
                end_str = datetime.now().strftime("%d %b %Y")

                raw_klines = await self.binance_client.get_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    start_str=start_str,
                    end_str=end_str
                )
            else:
                # 公开模式：分批获取
                raw_klines = await self.binance_client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=1000,
                    start_time=start_time,
                    end_time=end_time
                )

            # 转换数据格式
            klines = []
            for kline in raw_klines:
                klines.append(KLineData(
                    symbol=symbol,
                    timeframe=interval,
                    open_time=int(kline[0]),
                    close_time=int(kline[6]),
                    open_price=float(kline[1]),
                    high_price=float(kline[2]),
                    low_price=float(kline[3]),
                    close_price=float(kline[4]),
                    volume=float(kline[5])
                ))

            # 保存到数据库
            await self._save_klines_to_db(klines, symbol, interval)

            logger.info(f"Retrieved {len(klines)} historical klines for {symbol}")
            return klines

        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []

    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """获取实时价格信息"""
        try:
            if not self.binance_client:
                logger.warning(f"Binance client not available, returning mock data for {symbol}")
                return self._get_mock_ticker(symbol)

            ticker_24hr = await self.binance_client.get_ticker_24hr(symbol)
            current_price = await self.binance_client.get_symbol_ticker(symbol)

            # 合并数据
            result = ticker_24hr.copy()
            result['current_price'] = float(current_price.get('price', 0))
            result['timestamp'] = int(datetime.now().timestamp() * 1000)

            return result

        except Exception as e:
            logger.error(f"Error getting ticker for {symbol}: {e}")
            logger.warning(f"Returning mock data for {symbol}")
            return self._get_mock_ticker(symbol)

    async def get_market_overview(self) -> Dict:
        """获取市场概览"""
        try:
            if not self.binance_client:
                raise Exception("Binance client not initialized")

            exchange_info = await self.binance_client.get_exchange_info()
            symbols_info = exchange_info.get('symbols', [])

            # 统计活跃交易对
            active_symbols = [s['symbol'] for s in symbols_info if s['status'] == 'TRADING']
            supported_symbols = self.binance_client.get_supported_symbols()

            return {
                'total_symbols': len(symbols_info),
                'active_symbols': len(active_symbols),
                'supported_symbols': supported_symbols,
                'api_mode': 'FULL_MODE' if self.binance_client.is_full_mode() else 'PUBLIC_MODE',
                'last_update': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {
                'total_symbols': 0,
                'active_symbols': 0,
                'supported_symbols': self.symbols,
                'api_mode': 'PUBLIC_MODE',
                'last_update': datetime.now()
            }

    async def start_real_time_data(self):
        """启动实时数据更新"""
        try:
            if self._is_running:
                return

            self._is_running = True

            # 为每个支持的交易对启动数据更新任务
            for symbol in self.symbols:
                task = asyncio.create_task(
                    self._update_symbol_data_periodically(symbol)
                )
                self._real_time_tasks[symbol] = task

            logger.info(f"Started real-time data updates for {len(self.symbols)} symbols")

        except Exception as e:
            logger.error(f"Error starting real-time data: {e}")

    async def _update_symbol_data_periodically(self, symbol: str):
        """定期更新单个交易对的数据"""
        try:
            while self._is_running:
                try:
                    # 获取最新的K线数据
                    latest_klines = await self.get_klines(
                        symbol=symbol,
                        interval=self.default_interval,
                        limit=10,
                        use_cache=False
                    )

                    if latest_klines:
                        logger.debug(f"Updated {symbol} data: latest price {latest_klines[-1].close_price}")

                except Exception as e:
                    logger.error(f"Error updating {symbol} data: {e}")

                # 等待下次更新（4小时K线，每5分钟更新一次）
                await asyncio.sleep(300)  # 5分钟

        except asyncio.CancelledError:
            logger.info(f"Real-time data update for {symbol} cancelled")
        except Exception as e:
            logger.error(f"Error in real-time data update for {symbol}: {e}")

    def get_supported_symbols(self) -> List[str]:
        """获取支持的交易对列表"""
        return self.symbols.copy()

    def get_supported_intervals(self) -> List[str]:
        """获取支持的时间间隔"""
        return ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']

    def _get_mock_ticker(self, symbol: str) -> Dict:
        """生成模拟价格数据"""
        import random
        
        # 基础价格
        base_prices = {
            'BTCUSDT': 45000.0,
            'ETHUSDT': 3200.0,
            'ADAUSDT': 0.45,
            'DOTUSDT': 6.5,
            'LINKUSDT': 15.0
        }
        
        base_price = base_prices.get(symbol.upper(), 100.0)
        
        # 添加随机波动
        change_percent = random.uniform(-5.0, 5.0)
        current_price = base_price * (1 + change_percent / 100)
        
        # 计算24小时变化
        price_change = current_price - base_price
        price_change_percent = (price_change / base_price) * 100
        
        # 生成高低价
        high_price = current_price * (1 + abs(random.uniform(0, 3)) / 100)
        low_price = current_price * (1 - abs(random.uniform(0, 3)) / 100)
        
        # 生成成交量
        volume = random.uniform(1000, 10000)
        quote_volume = volume * current_price
        
        return {
            'symbol': symbol.upper(),
            'price': f"{current_price:.2f}",
            'price_change': f"{price_change:.2f}",
            'price_change_percent': f"{price_change_percent:.2f}",
            'weighted_avg_price': f"{current_price:.2f}",
            'prev_close_price': f"{base_price:.2f}",
            'last_price': f"{current_price:.2f}",
            'last_qty': f"{random.uniform(0.1, 10):.4f}",
            'bid_price': f"{current_price * 0.999:.2f}",
            'ask_price': f"{current_price * 1.001:.2f}",
            'open_price': f"{base_price:.2f}",
            'high_price': f"{high_price:.2f}",
            'low_price': f"{low_price:.2f}",
            'volume': f"{volume:.2f}",
            'quote_volume': f"{quote_volume:.2f}",
            'open_time': int((datetime.now() - timedelta(hours=24)).timestamp() * 1000),
            'close_time': int(datetime.now().timestamp() * 1000),
            'first_id': random.randint(1000000, 9999999),
            'last_id': random.randint(1000000, 9999999),
            'count': random.randint(1000, 10000),
            'timestamp': int(datetime.now().timestamp() * 1000)
        }

    def _get_mock_klines(self, symbol: str, interval: str, limit: int) -> List[KLineData]:
        """生成模拟K线数据"""
        import random
        
        # 基础价格
        base_prices = {
            'BTCUSDT': 45000.0,
            'ETHUSDT': 3200.0,
            'ADAUSDT': 0.45,
            'DOTUSDT': 6.5,
            'LINKUSDT': 15.0
        }
        
        base_price = base_prices.get(symbol.upper(), 100.0)
        
        # 时间间隔转换为分钟
        interval_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360,
            '8h': 480, '12h': 720, '1d': 1440, '3d': 4320, '1w': 10080
        }
        
        minutes = interval_minutes.get(interval, 240)  # 默认4小时
        
        klines = []
        current_time = datetime.now()
        current_price = base_price
        
        for i in range(limit):
            # 计算时间
            open_time = current_time - timedelta(minutes=minutes * (limit - i))
            close_time = open_time + timedelta(minutes=minutes)
            
            # 生成价格数据
            price_change = random.uniform(-0.02, 0.02)  # ±2% 变化
            open_price = current_price
            close_price = open_price * (1 + price_change)
            
            # 生成高低价
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
            
            # 生成成交量
            volume = random.uniform(100, 1000)
            
            kline = KLineData(
                symbol=symbol.upper(),
                timeframe=interval,
                open_time=int(open_time.timestamp() * 1000),
                close_time=int(close_time.timestamp() * 1000),
                open_price=round(open_price, 2),
                high_price=round(high_price, 2),
                low_price=round(low_price, 2),
                close_price=round(close_price, 2),
                volume=round(volume, 2)
            )
            
            klines.append(kline)
            current_price = close_price
        
        return klines
