import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Select, Space, Statistic, Tag, Spin, Alert } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';

import TradingViewChart from '@/components/Charts/TradingViewChart';
import MarketOverview from '@/components/Market/MarketOverview';
import PriceAlert from '@/components/Market/PriceAlert';
import { apiService } from '@/services/api';
import { websocketService } from '@/services/websocket';
import { KLineData, TickerData } from '@/types';

const { Option } = Select;

const MarketPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
  const [selectedInterval, setSelectedInterval] = useState('4h');
  const [realtimePrice, setRealtimePrice] = useState<TickerData | null>(null);

  // 获取K线数据
  const { data: klineData, isLoading: klineLoading, error: klineError } = useQuery({
    queryKey: ['klines', selectedSymbol, selectedInterval],
    queryFn: () => apiService.market.getKlines({
      symbol: selectedSymbol,
      interval: selectedInterval,
      limit: 500,
    }),
    refetchInterval: 30000, // 30秒刷新一次
  });

  // 获取实时价格
  const { data: tickerData, isLoading: tickerLoading } = useQuery({
    queryKey: ['ticker', selectedSymbol],
    queryFn: () => apiService.market.getTicker(selectedSymbol),
    refetchInterval: 5000, // 5秒刷新一次
  });

  // WebSocket实时价格订阅
  useEffect(() => {
    const handlePriceUpdate = (data: TickerData) => {
      setRealtimePrice(data);
    };

    // 订阅当前选中的交易对
    websocketService.subscribe(selectedSymbol);
    websocketService.on(`price_${selectedSymbol}`, handlePriceUpdate);

    return () => {
      websocketService.unsubscribe(selectedSymbol);
      websocketService.off(`price_${selectedSymbol}`, handlePriceUpdate);
    };
  }, [selectedSymbol]);

  // 选择交易对
  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbol(symbol);
    setRealtimePrice(null);
  };

  // 选择时间间隔
  const handleIntervalChange = (interval: string) => {
    setSelectedInterval(interval);
  };

  // 获取当前价格数据（优先使用实时数据）
  const currentPrice = realtimePrice || tickerData?.data;
  
  // 格式化价格变化
  const formatPriceChange = (change: number | string, changePercent: number | string) => {
    const numChange = typeof change === 'string' ? parseFloat(change) : change;
    const numChangePercent = typeof changePercent === 'string' ? parseFloat(changePercent) : changePercent;
    const isPositive = numChange >= 0;
    return {
      icon: isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />,
      color: isPositive ? '#52c41a' : '#ff4d4f',
      text: `${isPositive ? '+' : ''}${numChange.toFixed(2)} (${isPositive ? '+' : ''}${numChangePercent.toFixed(2)}%)`,
    };
  };

  if (klineError) {
    return (
      <Alert
        message="数据加载失败"
        description={klineError.message}
        type="error"
        showIcon
        style={{ margin: 16 }}
      />
    );
  }

  return (
    <div style={{ padding: 16 }}>
      {/* 工具栏 */}
      <div className="toolbar">
        <div className="toolbar-left">
          <Space>
            <Select
              value={selectedSymbol}
              onChange={handleSymbolChange}
              style={{ width: 120 }}
            >
              <Option value="BTCUSDT">BTC/USDT</Option>
              <Option value="ETHUSDT">ETH/USDT</Option>
            </Select>
            
            <Select
              value={selectedInterval}
              onChange={handleIntervalChange}
              style={{ width: 100 }}
            >
              <Option value="1h">1小时</Option>
              <Option value="4h">4小时</Option>
              <Option value="1d">1天</Option>
            </Select>
          </Space>
        </div>
        
        <div className="toolbar-right">
          {websocketService.isConnected() ? (
            <Tag color="green">实时连接</Tag>
          ) : (
            <Tag color="red">离线模式</Tag>
          )}
        </div>
      </div>

      <Row gutter={[16, 16]}>
        {/* 价格统计 */}
        <Col xs={24} lg={8}>
          <Card title="价格统计" className="dashboard-card">
            <Spin spinning={tickerLoading && !currentPrice}>
              {currentPrice ? (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Statistic
                    title="当前价格"
                    value={parseFloat(currentPrice.price || '0')}
                    precision={2}
                    prefix="$"
                    valueStyle={{ fontSize: 24 }}
                  />
                  
                  {currentPrice.price_change !== undefined && (
                    <div>
                      {(() => {
                        const formatted = formatPriceChange(
                          currentPrice.price_change,
                          currentPrice.price_change_percent
                        );
                        return (
                          <Statistic
                            title="24小时变化"
                            value={formatted.text}
                            valueStyle={{ color: formatted.color, fontSize: 16 }}
                            prefix={formatted.icon}
                          />
                        );
                      })()}
                    </div>
                  )}
                  
                  <Row gutter={16}>
                    <Col span={12}>
                      <Statistic
                        title="24小时最高"
                        value={parseFloat(currentPrice.high_price || '0')}
                        precision={2}
                        prefix="$"
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="24小时最低"
                        value={parseFloat(currentPrice.low_price || '0')}
                        precision={2}
                        prefix="$"
                      />
                    </Col>
                  </Row>
                  
                  <Statistic
                    title="24小时成交量"
                    value={parseFloat(currentPrice.volume || '0')}
                    precision={2}
                    suffix={selectedSymbol.replace('USDT', '')}
                  />
                </Space>
              ) : (
                <div style={{ textAlign: 'center', padding: 40 }}>
                  暂无数据
                </div>
              )}
            </Spin>
          </Card>
        </Col>

        {/* 市场概览 */}
        <Col xs={24} lg={8}>
          <MarketOverview />
        </Col>

        {/* 价格提醒 */}
        <Col xs={24} lg={8}>
          <PriceAlert symbol={selectedSymbol} currentPrice={currentPrice?.price} />
        </Col>
      </Row>

      {/* K线图表 */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title={`${selectedSymbol} K线图表`} className="dashboard-card">
            <Spin spinning={klineLoading}>
              {klineData?.data ? (
                <TradingViewChart
                  data={klineData.data}
                  symbol={selectedSymbol}
                  interval={selectedInterval}
                  height={500}
                />
              ) : (
                <div style={{ textAlign: 'center', padding: 100 }}>
                  {klineLoading ? '加载中...' : '暂无图表数据'}
                </div>
              )}
            </Spin>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default MarketPage;
