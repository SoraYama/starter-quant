import React from 'react';
import { Card, Statistic, Row, Col, Spin, Alert } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '@/services/api';

const MarketOverview: React.FC = () => {
  const { data: overview, isLoading, error } = useQuery({
    queryKey: ['market-overview'],
    queryFn: () => apiService.market.getOverview(),
    refetchInterval: 60000, // 每分钟刷新
  });

  if (error) {
    return (
      <Card title="市场概览" className="dashboard-card">
        <Alert
          message="数据加载失败"
          description={error.message}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  return (
    <Card title="市场概览" className="dashboard-card">
      <Spin spinning={isLoading}>
        {overview ? (
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Statistic
                title="支持交易对"
                value={overview.total_symbols}
                suffix="个"
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="活跃交易对"
                value={overview.active_symbols}
                suffix="个"
              />
            </Col>
            <Col span={24}>
              <Statistic
                title="API模式"
                value={overview.api_mode === 'PUBLIC_MODE' ? '公开数据模式' : '完整功能模式'}
                valueStyle={{ 
                  color: overview.api_mode === 'PUBLIC_MODE' ? '#faad14' : '#52c41a',
                  fontSize: 14
                }}
              />
            </Col>
            <Col span={24}>
              <div style={{ marginTop: 16 }}>
                <h4 style={{ marginBottom: 8, fontSize: 14, color: '#666' }}>
                  支持的交易对:
                </h4>
                <div style={{ fontSize: 12, color: '#999' }}>
                  {overview.supported_symbols?.join(', ') || 'BTC/USDT, ETH/USDT'}
                </div>
              </div>
            </Col>
            {overview.last_update && (
              <Col span={24}>
                <div style={{ fontSize: 12, color: '#999', marginTop: 8 }}>
                  最后更新: {new Date(overview.last_update).toLocaleString()}
                </div>
              </Col>
            )}
          </Row>
        ) : (
          <div style={{ textAlign: 'center', padding: 40 }}>
            暂无数据
          </div>
        )}
      </Spin>
    </Card>
  );
};

export default MarketOverview;
