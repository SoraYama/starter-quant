#!/usr/bin/env python3
"""
WebSocket 连接测试脚本
"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        # 添加额外的头部信息
        extra_headers = {
            "User-Agent": "WebSocketTest/1.0"
        }
        
        async with websockets.connect(uri, extra_headers=extra_headers) as websocket:
            print("✅ WebSocket 连接成功!")
            
            # 发送测试消息
            test_message = {
                "type": "ping",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 发送测试消息:", test_message)
            
            # 接收响应
            response = await websocket.recv()
            print("📥 收到响应:", response)
            
            # 订阅测试
            subscribe_message = {
                "type": "subscribe",
                "symbol": "BTCUSDT"
            }
            
            await websocket.send(json.dumps(subscribe_message))
            print("📤 发送订阅消息:", subscribe_message)
            
            # 等待一段时间接收数据
            print("⏳ 等待实时数据...")
            for i in range(3):
                try:
                    data = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"📥 收到数据 {i+1}:", data)
                except asyncio.TimeoutError:
                    print(f"⏰ 等待数据超时 {i+1}")
                    break
                    
    except Exception as e:
        print(f"❌ WebSocket 连接失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试 WebSocket 连接...")
    asyncio.run(test_websocket())
