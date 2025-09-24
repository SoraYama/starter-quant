"""
Configuration management for CryptoQuantBot
配置管理模块
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
import yaml

class Settings(BaseSettings):
    """应用配置"""

    # App Settings
    app_name: str = "CryptoQuantBot"
    app_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:3000"]

    # Database Settings
    sqlite_path: str = "./data/trading.db"
    redis_url: str = "redis://localhost:6379"

    # Proxy Settings
    proxy_url: Optional[str] = None

    # Binance API Settings
    binance_api_key: str = ""
    binance_api_secret: str = ""
    binance_testnet: bool = False
    binance_public_data_only: bool = True
    binance_base_url: str = "https://api.binance.com"
    binance_testnet_url: str = "https://testnet.binance.vision"
    binance_symbols: List[str] = ["BTCUSDT", "ETHUSDT"]
    binance_default_interval: str = "4h"

    # Proxy Settings
    proxy_url: Optional[str] = None

    # Trading Settings
    trading_max_position_size: float = 0.1
    trading_stop_loss_percent: float = 2.0
    trading_take_profit_percent: float = 4.0

    # Strategy Settings
    macd_fast_period: int = 12
    macd_slow_period: int = 26
    macd_signal_period: int = 9
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70
    bb_period: int = 20
    bb_std_dev: float = 2.0

    # Backtest Settings
    backtest_initial_balance: float = 10000.0
    backtest_commission: float = 0.001
    backtest_slippage: float = 0.001
    backtest_max_history_days: int = 730

    class Config:
        env_prefix = "CRYPTO_"
        case_sensitive = False

def load_config_from_yaml(config_path: str = "config.yaml") -> dict:
    """从YAML文件加载配置"""
    if not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Failed to load config from {config_path}: {e}")
        return {}

def create_settings() -> Settings:
    """创建配置实例，支持YAML文件覆盖"""
    # 加载YAML配置
    yaml_config = load_config_from_yaml()

    # 展平YAML配置以匹配Pydantic字段名
    flat_config = {}

    if 'app' in yaml_config:
        app_config = yaml_config['app']
        flat_config.update({
            'app_name': app_config.get('name', 'CryptoQuantBot'),
            'app_version': app_config.get('version', '1.0.0'),
            'app_host': app_config.get('host', '0.0.0.0'),
            'app_port': app_config.get('port', 8000),
            'debug': app_config.get('debug', False),
            'cors_origins': app_config.get('cors_origins', ["http://localhost:3000"])
        })

    if 'database' in yaml_config:
        db_config = yaml_config['database']
        flat_config.update({
            'sqlite_path': db_config.get('sqlite_path', './data/trading.db'),
            'redis_url': db_config.get('redis_url', 'redis://localhost:6379')
        })

    if 'binance' in yaml_config:
        binance_config = yaml_config['binance']
        flat_config.update({
            'binance_api_key': binance_config.get('api_key', ''),
            'binance_api_secret': binance_config.get('api_secret', ''),
            'binance_testnet': binance_config.get('testnet', False),
            'binance_public_data_only': binance_config.get('public_data_only', True),
            'binance_base_url': binance_config.get('base_url', 'https://api.binance.com'),
            'binance_testnet_url': binance_config.get('testnet_url', 'https://testnet.binance.vision'),
            'binance_symbols': binance_config.get('symbols', ['BTCUSDT', 'ETHUSDT']),
            'binance_default_interval': binance_config.get('default_interval', '4h')
        })

    # 添加代理配置支持
    if 'proxy' in yaml_config:
        proxy_config = yaml_config['proxy']
        flat_config.update({
            'proxy_url': proxy_config.get('url', None)
        })

    if 'trading' in yaml_config:
        trading_config = yaml_config['trading']
        flat_config.update({
            'trading_max_position_size': trading_config.get('max_position_size', 0.1),
            'trading_stop_loss_percent': trading_config.get('stop_loss_percent', 2.0),
            'trading_take_profit_percent': trading_config.get('take_profit_percent', 4.0)
        })

    if 'strategies' in yaml_config:
        strategies = yaml_config['strategies']
        if 'macd' in strategies:
            macd = strategies['macd']
            flat_config.update({
                'macd_fast_period': macd.get('fast_period', 12),
                'macd_slow_period': macd.get('slow_period', 26),
                'macd_signal_period': macd.get('signal_period', 9)
            })

        if 'rsi' in strategies:
            rsi = strategies['rsi']
            flat_config.update({
                'rsi_period': rsi.get('period', 14),
                'rsi_oversold': rsi.get('oversold', 30),
                'rsi_overbought': rsi.get('overbought', 70)
            })

        if 'bollinger_bands' in strategies:
            bb = strategies['bollinger_bands']
            flat_config.update({
                'bb_period': bb.get('period', 20),
                'bb_std_dev': bb.get('std_dev', 2.0)
            })

    if 'backtest' in yaml_config:
        backtest_config = yaml_config['backtest']
        flat_config.update({
            'backtest_initial_balance': backtest_config.get('initial_balance', 10000.0),
            'backtest_commission': backtest_config.get('commission', 0.001),
            'backtest_slippage': backtest_config.get('slippage', 0.001),
            'backtest_max_history_days': backtest_config.get('max_history_days', 730)
        })

    # 环境变量优先级更高，会覆盖YAML配置
    return Settings(**flat_config)

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（缓存）"""
    return create_settings()

# 配置检测函数
def detect_api_mode() -> str:
    """检测API配置模式"""
    settings = get_settings()

    # 检查环境变量
    api_key = os.getenv('BINANCE_API_KEY') or settings.binance_api_key
    api_secret = os.getenv('BINANCE_API_SECRET') or settings.binance_api_secret

    if api_key and api_secret:
        return "FULL_MODE"
    else:
        return "PUBLIC_MODE"

def get_binance_config() -> dict:
    """获取币安API配置"""
    settings = get_settings()
    mode = detect_api_mode()

    config = {
        'mode': mode,
        'symbols': settings.binance_symbols,
        'default_interval': settings.binance_default_interval,
        'testnet': settings.binance_testnet
    }

    if mode == "FULL_MODE":
        config.update({
            'api_key': os.getenv('BINANCE_API_KEY') or settings.binance_api_key,
            'api_secret': os.getenv('BINANCE_API_SECRET') or settings.binance_api_secret,
            'base_url': settings.binance_testnet_url if settings.binance_testnet else settings.binance_base_url
        })
    else:
        config.update({
            'base_url': settings.binance_base_url,
            'public_only': True
        })

    return config
