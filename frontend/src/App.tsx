import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme, App as AntdApp } from 'antd';
import { ProLayout } from '@ant-design/pro-components';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// 页面组件
import DashboardPage from '@/components/Dashboard/DashboardPage';
import MarketPage from '@/pages/MarketPage';
import StrategyPage from '@/pages/StrategyPage';
import BacktestPage from '@/pages/BacktestPage';
import TradingPage from '@/pages/TradingPage';
import SettingsPage from '@/pages/SettingsPage';

// 服务
import { websocketService } from '@/services/websocket';

import './App.css';

// 创建QueryClient实例
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30000, // 30秒
    },
  },
});

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  // WebSocket连接管理
  useEffect(() => {
    // 连接WebSocket
    websocketService.connect();

    // 监听连接状态
    const handleConnectionChange = (connected: boolean) => {
      setWsConnected(connected);
      console.log('WebSocket connection status:', connected ? 'connected' : 'disconnected');
    };

    websocketService.onConnectionChange(handleConnectionChange);

    // 清理函数
    return () => {
      websocketService.disconnect();
    };
  }, []);

  // 主题配置
  const themeConfig = {
    algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 6,
    },
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  // ProLayout 菜单配置
  const menuItems = [
    {
      key: '/dashboard',
      icon: '📊',
      label: '仪表板',
    },
    {
      key: '/market',
      icon: '📈',
      label: '市场数据',
    },
    {
      key: '/strategy',
      icon: '🤖',
      label: '策略管理',
    },
    {
      key: '/backtest',
      icon: '📋',
      label: '回测分析',
    },
    {
      key: '/trading',
      icon: '💰',
      label: '实盘交易',
    },
    {
      key: '/settings',
      icon: '⚙️',
      label: '系统设置',
    },
  ];

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={themeConfig}>
        <AntdApp>
          <Router>
            <ProLayout
              title="CryptoQuantBot"
              logo="https://gw.alipayobjects.com/zos/antfincdn/PmY%24TNNDBI/logo.svg"
              collapsed={collapsed}
              onCollapse={setCollapsed}
              route={{
                path: '/',
                routes: menuItems,
              }}
              location={{
                pathname: window.location.pathname,
              }}
              menuItemRender={(item, dom) => (
                <a
                  onClick={() => {
                    window.history.pushState(null, '', item.path || '/');
                    window.location.reload();
                  }}
                >
                  {dom}
                </a>
              )}
              headerContentRender={() => (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  marginRight: 16
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8
                  }}>
                    <div
                      style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        backgroundColor: wsConnected ? '#52c41a' : '#ff4d4f'
                      }}
                    />
                    <span style={{ fontSize: 12 }}>
                      {wsConnected ? '实时连接' : '离线模式'}
                    </span>
                  </div>
                  <button
                    onClick={toggleTheme}
                    style={{
                      padding: '4px 8px',
                      border: '1px solid #d9d9d9',
                      borderRadius: 4,
                      background: 'transparent',
                      cursor: 'pointer',
                    }}
                  >
                    {isDarkMode ? '🌞' : '🌙'}
                  </button>
                </div>
              )}
              fixSiderbar={true}
              layout="side"
              theme={isDarkMode ? 'dark' : 'light'}
            >
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/market" element={<MarketPage />} />
                <Route path="/strategy" element={<StrategyPage />} />
                <Route path="/backtest" element={<BacktestPage />} />
                <Route path="/trading" element={<TradingPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </ProLayout>
          </Router>
        </AntdApp>
      </ConfigProvider>

      {/* React Query DevTools (仅在开发环境显示) */}
      {/* @ts-ignore import.meta.env is not defined in the browser */}
      {import.meta.env.MODE === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
};

export default App;
