import React, { useState } from 'react';
import { Card, Form, InputNumber, Button, List, Tag, Space, App } from 'antd';
import { PlusOutlined, DeleteOutlined, BellOutlined } from '@ant-design/icons';

interface PriceAlertProps {
  symbol: string;
  currentPrice?: number;
}

interface Alert {
  id: string;
  price: number;
  type: 'above' | 'below';
  created: Date;
}

const PriceAlert: React.FC<PriceAlertProps> = ({ symbol, currentPrice }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [form] = Form.useForm();
  const { notification } = App.useApp();

  const addAlert = (values: { price: number; type: 'above' | 'below' }) => {
    const newAlert: Alert = {
      id: Date.now().toString(),
      price: values.price,
      type: values.type,
      created: new Date(),
    };

    setAlerts(prev => [...prev, newAlert]);
    form.resetFields();

    notification.success({
      message: '价格提醒已设置',
      description: `当${symbol}价格${values.type === 'above' ? '超过' : '低于'} $${values.price} 时将通知您`,
    });
  };

  const removeAlert = (id: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
    notification.info({
      message: '价格提醒已删除',
    });
  };

  // 检查是否触发提醒
  React.useEffect(() => {
    if (!currentPrice) return;

    alerts.forEach(alert => {
      const shouldTrigger = 
        (alert.type === 'above' && currentPrice >= alert.price) ||
        (alert.type === 'below' && currentPrice <= alert.price);

      if (shouldTrigger) {
        notification.warning({
          message: `${symbol} 价格提醒`,
          description: `当前价格 $${currentPrice} ${alert.type === 'above' ? '已超过' : '已低于'} 设定价格 $${alert.price}`,
          icon: <BellOutlined style={{ color: '#faad14' }} />,
          duration: 0, // 不自动关闭
        });

        // 触发后移除提醒
        removeAlert(alert.id);
      }
    });
  }, [currentPrice, alerts, symbol]);

  return (
    <Card 
      title={`${symbol} 价格提醒`} 
      className="dashboard-card"
      extra={<BellOutlined />}
    >
      <Form form={form} onFinish={addAlert} layout="vertical">
        <Form.Item
          name="price"
          label="提醒价格"
          rules={[
            { required: true, message: '请输入提醒价格' },
            { type: 'number', min: 0.01, message: '价格必须大于0.01' }
          ]}
        >
          <InputNumber
            style={{ width: '100%' }}
            placeholder="输入价格"
            precision={2}
            prefix="$"
            min={0.01}
          />
        </Form.Item>

        <Form.Item
          name="type"
          label="提醒类型"
          initialValue="above"
          rules={[{ required: true }]}
        >
          <Space.Compact style={{ width: '100%' }}>
            <Button 
              style={{ width: '50%' }} 
              onClick={() => form.setFieldValue('type', 'above')}
              type={form.getFieldValue('type') === 'above' ? 'primary' : 'default'}
            >
              价格上涨至
            </Button>
            <Button 
              style={{ width: '50%' }} 
              onClick={() => form.setFieldValue('type', 'below')}
              type={form.getFieldValue('type') === 'below' ? 'primary' : 'default'}
            >
              价格下跌至
            </Button>
          </Space.Compact>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" icon={<PlusOutlined />} block>
            添加提醒
          </Button>
        </Form.Item>
      </Form>

      {currentPrice && (
        <div style={{ marginBottom: 16, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
          <small style={{ color: '#666' }}>
            当前价格: <strong>${parseFloat(currentPrice || '0').toFixed(2)}</strong>
          </small>
        </div>
      )}

      <List
        size="small"
        dataSource={alerts}
        locale={{ emptyText: '暂无价格提醒' }}
        renderItem={alert => (
          <List.Item
            actions={[
              <Button
                type="text"
                danger
                size="small"
                icon={<DeleteOutlined />}
                onClick={() => removeAlert(alert.id)}
              />
            ]}
          >
            <div style={{ flex: 1 }}>
              <Tag color={alert.type === 'above' ? 'green' : 'red'}>
                {alert.type === 'above' ? '↗ 涨至' : '↘ 跌至'}
              </Tag>
              <span style={{ marginLeft: 8, fontWeight: 'bold' }}>
                ${parseFloat(alert.price || '0').toFixed(2)}
              </span>
              <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                {alert.created.toLocaleString()}
              </div>
            </div>
          </List.Item>
        )}
      />
    </Card>
  );
};

export default PriceAlert;
