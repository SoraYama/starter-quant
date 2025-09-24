"""
WebSocket管理器
负责实时数据推送和客户端连接管理
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活跃连接
        self.active_connections: List[WebSocket] = []
        # 订阅管理 {symbol: {websockets}}
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        # 连接元数据
        self.connection_info: Dict[WebSocket, Dict] = {}
        # 是否运行中
        self.is_running = False
        
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """接受WebSocket连接"""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            
            # 存储连接信息
            self.connection_info[websocket] = {
                'client_id': client_id or f"client_{len(self.active_connections)}",
                'connected_at': datetime.now(),
                'subscriptions': set()
            }
            
            logger.info(f"WebSocket连接已建立: {self.connection_info[websocket]['client_id']}")
            
            # 发送欢迎消息
            await self.send_personal_message({
                'type': 'connection',
                'status': 'connected',
                'client_id': self.connection_info[websocket]['client_id'],
                'timestamp': datetime.now().isoformat()
            }, websocket)
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            await self.disconnect(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            # 清理订阅
            if websocket in self.connection_info:
                client_info = self.connection_info[websocket]
                for symbol in client_info.get('subscriptions', set()):
                    if symbol in self.subscriptions:
                        self.subscriptions[symbol].discard(websocket)
                        if not self.subscriptions[symbol]:
                            del self.subscriptions[symbol]
                
                client_id = client_info.get('client_id', 'unknown')
                logger.info(f"WebSocket连接已断开: {client_id}")
                del self.connection_info[websocket]
                
        except Exception as e:
            logger.error(f"WebSocket断开处理失败: {e}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"发送个人消息失败: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """向订阅特定交易对的客户端广播消息"""
        if symbol not in self.subscriptions:
            return
        
        disconnected = []
        for websocket in self.subscriptions[symbol].copy():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"向{symbol}订阅者广播失败: {e}")
                disconnected.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def subscribe_symbol(self, websocket: WebSocket, symbol: str):
        """订阅交易对实时数据"""
        try:
            if symbol not in self.subscriptions:
                self.subscriptions[symbol] = set()
            
            self.subscriptions[symbol].add(websocket)
            
            # 更新连接信息
            if websocket in self.connection_info:
                self.connection_info[websocket]['subscriptions'].add(symbol)
            
            await self.send_personal_message({
                'type': 'subscription',
                'action': 'subscribed',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }, websocket)
            
            logger.info(f"客户端订阅 {symbol}: {self.connection_info[websocket]['client_id']}")
            
        except Exception as e:
            logger.error(f"订阅失败: {e}")
    
    async def unsubscribe_symbol(self, websocket: WebSocket, symbol: str):
        """取消订阅交易对"""
        try:
            if symbol in self.subscriptions:
                self.subscriptions[symbol].discard(websocket)
                if not self.subscriptions[symbol]:
                    del self.subscriptions[symbol]
            
            # 更新连接信息
            if websocket in self.connection_info:
                self.connection_info[websocket]['subscriptions'].discard(symbol)
            
            await self.send_personal_message({
                'type': 'subscription',
                'action': 'unsubscribed',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }, websocket)
            
            logger.info(f"客户端取消订阅 {symbol}: {self.connection_info[websocket]['client_id']}")
            
        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                symbol = data.get('symbol')
                if symbol:
                    await self.subscribe_symbol(websocket, symbol.upper())
                    
            elif message_type == 'unsubscribe':
                symbol = data.get('symbol')
                if symbol:
                    await self.unsubscribe_symbol(websocket, symbol.upper())
                    
            elif message_type == 'ping':
                await self.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }, websocket)
                
            elif message_type == 'get_status':
                await self.send_status(websocket)
                
            else:
                await self.send_personal_message({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}',
                    'timestamp': datetime.now().isoformat()
                }, websocket)
                
        except json.JSONDecodeError:
            await self.send_personal_message({
                'type': 'error',
                'message': 'Invalid JSON format',
                'timestamp': datetime.now().isoformat()
            }, websocket)
        except Exception as e:
            logger.error(f"处理客户端消息失败: {e}")
            await self.send_personal_message({
                'type': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }, websocket)
    
    async def send_status(self, websocket: WebSocket):
        """发送连接状态信息"""
        try:
            client_info = self.connection_info.get(websocket, {})
            status = {
                'type': 'status',
                'client_id': client_info.get('client_id'),
                'connected_at': client_info.get('connected_at', datetime.now()).isoformat(),
                'subscriptions': list(client_info.get('subscriptions', set())),
                'total_connections': len(self.active_connections),
                'active_subscriptions': len(self.subscriptions),
                'timestamp': datetime.now().isoformat()
            }
            
            await self.send_personal_message(status, websocket)
            
        except Exception as e:
            logger.error(f"发送状态信息失败: {e}")
    
    async def send_price_update(self, symbol: str, price_data: dict):
        """发送价格更新"""
        message = {
            'type': 'price_update',
            'symbol': symbol,
            'data': price_data,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_to_symbol(symbol, message)
    
    async def send_signal_update(self, symbol: str, signal_data: dict):
        """发送交易信号更新"""
        message = {
            'type': 'signal_update',
            'symbol': symbol,
            'data': signal_data,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_to_symbol(symbol, message)
    
    async def send_market_update(self, market_data: dict):
        """发送市场数据更新"""
        message = {
            'type': 'market_update',
            'data': market_data,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast(message)
    
    def get_connection_stats(self) -> dict:
        """获取连接统计信息"""
        return {
            'total_connections': len(self.active_connections),
            'active_subscriptions': len(self.subscriptions),
            'subscriptions_detail': {
                symbol: len(connections) 
                for symbol, connections in self.subscriptions.items()
            },
            'uptime': datetime.now().isoformat() if self.is_running else None
        }
    
    async def close_all(self):
        """关闭所有连接"""
        try:
            disconnected_count = 0
            for websocket in self.active_connections.copy():
                try:
                    await websocket.close()
                    disconnected_count += 1
                except Exception as e:
                    logger.error(f"关闭WebSocket连接失败: {e}")
            
            # 清理所有数据
            self.active_connections.clear()
            self.subscriptions.clear()
            self.connection_info.clear()
            self.is_running = False
            
            logger.info(f"已关闭 {disconnected_count} 个WebSocket连接")
            
        except Exception as e:
            logger.error(f"关闭所有连接失败: {e}")

# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()
