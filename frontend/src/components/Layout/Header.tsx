import React from 'react';
import { Layout, Button, Space, Badge, Tooltip, Switch } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  WifiOutlined,
  WifiOutlined as WifiDisconnectedOutlined,
} from '@ant-design/icons';

const { Header: AntHeader } = Layout;

interface HeaderProps {
  collapsed: boolean;
  onCollapse: () => void;
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
  isConnected: boolean;
}

const Header: React.FC<HeaderProps> = ({
  collapsed,
  onCollapse,
  theme,
  onThemeToggle,
  isConnected,
}) => {
  return (
    <AntHeader
      style={{
        padding: '0 24px',
        background: theme === 'dark' ? '#001529' : '#fff',
        borderBottom: `1px solid ${theme === 'dark' ? '#303030' : '#f0f0f0'}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      {/* 左侧：折叠按钮 */}
      <Button
        type="text"
        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        onClick={onCollapse}
        style={{
          fontSize: '16px',
          width: 64,
          height: 64,
          color: theme === 'dark' ? '#fff' : '#000',
        }}
      />

      {/* 右侧：工具栏 */}
      <Space size="middle">
        {/* WebSocket连接状态 */}
        <Tooltip title={isConnected ? '实时数据已连接' : '实时数据连接断开'}>
          <Badge
            status={isConnected ? 'success' : 'error'}
            text={
              isConnected ? (
                <WifiOutlined style={{ color: '#52c41a' }} />
              ) : (
                <WifiDisconnectedOutlined style={{ color: '#ff4d4f' }} />
              )
            }
          />
        </Tooltip>

        {/* 通知 */}
        <Tooltip title="通知">
          <Button
            type="text"
            icon={<BellOutlined />}
            style={{ color: theme === 'dark' ? '#fff' : '#000' }}
          />
        </Tooltip>

        {/* 主题切换 */}
        <Tooltip title={theme === 'dark' ? '切换到浅色主题' : '切换到深色主题'}>
          <Switch
            checked={theme === 'dark'}
            onChange={onThemeToggle}
            checkedChildren="🌙"
            unCheckedChildren="☀️"
          />
        </Tooltip>
      </Space>
    </AntHeader>
  );
};

export default Header;
