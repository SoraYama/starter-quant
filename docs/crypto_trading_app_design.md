# 加密货币量化交易应用设计方案

## 1. 项目概述

### 1.1 项目名称
CryptoQuantBot - 本地加密货币量化交易应用

### 1.2 项目目标
开发一个功能完整的本地部署量化交易应用，支持策略回测、实时交易信号生成、可视化分析等核心功能。

### 1.3 核心特性
- 跨平台本地部署（Windows/Mac/Linux）
- 直观的Web界面
- 多种技术指标组合
- 实时行情数据接入
- 完整的回测系统
- 币安交易所API集成

## 2. 系统架构设计

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                    Web Frontend                        │
│                  (React + TypeScript)                  │
├─────────────────────────────────────────────────────────┤
│                    API Gateway                         │
│                  (FastAPI + Python)                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │   Strategy  │ │    Market   │ │  Backtest   │        │
│  │   Engine    │ │    Data     │ │   Engine    │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│                  Data Storage                          │
│              (SQLite + Redis Cache)                    │
├─────────────────────────────────────────────────────────┤
│              External Services                         │
│          (Binance API + WebSocket)                     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 技术栈选择

#### 后端技术栈
- **主框架**: Python 3.9+ + FastAPI
- **数据库**: SQLite (本地存储) + Redis (缓存)
- **数据分析**: pandas, numpy, ta (技术分析库)
- **异步处理**: asyncio, websockets
- **API客户端**: python-binance

#### 前端技术栈
- **框架**: React 18 + TypeScript
- **图表库**: TradingView Lightweight Charts
- **UI组件**: Ant Design
- **状态管理**: Zustand
- **构建工具**: Vite

#### 部署技术栈
- **容器化**: Docker + Docker Compose
- **进程管理**: PM2 (Node.js应用)
- **反向代理**: Nginx

## 3. 功能模块设计

### 3.1 用户界面模块

#### 3.1.1 主控制台
- 系统状态监控
- 策略运行状态
- 实时PnL展示
- 快速操作面板

#### 3.1.2 回测模块
- **时间范围选择器**
  - 预设时间段（1天、1周、1月、3月、6月、1年、2年）
  - 自定义日期范围选择
- **K线图展示**
  - 支持多时间周期（1m, 5m, 15m, 1h, 4h, 1d）
  - 集成技术指标显示
  - 买卖信号标记
- **回测结果分析**
  - 收益率曲线图
  - 最大回撤分析
  - 夏普比率计算
  - 胜率统计
  - 详细交易记录

#### 3.1.3 实时交易模块
- 实时价格监控
- 持仓状态显示
- 订单管理界面
- 风险控制设置

#### 3.1.4 策略配置模块
- 技术指标参数调整
- 信号触发条件设置
- 风险管理参数
- 策略启停控制

### 3.2 数据获取模块

#### 3.2.1 历史数据获取
- 支持币安历史K线数据获取
- 数据时间范围：2022年至今（2年+数据）
- 支持多个交易对
- 数据缓存和增量更新

#### 3.2.2 实时数据流
- WebSocket连接币安实时行情
- Ticker数据处理
- K线数据实时更新
- 连接断线重连机制

### 3.3 策略引擎模块

#### 3.3.1 技术指标系统
**MACD (移动平均收敛散度)**
- 参数：快线(12)、慢线(26)、信号线(9)
- 信号：金叉买入、死叉卖出
- 强化信号：MACD柱状图变化

**RSI (相对强弱指数)**
- 参数：周期(14)
- 信号：超卖(<30)买入、超买(>70)卖出
- 背离信号检测

**布林带 (Bollinger Bands)**
- 参数：周期(20)、标准差(2)
- 信号：价格触及下轨买入、上轨卖出
- 布林带收缩/扩张趋势判断

#### 3.3.2 综合信号系统
**多指标组合逻辑**
```python
# 买入信号条件
def generate_buy_signal(data):
    macd_bullish = data['macd'] > data['macd_signal'] and data['macd_prev'] <= data['macd_signal_prev']
    rsi_oversold = data['rsi'] < 30
    bb_support = data['close'] <= data['bb_lower']

    return macd_bullish and (rsi_oversold or bb_support)

# 卖出信号条件
def generate_sell_signal(data):
    macd_bearish = data['macd'] < data['macd_signal'] and data['macd_prev'] >= data['macd_signal_prev']
    rsi_overbought = data['rsi'] > 70
    bb_resistance = data['close'] >= data['bb_upper']

    return macd_bearish and (rsi_overbought or bb_resistance)
```

#### 3.3.3 风险管理系统
- 止损止盈设置
- 最大持仓限制
- 每日最大亏损限制
- 连续亏损次数控制

### 3.4 回测引擎模块

#### 3.4.1 历史数据回测
- 基于历史K线数据模拟交易
- 支持滑点和手续费计算
- 多种订单类型模拟（市价单、限价单）
- 资金管理策略应用

#### 3.4.2 性能指标计算
- **收益指标**
  - 总收益率
  - 年化收益率
  - 月度收益率
- **风险指标**
  - 最大回撤
  - 夏普比率
  - 波动率
- **交易指标**
  - 胜率
  - 盈亏比
  - 交易频次

## 4. 数据库设计

### 4.1 SQLite数据表结构

```sql
-- 历史K线数据表
CREATE TABLE klines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open_time BIGINT NOT NULL,
    close_time BIGINT NOT NULL,
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    close_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe, open_time)
);

-- 交易信号表
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL, -- BUY/SELL
    price DECIMAL(20,8) NOT NULL,
    timestamp BIGINT NOT NULL,
    indicators TEXT, -- JSON格式存储指标数据
    confidence DECIMAL(3,2), -- 信号置信度
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 回测结果表
CREATE TABLE backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_name VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_balance DECIMAL(20,8) NOT NULL,
    final_balance DECIMAL(20,8) NOT NULL,
    total_return DECIMAL(10,4) NOT NULL,
    max_drawdown DECIMAL(10,4) NOT NULL,
    sharpe_ratio DECIMAL(10,4),
    win_rate DECIMAL(5,2) NOT NULL,
    total_trades INTEGER NOT NULL,
    config TEXT, -- 策略配置JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 交易记录表
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backtest_id INTEGER,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- BUY/SELL
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    timestamp BIGINT NOT NULL,
    pnl DECIMAL(20,8),
    FOREIGN KEY (backtest_id) REFERENCES backtest_results(id)
);
```

## 5. API接口设计

### 5.1 RESTful API规范

```python
# 市场数据接口
GET /api/v1/market/klines/{symbol}?interval=1h&limit=1000
GET /api/v1/market/ticker/{symbol}
GET /api/v1/market/symbols

# 策略管理接口
GET /api/v1/strategies
POST /api/v1/strategies
PUT /api/v1/strategies/{id}
DELETE /api/v1/strategies/{id}

# 回测接口
POST /api/v1/backtest/run
GET /api/v1/backtest/results/{id}
GET /api/v1/backtest/history

# 实时交易接口
GET /api/v1/trading/positions
POST /api/v1/trading/order
GET /api/v1/trading/orders
DELETE /api/v1/trading/orders/{id}

# 系统配置接口
GET /api/v1/config
PUT /api/v1/config
```

### 5.2 WebSocket接口

```javascript
// 实时价格推送
ws://localhost:8000/ws/market/{symbol}

// 交易信号推送
ws://localhost:8000/ws/signals

// 系统状态推送
ws://localhost:8000/ws/status
```

## 6. 部署方案设计

### 6.1 跨平台支持策略

#### 6.1.1 Docker容器化部署
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 6.1.2 Docker Compose配置
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./data:/app/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - app
```

#### 6.1.3 一键部署脚本

**Windows部署 (deploy.bat)**
```batch
@echo off
echo Starting CryptoQuantBot deployment...

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM 构建和启动服务
docker-compose up -d --build

echo Deployment completed!
echo Access the application at: http://localhost:3000
pause
```

**Mac/Linux部署 (deploy.sh)**
```bash
#!/bin/bash
echo "Starting CryptoQuantBot deployment..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# 设置执行权限
chmod +x deploy.sh

# 构建和启动服务
docker-compose up -d --build

echo "Deployment completed!"
echo "Access the application at: http://localhost:3000"
```

### 6.2 原生安装方案

#### 6.2.1 Python环境安装脚本
```python
# install.py
import subprocess
import sys
import os

def check_python_version():
    if sys.version_info < (3, 9):
        print("Python 3.9+ is required")
        sys.exit(1)

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_database():
    # 创建SQLite数据库和表结构
    pass

def main():
    check_python_version()
    install_requirements()
    setup_database()
    print("Installation completed!")

if __name__ == "__main__":
    main()
```

## 7. 配置管理

### 7.1 应用配置文件
```yaml
# config.yaml
app:
  name: "CryptoQuantBot"
  version: "1.0.0"
  host: "0.0.0.0"
  port: 8000
  debug: false

database:
  sqlite_path: "./data/trading.db"
  redis_url: "redis://localhost:6379"

binance:
  api_key: ""
  api_secret: ""
  testnet: true

trading:
  default_symbol: "BTCUSDT"
  max_position_size: 0.1
  stop_loss_percent: 2.0
  take_profit_percent: 4.0

strategies:
  macd:
    fast_period: 12
    slow_period: 26
    signal_period: 9
  rsi:
    period: 14
    oversold: 30
    overbought: 70
  bollinger_bands:
    period: 20
    std_dev: 2
```

## 8. 开发计划与里程碑

### 8.1 Phase 1: 基础架构 (第1-2周)
- [ ] 项目结构搭建
- [ ] 数据库设计与创建
- [ ] 基础API框架搭建
- [ ] Docker环境配置

### 8.2 Phase 2: 数据模块 (第3-4周)
- [ ] 币安API集成
- [ ] 历史数据获取功能
- [ ] 实时数据推送功能
- [ ] 数据存储和缓存系统

### 8.3 Phase 3: 策略引擎 (第5-6周)
- [ ] 技术指标计算
- [ ] 信号生成逻辑
- [ ] 风险管理系统
- [ ] 策略配置管理

### 8.4 Phase 4: 回测系统 (第7-8周)
- [ ] 回测引擎开发
- [ ] 性能指标计算
- [ ] 回测结果存储
- [ ] 报告生成功能

### 8.5 Phase 5: 前端开发 (第9-10周)
- [ ] React应用搭建
- [ ] K线图组件集成
- [ ] 回测界面开发
- [ ] 实时监控界面

### 8.6 Phase 6: 集成测试 (第11-12周)
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 部署脚本完善
- [ ] 文档编写

## 9. 风险评估与缓解

### 9.1 技术风险
- **API限制**: 币安API有频率限制，需要实现请求队列和重试机制
- **数据质量**: 历史数据可能存在缺失，需要数据验证和补全机制
- **系统稳定性**: 长时间运行可能出现内存泄漏，需要监控和重启机制

### 9.2 缓解措施
- 实现API请求缓存和限流
- 建立数据质量检查机制
- 添加系统监控和自动恢复功能
- 实现完整的日志记录系统

## 10. 成功标准

### 10.1 功能完整性
- [ ] 所有核心功能正常运行
- [ ] 支持3个操作系统平台部署
- [ ] 2年历史数据回测能力
- [ ] 实时行情接入正常

### 10.2 性能指标
- [ ] 回测速度: 2年数据在5分钟内完成
- [ ] 实时延迟: 行情数据延迟<100ms
- [ ] 系统稳定性: 连续运行24小时无崩溃

### 10.3 用户体验
- [ ] 一键部署成功率>90%
- [ ] 界面响应时间<2秒
- [ ] 操作流程直观易懂

---

## 总结

本设计方案提供了一个完整的加密货币量化交易应用架构，涵盖了从技术选型到部署策略的各个方面。该方案支持跨平台部署，具备完整的回测功能和实时交易能力，能够满足量化交易的基本需求。
