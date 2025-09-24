import React, { useState } from 'react';
import { 
  Row, Col, Card, Button, InputNumber, Form, Select, Space, 
  Table, Tag, Statistic, Switch, Alert, Modal, notification 
} from 'antd';
import { 
  PlayCircleOutlined, PauseCircleOutlined, StopOutlined,
  DollarOutlined, LineChartOutlined, SettingOutlined 
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { TradeData, OrderRequest } from '@/types';

const { Option } = Select;

const TradingPage: React.FC = () => {
  const [form] = Form.useForm();
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
  const [tradingEnabled, setTradingEnabled] = useState(false);
  const [orderModalVisible, setOrderModalVisible] = useState(false);
  const queryClient = useQueryClient();

  // 获取账户信息
  const { data: accountData } = useQuery({
    queryKey: ['account-info'],
    queryFn: () => apiService.trading.getAccount(),
    refetchInterval: 10000, // 10秒刷新
  });

  // 获取持仓信息
  const { data: positionsData } = useQuery({
    queryKey: ['positions'],
    queryFn: () => apiService.trading.getPositions(),
    refetchInterval: 5000, // 5秒刷新
  });

  // 获取交易历史
  const { data: tradesData, isLoading: tradesLoading } = useQuery({
    queryKey: ['trades-history', selectedSymbol],
    queryFn: () => apiService.trading.getOrders({ 
      symbol: selectedSymbol,
      limit: 50 
    }),
  });

  // 获取当前订单
  const { data: ordersData } = useQuery({
    queryKey: ['open-orders'],
    queryFn: () => apiService.trading.getOrders(),
    refetchInterval: 3000, // 3秒刷新
  });

  // 下单
  const orderMutation = useMutation({
    mutationFn: (request: OrderRequest) => apiService.trading.placeOrder(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['open-orders'] });
      queryClient.invalidateQueries({ queryKey: ['positions'] });
      queryClient.invalidateQueries({ queryKey: ['account-info'] });
      setOrderModalVisible(false);
      form.resetFields();
      notification.success({
        message: '订单提交成功',
        description: '订单已成功提交到交易所',
      });
    },
    onError: (error) => {
      notification.error({
        message: '订单提交失败',
        description: error.message,
      });
    },
  });

  // 取消订单
  const cancelOrderMutation = useMutation({
    mutationFn: (orderId: string) => apiService.trading.cancelOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['open-orders'] });
      notification.success({
        message: '订单已取消',
      });
    },
  });

  const handleCreateOrder = (values: any) => {
    const request: OrderRequest = {
      symbol: selectedSymbol,
      side: values.side,
      type: values.type || 'MARKET',
      quantity: values.quantity,
      price: values.price,
    };

    orderMutation.mutate(request);
  };

  // 订单表格列
  const orderColumns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: number) => new Date(timestamp * 1000).toLocaleString(),
      width: 140,
    },
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
    },
    {
      title: '类型',
      dataIndex: 'side',
      key: 'side',
      render: (side: string) => (
        <Tag color={side === 'BUY' ? 'green' : 'red'}>
          {side === 'BUY' ? '买入' : '卖出'}
        </Tag>
      ),
      width: 80,
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (qty: number) => qty.toFixed(8),
      width: 120,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `$${price.toFixed(2)}`,
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          'NEW': 'blue',
          'PARTIALLY_FILLED': 'orange',
          'FILLED': 'green',
          'CANCELED': 'red',
          'REJECTED': 'red',
        };
        return <Tag color={colorMap[status] || 'default'}>{status}</Tag>;
      },
      width: 100,
    },
    {
      title: '操作',
      key: 'actions',
      render: (record: any) => (
        record.status === 'NEW' || record.status === 'PARTIALLY_FILLED' ? (
          <Button
            type="text"
            danger
            size="small"
            onClick={() => cancelOrderMutation.mutate(record.order_id)}
            loading={cancelOrderMutation.isPending}
          >
            取消
          </Button>
        ) : null
      ),
      width: 80,
    },
  ];

  // 交易历史表格列
  const tradeColumns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: number) => new Date(timestamp * 1000).toLocaleString(),
      width: 140,
    },
    {
      title: '类型',
      dataIndex: 'side',
      key: 'side',
      render: (side: string) => (
        <Tag color={side === 'BUY' ? 'green' : 'red'}>
          {side === 'BUY' ? '买入' : '卖出'}
        </Tag>
      ),
      width: 80,
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (qty: number) => qty.toFixed(8),
      width: 120,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `$${price.toFixed(2)}`,
      width: 100,
    },
    {
      title: '手续费',
      dataIndex: 'commission',
      key: 'commission',
      render: (commission: number) => commission ? `$${commission.toFixed(4)}` : '-',
      width: 100,
    },
    {
      title: '总额',
      key: 'total',
      render: (record: TradeData) => `$${(record.quantity * record.price).toFixed(2)}`,
      width: 120,
    },
  ];

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
            
            <Switch
              checkedChildren="交易开启"
              unCheckedChildren="交易关闭"
              checked={tradingEnabled}
              onChange={setTradingEnabled}
            />
          </Space>
        </div>
        
        <div className="toolbar-right">
          <Space>
            <Button
              type="primary"
              icon={<DollarOutlined />}
              onClick={() => setOrderModalVisible(true)}
              disabled={!tradingEnabled}
            >
              下单
            </Button>
            <Button icon={<SettingOutlined />}>
              交易设置
            </Button>
          </Space>
        </div>
      </div>

      {/* API模式提示 */}
      <Alert
        message="当前使用公开数据模式"
        description="若要启用真实交易功能，请在配置中设置币安API密钥并切换到完整功能模式。当前为演示模式，所有交易都是模拟的。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        action={
          <Button size="small" type="link">
            查看配置指南
          </Button>
        }
      />

      <Row gutter={[16, 16]}>
        {/* 账户信息 */}
        <Col xs={24} lg={8}>
          <Card title="账户信息" className="dashboard-card">
            {accountData?.data ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Statistic
                      title="可用余额"
                      value={accountData.data.available_balance || 10000}
                      prefix="$"
                      precision={2}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="总资产"
                      value={accountData.data.total_balance || 10000}
                      prefix="$"
                      precision={2}
                    />
                  </Col>
                </Row>
                
                <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                  <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>
                    账户状态: 
                    <Tag color="green" style={{ marginLeft: 8 }}>
                      {accountData.data.account_type || '演示账户'}
                    </Tag>
                  </div>
                  <div style={{ fontSize: 12, color: '#666' }}>
                    权限: {accountData.data.permissions?.join(', ') || 'SPOT'}
                  </div>
                </div>
              </Space>
            ) : (
              <div style={{ textAlign: 'center', padding: 40 }}>
                暂无账户数据
              </div>
            )}
          </Card>
        </Col>

        {/* 持仓信息 */}
        <Col xs={24} lg={16}>
          <Card title="当前持仓" className="dashboard-card">
            {positionsData?.data && positionsData.data.length > 0 ? (
              <Row gutter={16}>
                {positionsData.data.map((position: any, index: number) => (
                  <Col xs={24} sm={12} md={8} key={index}>
                    <div style={{ 
                      padding: 16, 
                      border: '1px solid #d9d9d9', 
                      borderRadius: 4,
                      marginBottom: 16 
                    }}>
                      <div style={{ fontWeight: 'bold', marginBottom: 8 }}>
                        {position.symbol}
                      </div>
                      <div style={{ fontSize: 12, color: '#666' }}>
                        数量: {position.quantity}
                      </div>
                      <div style={{ fontSize: 12, color: '#666' }}>
                        均价: ${position.avg_price.toFixed(2)}
                      </div>
                      <div style={{ 
                        fontSize: 12, 
                        color: position.pnl >= 0 ? '#52c41a' : '#ff4d4f' 
                      }}>
                        盈亏: {position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)}
                      </div>
                    </div>
                  </Col>
                ))}
              </Row>
            ) : (
              <div style={{ textAlign: 'center', padding: 40 }}>
                暂无持仓
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 当前订单 */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card 
            title="当前订单" 
            className="dashboard-card"
            extra={<LineChartOutlined />}
          >
            <Table
              columns={orderColumns}
              dataSource={ordersData?.data || []}
              rowKey="order_id"
              pagination={false}
              scroll={{ x: 800 }}
              locale={{ emptyText: '暂无订单' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 交易历史 */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="交易历史" className="dashboard-card">
            <Table
              columns={tradeColumns}
              dataSource={tradesData?.data || []}
              rowKey="trade_id"
              loading={tradesLoading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 笔交易`,
              }}
              scroll={{ x: 800 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 下单弹窗 */}
      <Modal
        title="创建订单"
        open={orderModalVisible}
        onCancel={() => setOrderModalVisible(false)}
        footer={null}
        width={400}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateOrder}
          initialValues={{
            symbol: selectedSymbol,
            side: 'BUY',
            type: 'MARKET',
          }}
        >
          <Form.Item
            name="side"
            label="交易方向"
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="BUY">买入</Option>
              <Option value="SELL">卖出</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="type"
            label="订单类型"
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="MARKET">市价单</Option>
              <Option value="LIMIT">限价单</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="quantity"
            label="数量"
            rules={[
              { required: true, message: '请输入数量' },
              { type: 'number', min: 0.001, message: '数量必须大于0.001' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="输入数量"
              precision={8}
              min={0.001}
            />
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => 
              prevValues.type !== currentValues.type
            }
          >
            {({ getFieldValue }) =>
              getFieldValue('type') === 'LIMIT' ? (
                <Form.Item
                  name="price"
                  label="价格"
                  rules={[
                    { required: true, message: '请输入价格' },
                    { type: 'number', min: 0.01, message: '价格必须大于0.01' }
                  ]}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="输入价格"
                    precision={2}
                    min={0.01}
                    prefix="$"
                  />
                </Form.Item>
              ) : null
            }
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setOrderModalVisible(false)}>
                取消
              </Button>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={orderMutation.isPending}
              >
                提交订单
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TradingPage;
