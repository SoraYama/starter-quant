import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, ConfigProvider, theme, App as AntdApp } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// 页面组件
import DashboardPage from '@/components/Dashboard/DashboardPage';
import MarketPage from '@/pages/MarketPage';
import StrategyPage from '@/pages/StrategyPage';
import BacktestPage from '@/pages/BacktestPage';
import TradingPage from '@/pages/TradingPage';
import SettingsPage from '@/pages/SettingsPage';

// 布局组件
import Header from '@/components/Layout/Header';
import Sidebar from '@/components/Layout/Sidebar';

// 服务
import { websocketService } from '@/services/websocket';

import './App.css';

const { Content } = Layout;

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
      // 注意：这里不再使用静态 notification，而是在组件内部处理
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

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={themeConfig}>
        <AntdApp>
          <Router>
            <Layout style={{ minHeight: '100vh' }}>
              {/* 侧边栏 */}
              <Sidebar 
                collapsed={collapsed} 
                theme={isDarkMode ? 'dark' : 'light'}
              />
              
              <Layout>
                {/* 顶部导航 */}
                <Header
                  collapsed={collapsed}
                  onCollapse={() => setCollapsed(!collapsed)}
                  theme={isDarkMode ? 'dark' : 'light'}
                  onThemeToggle={toggleTheme}
                  isConnected={wsConnected}
                />
                
                {/* 主内容区域 */}
                <Content className="main-content">
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
                </Content>
              </Layout>
            </Layout>
          </Router>
        </AntdApp>
      </ConfigProvider>
      
      {/* React Query DevTools (仅在开发环境显示) */}
      {import.meta.env.MODE === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
};

export default App;
