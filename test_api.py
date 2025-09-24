#!/usr/bin/env python3
"""
API测试脚本
"""

import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/",
        "/api/health",
        "/api/market/overview",
        "/api/market/ticker/BTCUSDT",
        "/api/market/ticker/ETHUSDT",
        "/api/market/klines/BTCUSDT?interval=4h&limit=10"
    ]
    
    print("🧪 测试API端点...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - 状态码: {response.status_code}")
                data = response.json()
                if "data" in data:
                    print(f"   数据: {json.dumps(data['data'], indent=2)[:100]}...")
                else:
                    print(f"   响应: {json.dumps(data, indent=2)[:100]}...")
            else:
                print(f"❌ {endpoint} - 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - 错误: {e}")
        
        print()
    
    print("🎉 API测试完成！")
    print("\n📱 前端访问地址: http://localhost:3000")
    print("📊 后端API地址: http://localhost:8000")
    print("📖 API文档地址: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api_endpoints()
