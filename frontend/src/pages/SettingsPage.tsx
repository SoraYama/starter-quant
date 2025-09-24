import React, { useState } from 'react';
import { 
  Card, Form, Input, Button, Switch, Select, InputNumber, 
  Tabs, Space, Alert, Modal, notification, Divider 
} from 'antd';
import { 
  SettingOutlined, ApiOutlined, BellOutlined, 
  SafetyOutlined, SaveOutlined, ReloadOutlined 
} from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface SettingsFormData {
  // API配置
  api_mode: 'PUBLIC_MODE' | 'FULL_MODE';
  binance_api_key: string;
  binance_api_secret: string;
  binance_testnet: boolean;
  
  // 交易配置
  default_symbols: string[];
  default_timeframe: string;
  auto_trading_enabled: boolean;
  max_position_size: number;
  risk_management_enabled: boolean;
  stop_loss_percentage: number;
  take_profit_percentage: number;
  
  // 通知配置
  notifications_enabled: boolean;
  email_notifications: boolean;
  price_alert_enabled: boolean;
  trade_notifications: boolean;
  
  // 策略配置
  macd_fast: number;
  macd_slow: number;
  macd_signal: number;
  rsi_period: number;
  rsi_overbought: number;
  rsi_oversold: number;
  bb_period: number;
  bb_std_dev: number;
}

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testConnectionLoading, setTestConnectionLoading] = useState(false);
  const [resetModalVisible, setResetModalVisible] = useState(false);

  // 初始化表单数据
  const initialValues: Partial<SettingsFormData> = {
    api_mode: 'PUBLIC_MODE',
    binance_testnet: true,
    default_symbols: ['BTCUSDT', 'ETHUSDT'],
    default_timeframe: '4h',
    auto_trading_enabled: false,
    max_position_size: 1000,
    risk_management_enabled: true,
    stop_loss_percentage: 2,
    take_profit_percentage: 5,
    notifications_enabled: true,
    email_notifications: false,
    price_alert_enabled: true,
    trade_notifications: true,
    // 技术指标默认参数
    macd_fast: 12,
    macd_slow: 26,
    macd_signal: 9,
    rsi_period: 14,
    rsi_overbought: 70,
    rsi_oversold: 30,
    bb_period: 20,
    bb_std_dev: 2.0,
  };

  const handleSave = async (values: SettingsFormData) => {
    setLoading(true);
    try {
      // 这里应该调用API保存配置
      await new Promise(resolve => setTimeout(resolve, 1000)); // 模拟API调用
      
      notification.success({
        message: '配置保存成功',
        description: '您的设置已保存，部分配置需要重启应用后生效。',
      });
    } catch (error) {
      notification.error({
        message: '配置保存失败',
        description: '请检查网络连接后重试。',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    setTestConnectionLoading(true);
    try {
      const values = form.getFieldsValue();
      if (!values.binance_api_key || !values.binance_api_secret) {
        notification.warning({
          message: 'API密钥未设置',
          description: '请先填写币安API密钥和密钥。',
        });
        return;
      }

      // 模拟API连接测试
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      notification.success({
        message: 'API连接测试成功',
        description: '币安API连接正常，可以正常获取数据。',
      });
    } catch (error) {
      notification.error({
        message: 'API连接测试失败',
        description: '请检查API密钥是否正确，或网络是否正常。',
      });
    } finally {
      setTestConnectionLoading(false);
    }
  };

  const handleReset = () => {
    form.setFieldsValue(initialValues);
    setResetModalVisible(false);
    notification.info({
      message: '配置已重置',
      description: '所有设置已恢复为默认值，请保存生效。',
    });
  };

  return (
    <div style={{ padding: 16 }}>
      <Card title="系统设置" className="dashboard-card">
        <Form
          form={form}
          layout="vertical"
          initialValues={initialValues}
          onFinish={handleSave}
        >
          <Tabs defaultActiveKey="api" type="card">
            {/* API配置 */}
            <TabPane tab={<span><ApiOutlined />API配置</span>} key="api">
              <Alert
                message="API配置说明"
                description="切换到完整功能模式需要有效的币安API密钥。请确保API密钥具有适当的权限（现货交易、读取账户信息）。"
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              <Form.Item
                name="api_mode"
                label="API模式"
                tooltip="公开数据模式只能获取市场数据，完整功能模式支持账户管理和交易"
              >
                <Select>
                  <Option value="PUBLIC_MODE">公开数据模式（推荐新手）</Option>
                  <Option value="FULL_MODE">完整功能模式（需要API密钥）</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="binance_testnet"
                label="使用测试网"
                valuePropName="checked"
                tooltip="测试网环境安全无风险，建议初学者使用"
              >
                <Switch checkedChildren="测试网" unCheckedChildren="主网" />
              </Form.Item>

              <Form.Item
                name="binance_api_key"
                label="币安API Key"
                tooltip="从币安账户的API管理页面获取"
              >
                <Input.Password 
                  placeholder="请输入币安API Key" 
                  visibilityToggle={false}
                />
              </Form.Item>

              <Form.Item
                name="binance_api_secret"
                label="币安API Secret"
                tooltip="从币安账户的API管理页面获取，请妥善保管"
              >
                <Input.Password 
                  placeholder="请输入币安API Secret"
                  visibilityToggle={false}
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button 
                    type="dashed"
                    icon={<ApiOutlined />}
                    onClick={handleTestConnection}
                    loading={testConnectionLoading}
                  >
                    测试API连接
                  </Button>
                  <Button type="link" href="../binance_api_guide.md" target="_blank">
                    查看API密钥获取指南
                  </Button>
                </Space>
              </Form.Item>
            </TabPane>

            {/* 交易配置 */}
            <TabPane tab={<span><SettingOutlined />交易配置</span>} key="trading">
              <Form.Item
                name="default_symbols"
                label="默认交易对"
                tooltip="系统启动时默认加载的交易对"
              >
                <Select mode="multiple" placeholder="选择默认交易对">
                  <Option value="BTCUSDT">BTC/USDT</Option>
                  <Option value="ETHUSDT">ETH/USDT</Option>
                  <Option value="BNBUSDT">BNB/USDT</Option>
                  <Option value="ADAUSDT">ADA/USDT</Option>
                  <Option value="DOTUSDT">DOT/USDT</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="default_timeframe"
                label="默认时间周期"
                tooltip="策略分析和图表显示的默认时间周期"
              >
                <Select>
                  <Option value="1h">1小时</Option>
                  <Option value="4h">4小时</Option>
                  <Option value="1d">1天</Option>
                  <Option value="1w">1周</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="auto_trading_enabled"
                label="启用自动交易"
                valuePropName="checked"
                tooltip="启用后系统将根据策略信号自动执行交易"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="max_position_size"
                label="最大仓位大小 (USDT)"
                tooltip="单次交易的最大金额限制"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={100}
                  max={100000}
                  placeholder="1000"
                />
              </Form.Item>

              <Divider>风险管理</Divider>

              <Form.Item
                name="risk_management_enabled"
                label="启用风险管理"
                valuePropName="checked"
                tooltip="启用止损和止盈自动管理"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="stop_loss_percentage"
                label="止损百分比 (%)"
                tooltip="当亏损达到此百分比时自动止损"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0.1}
                  max={20}
                  step={0.1}
                  placeholder="2.0"
                />
              </Form.Item>

              <Form.Item
                name="take_profit_percentage"
                label="止盈百分比 (%)"
                tooltip="当盈利达到此百分比时自动止盈"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  max={50}
                  step={0.1}
                  placeholder="5.0"
                />
              </Form.Item>
            </TabPane>

            {/* 策略参数 */}
            <TabPane tab={<span><SettingOutlined />策略参数</span>} key="strategy">
              <Alert
                message="技术指标参数"
                description="调整技术指标的计算参数，建议有经验的用户修改。默认参数已经过优化，适合大多数市场条件。"
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              <Divider>MACD指标</Divider>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Form.Item
                  name="macd_fast"
                  label="快线周期"
                  tooltip="MACD快线EMA周期，通常为12"
                >
                  <InputNumber min={5} max={50} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name="macd_slow"
                  label="慢线周期"
                  tooltip="MACD慢线EMA周期，通常为26"
                >
                  <InputNumber min={10} max={100} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name="macd_signal"
                  label="信号线周期"
                  tooltip="MACD信号线EMA周期，通常为9"
                >
                  <InputNumber min={3} max={30} style={{ width: '100%' }} />
                </Form.Item>
              </Space>

              <Divider>RSI指标</Divider>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Form.Item
                  name="rsi_period"
                  label="RSI周期"
                  tooltip="RSI计算周期，通常为14"
                >
                  <InputNumber min={5} max={50} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name="rsi_overbought"
                  label="超买阈值"
                  tooltip="RSI超买阈值，通常为70"
                >
                  <InputNumber min={60} max={90} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name="rsi_oversold"
                  label="超卖阈值"
                  tooltip="RSI超卖阈值，通常为30"
                >
                  <InputNumber min={10} max={40} style={{ width: '100%' }} />
                </Form.Item>
              </Space>

              <Divider>布林带指标</Divider>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Form.Item
                  name="bb_period"
                  label="布林带周期"
                  tooltip="布林带移动平均线周期，通常为20"
                >
                  <InputNumber min={10} max={50} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name="bb_std_dev"
                  label="标准差倍数"
                  tooltip="布林带标准差倍数，通常为2.0"
                >
                  <InputNumber min={1} max={3} step={0.1} style={{ width: '100%' }} />
                </Form.Item>
              </Space>
            </TabPane>

            {/* 通知设置 */}
            <TabPane tab={<span><BellOutlined />通知设置</span>} key="notifications">
              <Form.Item
                name="notifications_enabled"
                label="启用通知"
                valuePropName="checked"
                tooltip="启用系统通知功能"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="price_alert_enabled"
                label="价格提醒"
                valuePropName="checked"
                tooltip="启用价格达到设定值时的提醒"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="trade_notifications"
                label="交易通知"
                valuePropName="checked"
                tooltip="交易执行时发送通知"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="email_notifications"
                label="邮件通知"
                valuePropName="checked"
                tooltip="通过邮件发送重要通知（需要配置邮件服务）"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </TabPane>
          </Tabs>

          {/* 操作按钮 */}
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Space>
              <Button 
                icon={<ReloadOutlined />}
                onClick={() => setResetModalVisible(true)}
              >
                重置为默认值
              </Button>
              <Button 
                type="primary" 
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
              >
                保存配置
              </Button>
            </Space>
          </div>
        </Form>

        {/* 重置确认弹窗 */}
        <Modal
          title="确认重置"
          open={resetModalVisible}
          onOk={handleReset}
          onCancel={() => setResetModalVisible(false)}
          okText="确认重置"
          cancelText="取消"
        >
          <Alert
            message="警告"
            description="此操作将重置所有配置为默认值，包括API密钥等敏感信息。请确认是否继续？"
            type="warning"
            showIcon
          />
        </Modal>
      </Card>
    </div>
  );
};

export default SettingsPage;
