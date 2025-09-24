import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  BarChartOutlined,
  SettingOutlined,
  RobotOutlined,
  HistoryOutlined,
  DollarOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;

interface SidebarProps {
  collapsed: boolean;
  theme: 'light' | 'dark';
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, theme }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: '/market',
      icon: <BarChartOutlined />,
      label: '市场数据',
    },
    {
      key: '/strategy',
      icon: <RobotOutlined />,
      label: '策略管理',
    },
    {
      key: '/backtest',
      icon: <HistoryOutlined />,
      label: '回测分析',
    },
    {
      key: '/trading',
      icon: <DollarOutlined />,
      label: '实盘交易',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={collapsed}
      theme={theme}
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 1000,
      }}
    >
      <div
        style={{
          height: 64,
          margin: 16,
          background: theme === 'dark' ? '#1890ff' : '#f0f0f0',
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: theme === 'dark' ? '#fff' : '#000',
          fontWeight: 'bold',
          fontSize: collapsed ? 12 : 16,
        }}
      >
        {collapsed ? 'CQB' : 'CryptoQuantBot'}
      </div>

      <Menu
        theme={theme}
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{
          borderRight: 0,
        }}
      />
    </Sider>
  );
};

export default Sidebar;
