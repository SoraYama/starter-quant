# 代理配置说明

## 环境变量配置

### PROXY_URL 环境变量

设置 `CRYPTO_PROXY_URL` 环境变量来配置代理：

```bash
# HTTP代理
export CRYPTO_PROXY_URL=http://proxy.example.com:8080

# HTTPS代理
export CRYPTO_PROXY_URL=https://proxy.example.com:8080

# SOCKS5代理
export CRYPTO_PROXY_URL=socks5://proxy.example.com:1080

# SOCKS4代理
export CRYPTO_PROXY_URL=socks4://proxy.example.com:1080

# 带认证的代理
export CRYPTO_PROXY_URL=http://username:password@proxy.example.com:8080
export CRYPTO_PROXY_URL=socks5://username:password@proxy.example.com:1080
```

### 支持的代理类型

1. **HTTP代理**
   - 格式: `http://host:port`
   - 示例: `http://127.0.0.1:8080`

2. **HTTPS代理**
   - 格式: `https://host:port`
   - 示例: `https://127.0.0.1:8080`

3. **SOCKS5代理**
   - 格式: `socks5://host:port`
   - 示例: `socks5://127.0.0.1:1080`

4. **SOCKS4代理**
   - 格式: `socks4://host:port`
   - 示例: `socks4://127.0.0.1:1080`

### 认证支持

代理支持用户名和密码认证：

```bash
# HTTP代理认证
export CRYPTO_PROXY_URL=http://username:password@proxy.example.com:8080

# SOCKS5代理认证
export CRYPTO_PROXY_URL=socks5://username:password@proxy.example.com:1080
```

## 使用方法

### 1. 设置环境变量

```bash
# 临时设置
export CRYPTO_PROXY_URL=socks5://127.0.0.1:1080

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export CRYPTO_PROXY_URL=socks5://127.0.0.1:1080' >> ~/.bashrc
```

### 2. 启动应用

```bash
cd backend
source venv/bin/activate
python main.py
```

### 3. 验证代理

启动后查看日志，应该能看到类似信息：

```
INFO - Using proxy: socks5://127.0.0.1:1080
INFO - SOCKS proxy configured: socks5://127.0.0.1:1080
```

## 注意事项

1. **python-binance库限制**: 当使用API密钥模式时，python-binance库目前不支持代理，会显示警告信息
2. **公开数据模式**: 代理功能在公开数据模式下完全支持
3. **网络超时**: 使用代理时可能会增加网络延迟，建议适当调整超时设置
4. **代理稳定性**: 确保代理服务器稳定可靠，避免频繁断线

## 故障排除

### 代理连接失败

1. 检查代理URL格式是否正确
2. 确认代理服务器是否运行
3. 检查网络连接
4. 验证认证信息（如果使用）

### 性能问题

1. 选择地理位置较近的代理服务器
2. 使用高质量的代理服务
3. 考虑使用HTTP代理而不是SOCKS代理（通常更快）

## 示例配置

### 本地代理服务器

```bash
# 使用本地HTTP代理
export CRYPTO_PROXY_URL=http://127.0.0.1:8080

# 使用本地SOCKS5代理
export CRYPTO_PROXY_URL=socks5://127.0.0.1:1080
```

### 云代理服务

```bash
# 使用云代理服务
export CRYPTO_PROXY_URL=http://proxy-service.example.com:8080
export CRYPTO_PROXY_URL=socks5://proxy-service.example.com:1080
```
