#!/usr/bin/env python3
"""
代理功能测试脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.proxy import ProxyManager
from app.core.config import get_settings
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_proxy():
    """测试代理功能"""
    settings = get_settings()

    print("=== 代理配置测试 ===")
    print(f"配置的代理URL: {settings.proxy_url}")

    if not settings.proxy_url:
        print("❌ 未配置代理URL")
        print("请在config.yaml中设置proxy.url或在环境变量中设置PROXY_URL")
        return

    # 创建代理管理器
    proxy_manager = ProxyManager(settings.proxy_url)

    # 测试连接器创建
    print("\n=== 测试连接器创建 ===")
    connector = proxy_manager.create_connector()
    if connector:
        print("✅ 代理连接器创建成功")
        print(f"连接器类型: {type(connector).__name__}")
    else:
        print("❌ 代理连接器创建失败")
        return

    # 测试会话创建
    print("\n=== 测试会话创建 ===")
    session = proxy_manager.create_session()
    if session:
        print("✅ 代理会话创建成功")
    else:
        print("❌ 代理会话创建失败")
        return

    # 测试HTTP请求
    print("\n=== 测试HTTP请求 ===")
    try:
        # 测试币安API连接
        url = "https://api.binance.com/api/v3/ping"
        async with session.get(url) as response:
            if response.status == 200:
                print("✅ 通过代理成功连接到币安API")
                data = await response.text()
                print(f"响应: {data}")
            else:
                print(f"❌ 代理请求失败，状态码: {response.status}")
    except Exception as e:
        print(f"❌ 代理请求异常: {e}")
    finally:
        await session.close()

    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_proxy())
