# CryptoQuantBot - 加密货币量化交易应用

🚀 **专业的本地部署加密货币量化交易系统**

一个功能完整的加密货币量化交易应用，支持策略回测、实时数据分析、多指标技术分析和自动化交易。

## ✨ 核心功能特性

### 📊 可视化回测系统
- **专业K线图表**: 集成TradingView图表库，提供专业级交易界面
- **灵活时间范围**: 支持2年历史数据回测分析
- **完整性能指标**: 收益率曲线、夏普比率、最大回撤、胜率分析
- **详细交易记录**: 完整的交易历史和盈亏分析

### 🎯 智能策略系统
- **多指标组合**: MACD + RSI + 布林带三重技术指标
- **信号生成逻辑**:
  - MACD金叉死叉信号识别
  - RSI超买超卖判断（30/70阈值）
  - 布林带支撑阻力位分析
- **策略强度评估**: 智能组合信号生成和置信度评分

### 🔌 数据与交易集成
- **币安API完整对接**: 支持实时行情和交易执行
- **双模式运行**:
  - 公开数据模式：免费获取市场数据
  - 完整功能模式：支持真实账户交易
- **实时数据推送**: WebSocket实时价格更新
- **风险管理**: 止损止盈、仓位管理、风险控制

### 🚀 跨平台部署
- **一键部署**: Windows/Mac/Linux一键部署脚本
- **Docker容器化**: 完整的容器化部署方案
- **配置管理**: 灵活的配置系统，支持环境切换

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.11**: 现代Python运行环境
- **FastAPI**: 高性能异步Web框架
- **SQLAlchemy**: 强大的ORM数据库管理
- **SQLite**: 轻量级本地数据库
- **Redis**: 高速缓存和会话管理
- **Pandas/NumPy**: 专业数据分析和计算

### 前端技术栈
- **React 18**: 现代化前端框架
- **TypeScript**: 类型安全的JavaScript
- **Ant Design**: 企业级UI组件库
- **TradingView Charts**: 专业金融图表
- **React Query**: 智能数据管理

### 部署技术
- **Docker**: 容器化部署
- **Nginx**: 反向代理和静态文件服务
- **Docker Compose**: 多服务编排

## 📦 快速开始

### 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Docker**: 20.10+ 
- **Docker Compose**: 1.29+
- **内存**: 至少4GB RAM
- **存储**: 至少2GB可用空间

### 一键部署

#### Windows用户
```cmd
git clone <repository-url>
cd crypto_trading_app
deploy.bat
```

#### Mac/Linux用户
```bash
git clone <repository-url>
cd crypto_trading_app
chmod +x deploy.sh
./deploy.sh
```

#### Docker部署
```bash
docker-compose up -d
```

### 访问应用
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## ⚙️ 配置说明

### 环境变量配置（.env文件）
```bash
# API模式配置
BINANCE_API_MODE=PUBLIC_MODE          # 公开数据模式
BINANCE_API_KEY=                      # 币安API密钥（可选）
BINANCE_API_SECRET=                   # 币安API密钥（可选）
BINANCE_TESTNET=true                  # 是否使用测试网

# 支持的交易对
BINANCE_SYMBOLS=BTCUSDT,ETHUSDT       # 默认交易对
BINANCE_DEFAULT_INTERVAL=4h           # 默认分析周期

# 服务端口
BACKEND_PORT=8000                     # 后端服务端口
FRONTEND_PORT=3000                    # 前端服务端口
```

### 币安API配置（可选）
1. 查看 `binance_api_guide.md` 文件获取详细的API密钥申请指南
2. 在应用设置页面配置API密钥
3. 切换到完整功能模式启用真实交易

## 🎮 使用指南

### 1. 仪表板
- 实时价格监控
- 市场概览信息
- 最新交易信号
- 价格提醒设置

### 2. 市场数据
- 实时K线图表
- 技术指标分析
- 价格提醒管理
- 历史数据查询

### 3. 策略分析
- 多指标技术分析
- 信号强度评估
- 策略参数调整
- 历史信号回顾

### 4. 回测系统
- 历史数据回测
- 性能指标分析
- 收益率计算
- 风险评估报告

### 5. 交易管理
- 模拟交易操作
- 订单管理
- 仓位监控
- 交易历史

### 6. 系统设置
- API密钥配置
- 策略参数调整
- 风险管理设置
- 通知配置

## 📊 支持的技术指标

### MACD (移动平均收敛散度)
- **快线**: 12周期EMA
- **慢线**: 26周期EMA  
- **信号线**: 9周期EMA
- **信号**: 金叉买入，死叉卖出

### RSI (相对强弱指标)
- **周期**: 14
- **超买阈值**: 70
- **超卖阈值**: 30
- **信号**: 超卖买入，超买卖出

### 布林带 (Bollinger Bands)
- **周期**: 20
- **标准差**: 2.0
- **信号**: 价格触及下轨买入，上轨卖出

## 🔧 开发与定制

### 本地开发环境搭建
```bash
# 后端开发
cd backend
pip install -r requirements.txt
python main.py

# 前端开发  
cd frontend
npm install
npm run dev
```

### 添加新的技术指标
1. 在 `backend/app/services/technical_indicators.py` 添加指标计算函数
2. 在 `backend/app/services/strategy_engine.py` 集成新指标
3. 更新前端显示组件

### 添加新的交易对
1. 在配置文件中添加新的symbol
2. 确保币安API支持该交易对
3. 更新前端选择器选项

## 🛡️ 安全注意事项

- **API密钥安全**: 
  - 仅授予必要权限（现货交易、读取权限）
  - 定期更换API密钥
  - 不要在代码中硬编码密钥

- **网络安全**:
  - 使用测试网进行初期测试
  - 启用IP白名单限制
  - 定期检查账户安全

- **资金安全**:
  - 从小额开始测试
  - 设置合理的止损点
  - 定期备份交易数据

## 📁 项目结构
```
crypto_trading_app/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # 数据模式
│   │   └── services/       # 业务逻辑
│   ├── config.yaml         # 配置文件
│   ├── main.py            # 应用入口
│   └── requirements.txt    # Python依赖

├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   └── types/         # TypeScript类型
│   ├── package.json       # Node.js依赖
│   └── vite.config.ts     # 构建配置

├── data/                   # 数据目录
│   ├── db/                # 数据库文件
│   ├── logs/              # 日志文件
│   └── backups/           # 备份文件

├── docker-compose.yml      # Docker编排文件
├── deploy.sh              # Linux/Mac部署脚本
├── deploy.bat             # Windows部署脚本
├── .env                   # 环境变量配置
└── README.md              # 项目说明
```

## 🤝 贡献指南

欢迎贡献代码和提出建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持与帮助

### 常见问题
- **Docker启动失败**: 检查Docker服务是否运行，端口是否被占用
- **API连接失败**: 验证网络连接和API密钥配置
- **数据显示异常**: 检查Redis服务状态和数据库连接

### 获取帮助
- 查看 [binance_api_guide.md](binance_api_guide.md) 获取API配置帮助
- 检查 `data/logs/` 目录中的日志文件
- 使用 `docker-compose logs` 查看容器日志

### 联系方式
- 提交 Issue 报告问题
- 参与 Discussion 讨论功能

---

⭐ **如果这个项目对您有帮助，请给我们一个星标！**

**免责声明**: 本软件仅供学习和研究使用。加密货币交易存在风险，请谨慎操作，软件开发者不承担任何交易损失责任。
