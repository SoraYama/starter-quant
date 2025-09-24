"""
Database configuration and models
数据库配置和模型
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """数据库模型基类"""
    pass

# 全局数据库引擎和会话
engine = None
async_session_maker = None

def get_database_url() -> str:
    """获取数据库URL"""
    settings = get_settings()
    # 确保数据目录存在
    db_dir = os.path.dirname(settings.sqlite_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    return f"sqlite+aiosqlite:///{settings.sqlite_path}"

async def init_database():
    """初始化数据库"""
    global engine, async_session_maker

    database_url = get_database_url()
    logger.info(f"Initializing database: {database_url}")

    # 创建异步引擎
    engine = create_async_engine(
        database_url,
        echo=False,  # 设置为True可以看到SQL日志
        future=True
    )

    # 创建会话工厂
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # 创建所有表
    async with engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from ..models import kline, signal, backtest, trade

        # 创建表，忽略已存在的索引错误
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            if "already exists" in str(e):
                logger.warning(f"Some database objects already exist: {e}")
            else:
                raise

    logger.info("Database initialized successfully")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    if async_session_maker is None:
        await init_database()

    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def close_database():
    """关闭数据库连接"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")
