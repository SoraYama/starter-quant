import React, { useState } from 'react';
import { Row, Col, Card, Button, Select, Space, Table, Tag, Spin, Alert, Progress } from 'antd';
import { PlayCircleOutlined, ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { SignalData, StrategyConfig } from '@/types';

const { Option } = Select;

const StrategyPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
  const [selectedTimeframe, setSelectedTimeframe] = useState('4h');
  const queryClient = useQueryClient();

  // 获取策略分析结果
  const { data: analysisData, isLoading, error } = useQuery({
    queryKey: ['strategy-analysis', selectedSymbol, selectedTimeframe],
    queryFn: () => apiService.strategy.analyze({
      symbol: selectedSymbol,
      timeframe: selectedTimeframe,
    }),
    refetchInterval: 60000, // 1分钟刷新
  });

  // 获取信号强度
  const { data: strengthData } = useQuery({
    queryKey: ['signal-strength', selectedSymbol, selectedTimeframe],
    queryFn: () => apiService.strategy.evaluateStrength({
      symbol: selectedSymbol,
      timeframe: selectedTimeframe,
    }),
    refetchInterval: 30000, // 30秒刷新
  });

  // 重新分析
  const analysisMutation = useMutation({
    mutationFn: () => apiService.strategy.analyze({
      symbol: selectedSymbol,
      timeframe: selectedTimeframe,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategy-analysis'] });
      queryClient.invalidateQueries({ queryKey: ['signal-strength'] });
    },
  });

  const handleAnalyze = () => {
    analysisMutation.mutate();
  };

  // 信号表格列定义
  const signalColumns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: number) => new Date(timestamp * 1000).toLocaleString(),
      width: 180,
    },
    {
      title: '信号类型',
      dataIndex: 'signal_type',
      key: 'signal_type',
      render: (type: string) => (
        <Tag color={type === 'BUY' ? 'green' : 'red'}>
          {type === 'BUY' ? '买入' : '卖出'}
        </Tag>
      ),
      width: 100,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `$${price.toFixed(2)}`,
      width: 120,
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence: number) => (
        <Progress 
          percent={Math.round(confidence * 100)} 
          size="small" 
          status={confidence > 0.7 ? 'success' : confidence > 0.4 ? 'normal' : 'exception'}
        />
      ),
      width: 120,
    },
    {
      title: '策略',
      dataIndex: 'strategy_name',
      key: 'strategy_name',
      width: 150,
    },
    {
      title: '原因',
      dataIndex: 'reason',
      key: 'reason',
      ellipsis: true,
    },
  ];

  // 技术指标显示组件
  const TechnicalIndicatorCard: React.FC<{ title: string; data: any }> = ({ title, data }) => {
    if (!data) return null;

    return (
      <Card size="small" title={title}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {Object.entries(data).map(([key, value]: [string, any]) => (
            <div key={key} style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#666' }}>{key}:</span>
              <strong>{typeof value === 'number' ? value.toFixed(4) : value}</strong>
            </div>
          ))}
        </Space>
      </Card>
    );
  };

  if (error) {
    return (
      <Alert
        message="数据加载失败"
        description={error.message}
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
              onChange={setSelectedSymbol}
              style={{ width: 120 }}
            >
              <Option value="BTCUSDT">BTC/USDT</Option>
              <Option value="ETHUSDT">ETH/USDT</Option>
            </Select>
            
            <Select
              value={selectedTimeframe}
              onChange={setSelectedTimeframe}
              style={{ width: 100 }}
            >
              <Option value="1h">1小时</Option>
              <Option value="4h">4小时</Option>
              <Option value="1d">1天</Option>
            </Select>
          </Space>
        </div>
        
        <div className="toolbar-right">
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleAnalyze}
              loading={analysisMutation.isPending}
            >
              重新分析
            </Button>
            <Button icon={<SettingOutlined />}>
              策略配置
            </Button>
          </Space>
        </div>
      </div>

      <Row gutter={[16, 16]}>
        {/* 信号强度 */}
        <Col xs={24} lg={8}>
          <Card title="信号强度分析" className="dashboard-card">
            {strengthData?.data ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 8 }}>
                    {strengthData.data.strength}
                  </div>
                  <Progress 
                    percent={Math.round(strengthData.data.confidence * 100)}
                    strokeColor={{
                      '0%': '#ff4d4f',
                      '50%': '#faad14', 
                      '100%': '#52c41a',
                    }}
                  />
                </div>
                
                <Row gutter={16} style={{ marginTop: 16 }}>
                  <Col span={12}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 18, fontWeight: 'bold', color: '#52c41a' }}>
                        {strengthData.data.buy_signals}
                      </div>
                      <div style={{ color: '#666', fontSize: 12 }}>买入信号</div>
                    </div>
                  </Col>
                  <Col span={12}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 18, fontWeight: 'bold', color: '#ff4d4f' }}>
                        {strengthData.data.sell_signals}
                      </div>
                      <div style={{ color: '#666', fontSize: 12 }}>卖出信号</div>
                    </div>
                  </Col>
                </Row>

                {strengthData.data.latest_signal && (
                  <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                    <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>最新信号:</div>
                    <Tag color={strengthData.data.latest_signal.signal_type === 'BUY' ? 'green' : 'red'}>
                      {strengthData.data.latest_signal.signal_type === 'BUY' ? '买入' : '卖出'}
                    </Tag>
                    <span style={{ marginLeft: 8 }}>
                      ${parseFloat(strengthData.data.latest_signal.price || '0').toFixed(2)}
                    </span>
                  </div>
                )}
              </Space>
            ) : (
              <Spin spinning={isLoading}>
                <div style={{ textAlign: 'center', padding: 40 }}>
                  暂无信号数据
                </div>
              </Spin>
            )}
          </Card>
        </Col>

        {/* 技术指标 */}
        <Col xs={24} lg={16}>
          <Row gutter={[16, 16]}>
            <Col xs={24} md={8}>
              <TechnicalIndicatorCard 
                title="MACD指标" 
                data={analysisData?.data?.indicators?.[0]?.macd ? {
                  'MACD': analysisData.data.indicators[0].macd,
                  'Signal': analysisData.data.indicators[0].macd_signal,
                  'Histogram': analysisData.data.indicators[0].macd_histogram,
                } : null}
              />
            </Col>
            <Col xs={24} md={8}>
              <TechnicalIndicatorCard 
                title="RSI指标" 
                data={analysisData?.data?.indicators?.[0]?.rsi ? {
                  'RSI': analysisData.data.indicators[0].rsi,
                  '状态': analysisData.data.indicators[0].rsi > 70 ? '超买' : 
                         analysisData.data.indicators[0].rsi < 30 ? '超卖' : '正常',
                } : null}
              />
            </Col>
            <Col xs={24} md={8}>
              <TechnicalIndicatorCard 
                title="布林带" 
                data={analysisData?.data?.indicators?.[0]?.bb_upper ? {
                  'Upper': analysisData.data.indicators[0].bb_upper,
                  'Middle': analysisData.data.indicators[0].bb_middle,
                  'Lower': analysisData.data.indicators[0].bb_lower,
                  'Width': analysisData.data.indicators[0].bb_width,
                } : null}
              />
            </Col>
          </Row>
        </Col>
      </Row>

      {/* 交易信号历史 */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card 
            title="交易信号历史" 
            className="dashboard-card"
            extra={
              <Space>
                <Button 
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={handleAnalyze}
                  loading={analysisMutation.isPending}
                >
                  开始分析
                </Button>
              </Space>
            }
          >
            <Spin spinning={isLoading || analysisMutation.isPending}>
              <Table
                columns={signalColumns}
                dataSource={analysisData?.data?.signals || []}
                rowKey="timestamp"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 条信号`,
                }}
                scroll={{ x: 800 }}
              />
            </Spin>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default StrategyPage;
