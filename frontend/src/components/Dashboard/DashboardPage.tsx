import React from 'react';
import { Row, Col, Card, Statistic, Progress, Space, Tag } from 'antd';
import { 
  RiseOutlined, FallOutlined, LineChartOutlined, 
  WalletOutlined, ThunderboltOutlined, SignalFilled 
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import MarketOverview from '@/components/Market/MarketOverview';
import PriceAlert from '@/components/Market/PriceAlert';
import TradingViewChart from '@/components/Charts/TradingViewChart';

const DashboardPage: React.FC = () => {
  // 获取仪表板数据
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: () => apiService.market.getOverview(),
    refetchInterval: 60000, // 1分钟刷新
  });

  // 获取最新价格数据
  const { data: priceData } = useQuery({
    queryKey: ['latest-prices'],
    queryFn: () => Promise.all([
      apiService.market.getPrice('BTCUSDT'),
      apiService.market.getPrice('ETHUSDT'),
    ]),
    refetchInterval: 10000, // 10秒刷新
  });

  // 获取最新信号
  const { data: signalData } = useQuery({
    queryKey: ['latest-signals'],
    queryFn: () => apiService.strategy.analyze({
      symbol: 'BTCUSDT',
      timeframe: '4h',
    }),
    refetchInterval: 300000, // 5分钟刷新
  });

  // 获取K线数据用于图表
  const { data: klineData } = useQuery({
    queryKey: ['dashboard-kline', 'BTCUSDT'],
    queryFn: () => apiService.market.getKlines({
      symbol: 'BTCUSDT',
      interval: '4h',
      limit: 100,
    }),
    refetchInterval: 300000, // 5分钟刷新
  });

  const btcPrice = parseFloat(priceData?.[0]?.data?.price || '0');
  const ethPrice = parseFloat(priceData?.[1]?.data?.price || '0');
  const btcChange = parseFloat(priceData?.[0]?.data?.price_change_percent || '0');
  const ethChange = parseFloat(priceData?.[1]?.data?.price_change_percent || '0');

  // 最新信号信息
  const latestSignal = signalData?.data?.signals?.[0];
  const signalStrength = signalData?.data?.signal_strength || 0;

  return (
    <div style={{ padding: 16 }}>
      {/* 价格概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={6}>
          <Card className="dashboard-card">
            <Statistic
              title="BTC/USDT"
              value={btcPrice}
              precision={2}
              prefix="$"
              valueStyle={{ 
                color: btcChange >= 0 ? '#52c41a' : '#ff4d4f',
                fontSize: 18 
              }}
              suffix={
                <Tag 
                  color={btcChange >= 0 ? 'green' : 'red'}
                  icon={btcChange >= 0 ? <RiseOutlined /> : <FallOutlined />}
                >
                  {btcChange >= 0 ? '+' : ''}{btcChange.toFixed(2)}%
                </Tag>
              }
            />
          </Card>
        </Col>
        
        <Col xs={12} sm={6}>
          <Card className="dashboard-card">
            <Statistic
              title="ETH/USDT"
              value={ethPrice}
              precision={2}
              prefix="$"
              valueStyle={{ 
                color: ethChange >= 0 ? '#52c41a' : '#ff4d4f',
                fontSize: 18 
              }}
              suffix={
                <Tag 
                  color={ethChange >= 0 ? 'green' : 'red'}
                  icon={ethChange >= 0 ? <RiseOutlined /> : <FallOutlined />}
                >
                  {ethChange >= 0 ? '+' : ''}{ethChange.toFixed(2)}%
                </Tag>
              }
            />
          </Card>
        </Col>

        <Col xs={12} sm={6}>
          <Card className="dashboard-card">
            <Statistic
              title="账户余额"
              value={10000}
              precision={2}
              prefix="$"
              valueStyle={{ fontSize: 18 }}
              suffix={
                <Tag color="blue" icon={<WalletOutlined />}>
                  演示模式
                </Tag>
              }
            />
          </Card>
        </Col>

        <Col xs={12} sm={6}>
          <Card className="dashboard-card">
            <Statistic
              title="信号强度"
              value={Math.round(signalStrength * 100)}
              suffix="%"
              valueStyle={{ fontSize: 18 }}
              prefix={
                <ThunderboltOutlined 
                  style={{ 
                    color: signalStrength > 0.7 ? '#52c41a' : 
                           signalStrength > 0.4 ? '#faad14' : '#ff4d4f' 
                  }} 
                />
              }
            />
            <Progress 
              percent={Math.round(signalStrength * 100)} 
              size="small" 
              status={signalStrength > 0.7 ? 'success' : signalStrength > 0.4 ? 'normal' : 'exception'}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 左侧 - 图表和市场信息 */}
        <Col xs={24} lg={16}>
          <Space direction="vertical" style={{ width: '100%' }} size={16}>
            {/* K线图表 */}
            <Card 
              title="BTC/USDT - 4小时K线" 
              className="dashboard-card"
              extra={<LineChartOutlined />}
            >
              {klineData?.data ? (
                <TradingViewChart
                  data={klineData.data}
                  symbol="BTCUSDT"
                  interval="4h"
                  height={400}
                  showVolume={true}
                />
              ) : (
                <div style={{ 
                  height: 400, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  background: '#f5f5f5',
                  borderRadius: 4 
                }}>
                  <div style={{ textAlign: 'center', color: '#666' }}>
                    <LineChartOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                    <div>图表数据加载中...</div>
                  </div>
                </div>
              )}
            </Card>

            {/* 市场概览 */}
            <MarketOverview />
          </Space>
        </Col>

        {/* 右侧 - 信号和提醒 */}
        <Col xs={24} lg={8}>
          <Space direction="vertical" style={{ width: '100%' }} size={16}>
            {/* 最新交易信号 */}
            <Card 
              title="最新交易信号" 
              className="dashboard-card"
              extra={<SignalFilled />}
            >
              {latestSignal ? (
                <div>
                  <div style={{ marginBottom: 16 }}>
                    <Tag 
                      color={latestSignal.signal_type === 'BUY' ? 'green' : 'red'}
                      style={{ fontSize: 14, padding: '4px 12px' }}
                    >
                      {latestSignal.signal_type === 'BUY' ? '买入信号' : '卖出信号'}
                    </Tag>
                  </div>
                  
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <span style={{ color: '#666' }}>价格: </span>
                      <strong>${parseFloat(latestSignal.price || '0').toFixed(2)}</strong>
                    </div>
                    <div>
                      <span style={{ color: '#666' }}>置信度: </span>
                      <Progress 
                        percent={Math.round(latestSignal.confidence * 100)} 
                        size="small"
                        status={latestSignal.confidence > 0.7 ? 'success' : 'normal'}
                      />
                    </div>
                    <div>
                      <span style={{ color: '#666' }}>策略: </span>
                      <Tag>{latestSignal.strategy_name}</Tag>
                    </div>
                    <div>
                      <span style={{ color: '#666' }}>时间: </span>
                      <span style={{ fontSize: 12 }}>
                        {new Date(latestSignal.timestamp * 1000).toLocaleString()}
                      </span>
                    </div>
                    {latestSignal.reason && (
                      <div>
                        <span style={{ color: '#666' }}>原因: </span>
                        <div style={{ 
                          fontSize: 12, 
                          color: '#999', 
                          marginTop: 4,
                          padding: 8,
                          background: '#f5f5f5',
                          borderRadius: 4 
                        }}>
                          {latestSignal.reason}
                        </div>
                      </div>
                    )}
                  </Space>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: 40, color: '#666' }}>
                  <SignalFilled style={{ fontSize: 32, marginBottom: 16 }} />
                  <div>暂无最新信号</div>
                </div>
              )}
            </Card>

            {/* 价格提醒 */}
            <PriceAlert 
              symbol="BTCUSDT" 
              currentPrice={btcPrice}
            />

            {/* 快速操作 */}
            <Card title="快速操作" className="dashboard-card">
              <Space direction="vertical" style={{ width: '100%' }}>
                <a href="/market" style={{ display: 'block', padding: '8px 0' }}>
                  📊 查看完整市场数据
                </a>
                <a href="/strategy" style={{ display: 'block', padding: '8px 0' }}>
                  🎯 策略分析工具
                </a>
                <a href="/backtest" style={{ display: 'block', padding: '8px 0' }}>
                  📈 启动新的回测
                </a>
                <a href="/trading" style={{ display: 'block', padding: '8px 0' }}>
                  💰 模拟交易操作
                </a>
                <a href="/settings" style={{ display: 'block', padding: '8px 0' }}>
                  ⚙️ 系统设置配置
                </a>
              </Space>
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
