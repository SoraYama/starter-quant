import React, { useState } from 'react';
import { 
  Row, Col, Card, Form, Input, InputNumber, DatePicker, Button, 
  Table, Tag, Statistic, Progress, Modal, Spin, Alert, Space 
} from 'antd';
import { 
  PlayCircleOutlined, HistoryOutlined, EyeOutlined, 
  DeleteOutlined, ThunderboltOutlined 
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { apiService } from '@/services/api';
import { BacktestResult, BacktestRequest } from '@/types';

const { RangePicker } = DatePicker;

const BacktestPage: React.FC = () => {
  const [form] = Form.useForm();
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedBacktest, setSelectedBacktest] = useState<BacktestResult | null>(null);
  const queryClient = useQueryClient();

  // 获取回测历史
  const { data: backtestHistory, isLoading } = useQuery({
    queryKey: ['backtest-history'],
    queryFn: () => apiService.backtest.getHistory({ limit: 20 }),
  });

  // 运行回测
  const runBacktestMutation = useMutation({
    mutationFn: (request: BacktestRequest) => apiService.backtest.run(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backtest-history'] });
      form.resetFields();
    },
  });

  // 快速回测
  const quickTestMutation = useMutation({
    mutationFn: (params: { symbol: string; days?: number; initial_balance?: number }) => 
      apiService.backtest.quickTest(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backtest-history'] });
    },
  });

  // 删除回测
  const deleteBacktestMutation = useMutation({
    mutationFn: (id: number) => apiService.backtest.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backtest-history'] });
    },
  });

  const handleSubmit = (values: any) => {
    const request: BacktestRequest = {
      symbol: values.symbol,
      start_date: values.dateRange[0].format('YYYY-MM-DD'),
      end_date: values.dateRange[1].format('YYYY-MM-DD'),
      initial_balance: values.initial_balance,
      timeframe: values.timeframe || '4h',
    };

    runBacktestMutation.mutate(request);
  };

  const handleQuickTest = (symbol: string) => {
    quickTestMutation.mutate({
      symbol,
      days: 30,
      initial_balance: 10000,
    });
  };

  const showBacktestDetail = (backtest: BacktestResult) => {
    setSelectedBacktest(backtest);
    setDetailModalVisible(true);
  };

  // 回测结果表格列
  const columns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
    },
    {
      title: '时间范围',
      key: 'period',
      render: (record: BacktestResult) => (
        <div style={{ fontSize: 12 }}>
          <div>{dayjs(record.start_date).format('MM-DD')}</div>
          <div>{dayjs(record.end_date).format('MM-DD')}</div>
        </div>
      ),
      width: 80,
    },
    {
      title: '总收益率',
      dataIndex: 'total_return',
      key: 'total_return',
      render: (value: number) => (
        <Tag color={value >= 0 ? 'green' : 'red'}>
          {value >= 0 ? '+' : ''}{(value * 100).toFixed(2)}%
        </Tag>
      ),
      width: 100,
    },
    {
      title: '最大回撤',
      dataIndex: 'max_drawdown',
      key: 'max_drawdown',
      render: (value: number) => (
        <span style={{ color: '#ff4d4f' }}>
          -{(value * 100).toFixed(2)}%
        </span>
      ),
      width: 100,
    },
    {
      title: '胜率',
      dataIndex: 'win_rate',
      key: 'win_rate',
      render: (value: number) => (
        <Progress 
          percent={Math.round(value * 100)} 
          size="small"
          status={value > 0.6 ? 'success' : value > 0.4 ? 'normal' : 'exception'}
        />
      ),
      width: 120,
    },
    {
      title: '交易次数',
      dataIndex: 'total_trades',
      key: 'total_trades',
      width: 80,
    },
    {
      title: '夏普比率',
      dataIndex: 'sharpe_ratio',
      key: 'sharpe_ratio',
      render: (value: number) => value ? value.toFixed(2) : '-',
      width: 80,
    },
    {
      title: '操作',
      key: 'actions',
      render: (record: BacktestResult) => (
        <Space>
          <Button 
            type="text" 
            icon={<EyeOutlined />} 
            size="small"
            onClick={() => showBacktestDetail(record)}
          >
            查看
          </Button>
          <Button 
            type="text" 
            danger
            icon={<DeleteOutlined />} 
            size="small"
            onClick={() => deleteBacktestMutation.mutate(record.backtest_id)}
            loading={deleteBacktestMutation.isPending}
          >
            删除
          </Button>
        </Space>
      ),
      width: 120,
    },
  ];

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={[16, 16]}>
        {/* 回测配置 */}
        <Col xs={24} lg={8}>
          <Card title="回测配置" className="dashboard-card">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              initialValues={{
                symbol: 'BTCUSDT',
                timeframe: '4h',
                initial_balance: 10000,
                dateRange: [dayjs().subtract(60, 'day'), dayjs().subtract(1, 'day')],
              }}
            >
              <Form.Item
                name="symbol"
                label="交易对"
                rules={[{ required: true, message: '请选择交易对' }]}
              >
                <Input placeholder="如: BTCUSDT" />
              </Form.Item>

              <Form.Item
                name="timeframe"
                label="时间周期"
              >
                <Input placeholder="如: 4h" />
              </Form.Item>

              <Form.Item
                name="dateRange"
                label="回测时间范围"
                rules={[{ required: true, message: '请选择时间范围' }]}
              >
                <RangePicker 
                  style={{ width: '100%' }}
                  format="YYYY-MM-DD"
                  disabledDate={(current) => current && current > dayjs().endOf('day')}
                />
              </Form.Item>

              <Form.Item
                name="initial_balance"
                label="初始资金 (USDT)"
                rules={[{ required: true, message: '请输入初始资金' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1000}
                  max={1000000}
                  placeholder="10000"
                />
              </Form.Item>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block
                  icon={<PlayCircleOutlined />}
                  loading={runBacktestMutation.isPending}
                >
                  开始回测
                </Button>
              </Form.Item>
            </Form>

            <div style={{ marginTop: 16 }}>
              <h4>快速回测</h4>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button 
                  block
                  icon={<ThunderboltOutlined />}
                  onClick={() => handleQuickTest('BTCUSDT')}
                  loading={quickTestMutation.isPending}
                >
                  BTC/USDT 30天回测
                </Button>
                <Button 
                  block
                  icon={<ThunderboltOutlined />}
                  onClick={() => handleQuickTest('ETHUSDT')}
                  loading={quickTestMutation.isPending}
                >
                  ETH/USDT 30天回测
                </Button>
              </Space>
            </div>
          </Card>
        </Col>

        {/* 回测统计 */}
        <Col xs={24} lg={16}>
          {backtestHistory?.data && backtestHistory.data.length > 0 ? (
            <Row gutter={[16, 16]}>
              {/* 最佳回测结果展示 */}
              {(() => {
                const bestResult = backtestHistory.data.reduce((best, current) => 
                  current.total_return > best.total_return ? current : best
                );
                return (
                  <Col xs={24}>
                    <Card title="最佳回测结果" className="dashboard-card">
                      <Row gutter={16}>
                        <Col xs={12} sm={6}>
                          <Statistic
                            title="交易对"
                            value={bestResult.symbol}
                            valueStyle={{ fontSize: 16 }}
                          />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic
                            title="总收益率"
                            value={(bestResult.total_return * 100).toFixed(2)}
                            suffix="%"
                            valueStyle={{ 
                              color: bestResult.total_return >= 0 ? '#52c41a' : '#ff4d4f',
                              fontSize: 16 
                            }}
                          />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic
                            title="胜率"
                            value={(bestResult.win_rate * 100).toFixed(1)}
                            suffix="%"
                            valueStyle={{ fontSize: 16 }}
                          />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic
                            title="交易次数"
                            value={bestResult.total_trades}
                            valueStyle={{ fontSize: 16 }}
                          />
                        </Col>
                      </Row>
                    </Card>
                  </Col>
                );
              })()}
            </Row>
          ) : null}
        </Col>
      </Row>

      {/* 回测历史 */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card 
            title="回测历史" 
            className="dashboard-card"
            extra={<HistoryOutlined />}
          >
            <Spin spinning={isLoading}>
              {backtestHistory?.data ? (
                <Table
                  columns={columns}
                  dataSource={backtestHistory.data}
                  rowKey="backtest_id"
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showTotal: (total) => `共 ${total} 条回测记录`,
                  }}
                  scroll={{ x: 800 }}
                />
              ) : (
                <div style={{ textAlign: 'center', padding: 40 }}>
                  暂无回测记录
                </div>
              )}
            </Spin>
          </Card>
        </Col>
      </Row>

      {/* 回测详情弹窗 */}
      <Modal
        title="回测详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={800}
        footer={null}
      >
        {selectedBacktest && (
          <div>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="交易对"
                  value={selectedBacktest.symbol}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="时间周期"
                  value={selectedBacktest.timeframe}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="初始资金"
                  value={selectedBacktest.initial_balance}
                  prefix="$"
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="最终资金"
                  value={selectedBacktest.final_balance}
                  prefix="$"
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="总收益率"
                  value={(selectedBacktest.total_return * 100).toFixed(2)}
                  suffix="%"
                  valueStyle={{ 
                    color: selectedBacktest.total_return >= 0 ? '#52c41a' : '#ff4d4f'
                  }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="最大回撤"
                  value={(selectedBacktest.max_drawdown * 100).toFixed(2)}
                  suffix="%"
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="总交易次数"
                  value={selectedBacktest.total_trades}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="盈利交易"
                  value={selectedBacktest.winning_trades}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="亏损交易"
                  value={selectedBacktest.losing_trades}
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Col>
              {selectedBacktest.sharpe_ratio && (
                <Col span={12}>
                  <Statistic
                    title="夏普比率"
                    value={selectedBacktest.sharpe_ratio.toFixed(3)}
                  />
                </Col>
              )}
              {selectedBacktest.profit_factor && (
                <Col span={12}>
                  <Statistic
                    title="盈亏比"
                    value={selectedBacktest.profit_factor.toFixed(2)}
                  />
                </Col>
              )}
            </Row>
            
            <div style={{ marginTop: 24 }}>
              <h4>时间范围</h4>
              <p>
                {dayjs(selectedBacktest.start_date).format('YYYY-MM-DD')} 至{' '}
                {dayjs(selectedBacktest.end_date).format('YYYY-MM-DD')}
              </p>
              <p style={{ fontSize: 12, color: '#666' }}>
                创建时间: {dayjs(selectedBacktest.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BacktestPage;
