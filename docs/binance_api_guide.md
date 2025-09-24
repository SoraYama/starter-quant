# 币安API密钥获取指南

## 📋 概述

本指南将详细说明如何获取币安交易所的API密钥，用于CryptoQuantBot应用的完整功能模式。

## 🚀 获取步骤

### 步骤1：注册币安账户

1. 访问币安官网：https://www.binance.com
2. 点击右上角"注册"按钮
3. 使用邮箱或手机号完成注册
4. 完成邮箱/手机验证

### 步骤2：完成身份验证（KYC）

⚠️ **重要提示**：获取API密钥需要完成身份验证

1. 登录币安账户
2. 进入"用户中心" → "身份认证"
3. 上传身份证件照片
4. 完成人脸识别验证
5. 等待审核通过（通常1-3个工作日）

### 步骤3：创建API密钥

1. **进入API管理页面**
   - 登录币安账户
   - 点击右上角头像 → "API管理"
   - 或直接访问：https://www.binance.com/zh-CN/my/settings/api-management

2. **创建新的API密钥**
   - 点击"创建API"按钮
   - 输入API标签名称（例如：CryptoQuantBot）
   - 完成安全验证（邮箱/手机验证码）

3. **设置API权限**
   ```
   ✅ 启用阅读 (Enable Reading) - 必需
   ❌ 启用现货和杠杆交易 (Enable Spot & Margin Trading) - 开发阶段暂不启用
   ❌ 启用期货交易 (Enable Futures) - 开发阶段暂不启用
   ❌ 启用提现 (Enable Withdrawals) - 不建议启用
   ```

4. **获取密钥信息**
   - **API Key**: 公开密钥（用于身份识别）
   - **Secret Key**: 私密密钥（用于签名请求）⚠️ 仅显示一次，务必保存

## 🔒 安全注意事项

### API密钥安全管理
- ❌ 绝不在代码中硬编码API密钥
- ✅ 使用环境变量或配置文件存储
- ✅ 定期更换API密钥
- ✅ 设置IP白名单限制访问

### 权限最小化原则
- 开发测试阶段：仅启用"阅读"权限
- 生产交易阶段：根据需要逐步开启其他权限
- 不要同时启用所有权限

### IP白名单设置
1. 在API管理页面点击"编辑限制"
2. 添加您的服务器IP地址
3. 建议使用固定IP或VPS

## 🧪 测试网API（推荐开发使用）

币安提供测试网环境，无需真实资金即可测试：

### 测试网特点
- 完全免费使用
- 功能与主网相同
- 使用虚拟资金测试
- 适合开发和调试

### 获取测试网API
1. 访问币安测试网：https://testnet.binance.vision/
2. 使用GitHub账户登录
3. 直接获取测试网API密钥
4. 无需KYC验证

### 测试网配置示例
```yaml
# config.yaml
binance:
  api_key: "your_testnet_api_key"
  api_secret: "your_testnet_api_secret"
  testnet: true  # 启用测试网模式
  base_url: "https://testnet.binance.vision"
```

## 🔄 CryptoQuantBot配置

### 公开数据模式配置
```yaml
# config.yaml - 公开数据模式
binance:
  api_key: ""  # 留空
  api_secret: ""  # 留空
  testnet: false
  public_data_only: true  # 仅使用公开数据
```

### 完整功能模式配置
```yaml
# config.yaml - 完整功能模式
binance:
  api_key: "your_api_key_here"
  api_secret: "your_api_secret_here"
  testnet: false  # 生产环境设为false，测试环境设为true
  public_data_only: false
```

### 环境变量配置（推荐）
```bash
# .env文件
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=false
```

## 📊 API使用限制

### 请求频率限制
- **Spot API**: 1200 requests per minute
- **WebSocket**: 5 connections per IP
- **历史数据**: 每个端点有不同限制

### 权重系统
- 每个API请求消耗不同权重
- 权重限制：1200 per minute
- 超限将被暂时封禁

## 🛠️ 应用中的配置切换

### 自动配置检测
```python
# 应用启动时自动检测配置模式
def detect_api_mode():
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if api_key and api_secret:
        return "FULL_MODE"  # 完整功能模式
    else:
        return "PUBLIC_MODE"  # 公开数据模式
```

### 功能对比
| 功能 | 公开数据模式 | 完整功能模式 |
|------|-------------|-------------|
| 实时价格 | ✅ | ✅ |
| 历史K线 | ✅ | ✅ |
| 账户信息 | ❌ | ✅ |
| 下单交易 | ❌ | ✅ |
| 持仓查询 | ❌ | ✅ |
| 交易历史 | ❌ | ✅ |

## 📞 技术支持

### 遇到问题时
1. **检查API密钥格式**：确保没有多余空格
2. **验证网络连接**：确保能访问币安API
3. **查看错误日志**：应用会记录详细错误信息
4. **测试网优先**：建议先在测试网环境调试

### 常见错误代码
- `-1021`: 时间戳错误（检查系统时间）
- `-1022`: 签名错误（检查Secret Key）
- `-2010`: 余额不足
- `-1003`: 请求频率过高

## 🎯 下一步

1. 根据需要选择测试网或主网API
2. 将API密钥配置到CryptoQuantBot
3. 启动应用测试连接
4. 确认数据获取正常后进行策略回测

---

**⚠️ 重要提醒**：请妥善保管您的API密钥，建议定期更换以确保账户安全。
