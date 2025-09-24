"""
代理管理器
支持HTTP和SOCKS代理
"""

import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import aiohttp
from aiohttp_socks import ProxyConnector

logger = logging.getLogger(__name__)

class ProxyManager:
    """代理管理器"""

    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url
        self.connector: Optional[aiohttp.BaseConnector] = None

        if proxy_url:
            self._setup_proxy()

    def _setup_proxy(self):
        """设置代理连接器"""
        try:
            parsed_url = urlparse(self.proxy_url)
            scheme = parsed_url.scheme.lower()

            if scheme in ['http', 'https']:
                # HTTP代理
                self.connector = aiohttp.TCPConnector()
                logger.info(f"HTTP proxy configured: {self.proxy_url}")

            elif scheme in ['socks4', 'socks5']:
                # SOCKS代理
                self.connector = ProxyConnector.from_url(self.proxy_url)
                logger.info(f"SOCKS proxy configured: {self.proxy_url}")

            else:
                logger.warning(f"Unsupported proxy scheme: {scheme}")
                self.connector = None

        except Exception as e:
            logger.error(f"Failed to setup proxy: {e}")
            self.connector = None

    def get_connector(self) -> Optional[aiohttp.BaseConnector]:
        """获取连接器"""
        return self.connector

    def get_proxy_config(self) -> Dict[str, Any]:
        """获取代理配置"""
        if not self.proxy_url:
            return {}

        parsed_url = urlparse(self.proxy_url)
        scheme = parsed_url.scheme.lower()

        if scheme in ['http', 'https']:
            return {
                'proxy': self.proxy_url,
                'connector': self.connector
            }
        elif scheme in ['socks4', 'socks5']:
            return {
                'connector': self.connector
            }

        return {}

    def is_enabled(self) -> bool:
        """检查代理是否启用"""
        return self.proxy_url is not None and self.connector is not None

    def create_session(self) -> aiohttp.ClientSession:
        """创建带代理的aiohttp会话"""
        proxy_config = self.get_proxy_config()
        return aiohttp.ClientSession(**proxy_config)
