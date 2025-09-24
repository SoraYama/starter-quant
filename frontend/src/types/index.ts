/**
 * 前端TypeScript类型定义
 */

// 基础类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// K线数据
export interface KLineData {
  symbol: string;
  timeframe: string;
  open_time: number;
  close_time: number;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
}

// 技术指标
export interface TechnicalIndicators {
  timestamp: number;
  macd?: number;
  macd_signal?: number;
  macd_histogram?: number;
  rsi?: number;
  bb_upper?: number;
  bb_middle?: number;
  bb_lower?: number;
  bb_width?: number;
}

// 交易信号
export interface SignalData {
  symbol: string;
  signal_type: 'BUY' | 'SELL';
  price: number;
  timestamp: number;
  confidence?: number;
  indicators?: TechnicalIndicators;
  strategy_name: string;
  timeframe: string;
  reason?: string;
}

// 策略配置  
export interface StrategyConfig {
  name: string;
  description?: string;
  macd_fast_period: number;
  macd_slow_period: number;
  macd_signal_period: number;
  rsi_period: number;
  rsi_oversold: number;
  rsi_overbought: number;
  bb_period: number;
  bb_std_dev: number;
  stop_loss_percent: number;
  take_profit_percent: number;
  max_position_size: number;
}

// 回测结果
export interface BacktestResult {
  backtest_id: number;
  symbol: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_balance: number;
  final_balance: number;
  total_return: number;
  max_drawdown: number;
  sharpe_ratio?: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  avg_profit?: number;
  avg_loss?: number;
  profit_factor?: number;
  created_at: string;
}

// 交易记录
export interface TradeRecord {
  id: number;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  timestamp: number;
  pnl?: number;
  commission: number;
  strategy_name?: string;
  reason?: string;
}

// 交易数据（用于TradingPage组件）
export interface TradeData {
  trade_id: string;
  timestamp: number;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  commission?: number;
}

// 账户信息
export interface AccountInfo {
  account_type: string;
  total_balance: number;
  available_balance: number;
  locked_balance: number;
  positions: Position[];
  api_mode: string;
}

// 持仓信息
export interface Position {
  symbol: string;
  side: 'LONG' | 'SHORT';
  quantity: number;
  avg_price: number;
  current_price: number;
  unrealized_pnl: number;
  pnl_percentage: number;
  entry_time: number;
}

// 订单信息
export interface OrderInfo {
  order_id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  status: string;
  timestamp: number;
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: 'connection' | 'price_update' | 'signal_update' | 'market_update' | 'subscription' | 'error' | 'pong' | 'status';
  symbol?: string;
  data?: any;
  timestamp: string;
  client_id?: string;
  message?: string;
}

// 市场概览
export interface MarketOverview {
  total_symbols: number;
  active_symbols: number;
  supported_symbols: string[];
  api_mode: string;
  last_update: string;
}

// 价格统计
export interface TickerData {
  symbol: string;
  price: number;
  price_change: number;
  price_change_percent: number;
  high_price: number;
  low_price: number;
  volume: number;
  quote_volume: number;
  open_price: number;
  prev_close_price: number;
  bid_price: number;
  ask_price: number;
  timestamp: number;
}

// 图表数据点
export interface ChartDataPoint {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

// 回测请求
export interface BacktestRequest {
  symbol: string;
  start_date: string;
  end_date: string;
  initial_balance: number;
  timeframe: string;
  strategy_config?: StrategyConfig;
}

// 订单请求
export interface OrderRequest {
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price?: number;
  order_type: 'MARKET' | 'LIMIT';
}

// 应用状态
export interface AppState {
  isLoading: boolean;
  error: string | null;
  selectedSymbol: string;
  timeframe: string;
  isConnected: boolean;
  apiMode: 'PUBLIC_MODE' | 'FULL_MODE';
}

// 路由路径
export enum RoutePaths {
  HOME = '/',
  MARKET = '/market',
  STRATEGY = '/strategy', 
  BACKTEST = '/backtest',
  TRADING = '/trading',
  SETTINGS = '/settings'
}

// 主题类型
export type ThemeMode = 'light' | 'dark';

// 图表主题
export interface ChartTheme {
  background: string;
  textColor: string;
  gridColor: string;
  upColor: string;
  downColor: string;
  volumeColor: string;
}
