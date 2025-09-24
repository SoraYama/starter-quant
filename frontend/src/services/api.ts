/**
 * API服务层
 * 封装所有与后端的HTTP请求
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  ApiResponse,
  KLineData,
  SignalData,
  StrategyConfig,
  BacktestResult,
  BacktestRequest,
  AccountInfo,
  OrderRequest,
  OrderInfo,
  MarketOverview,
  TickerData
} from '@/types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // 通用请求方法
  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: any,
    params?: any
  ): Promise<T> {
    try {
      const response = await this.api.request({
        method,
        url,
        data,
        params,
      });
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'API请求失败';
      throw new Error(errorMessage);
    }
  }

  // 市场数据API
  market = {
    // 获取K线数据
    getKlines: async (params: {
      symbol: string;
      interval?: string;
      limit?: number;
      start_time?: number;
      end_time?: number;
      use_cache?: boolean;
    }): Promise<ApiResponse<KLineData[]>> => {
      return this.request('GET', `/market/klines/${params.symbol}`, null, {
        interval: params.interval || '4h',
        limit: params.limit || 500,
        start_time: params.start_time,
        end_time: params.end_time,
        use_cache: params.use_cache ?? true,
      });
    },

    // 获取实时价格
    getTicker: async (symbol: string): Promise<ApiResponse<TickerData>> => {
      return this.request('GET', `/market/ticker/${symbol}`);
    },

    // 获取价格（别名方法）
    getPrice: async (symbol: string): Promise<ApiResponse<TickerData>> => {
      return this.request('GET', `/market/ticker/${symbol}`);
    },

    // 获取历史数据
    getHistoricalData: async (params: {
      symbol: string;
      interval?: string;
      days?: number;
    }): Promise<ApiResponse<KLineData[]>> => {
      return this.request('GET', `/market/historical/${params.symbol}`, null, {
        interval: params.interval || '4h',
        days: params.days || 30,
      });
    },

    // 获取市场概览
    getOverview: async (): Promise<MarketOverview> => {
      return this.request('GET', '/market/overview');
    },

    // 获取支持的交易对
    getSymbols: async (): Promise<ApiResponse<{
      symbols: string[];
      intervals: string[];
      default_interval: string;
    }>> => {
      return this.request('GET', '/market/symbols');
    },

    // 获取市场状态
    getStatus: async (): Promise<ApiResponse<any>> => {
      return this.request('GET', '/market/status');
    },

    // 刷新市场数据
    refreshData: async (symbol?: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/market/refresh', { symbol });
    },
  };

  // 策略分析API
  strategy = {
    // 分析交易对
    analyze: async (params: {
      symbol: string;
      timeframe?: string;
      limit?: number;
      config?: StrategyConfig;
    }): Promise<ApiResponse<{
      signals: SignalData[];
      indicators: any[];
      symbol: string;
      timeframe: string;
      strategy_config: StrategyConfig;
    }>> => {
      return this.request('POST', '/strategy/analyze', {
        symbol: params.symbol,
        timeframe: params.timeframe || '4h',
        limit: params.limit || 200,
        config: params.config,
      });
    },

    // 获取最新信号
    getLatestSignals: async (params: {
      symbol: string;
      timeframe?: string;
      limit?: number;
    }): Promise<ApiResponse<{
      signals: SignalData[];
      total_count: number;
    }>> => {
      return this.request('GET', `/strategy/signals/${params.symbol}`, null, {
        timeframe: params.timeframe || '4h',
        limit: params.limit || 10,
      });
    },

    // 获取技术指标
    getIndicators: async (params: {
      symbol: string;
      timeframe?: string;
    }): Promise<ApiResponse<any>> => {
      return this.request('GET', `/strategy/indicators/${params.symbol}`, null, {
        timeframe: params.timeframe || '4h',
      });
    },

    // 评估信号强度
    evaluateStrength: async (params: {
      symbol: string;
      timeframe?: string;
    }): Promise<ApiResponse<{
      strength: string;
      confidence: number;
      buy_signals: number;
      sell_signals: number;
      latest_signal?: SignalData;
    }>> => {
      return this.request('GET', `/strategy/strength/${params.symbol}`, null, {
        timeframe: params.timeframe || '4h',
      });
    },

    // 批量分析
    batchAnalyze: async (params: {
      symbols: string[];
      timeframe?: string;
      config?: StrategyConfig;
    }): Promise<ApiResponse<any>> => {
      return this.request('POST', '/strategy/batch-analyze', {
        symbols: params.symbols,
        timeframe: params.timeframe || '4h',
        config: params.config,
      });
    },

    // 获取默认配置
    getDefaultConfig: async (): Promise<ApiResponse<{
      config: StrategyConfig;
    }>> => {
      return this.request('GET', '/strategy/config/default');
    },

    // 验证配置
    validateConfig: async (config: StrategyConfig): Promise<ApiResponse<{
      valid: boolean;
      config: StrategyConfig;
    }>> => {
      return this.request('POST', '/strategy/config/validate', config);
    },

    // 获取策略概览
    getOverview: async (): Promise<ApiResponse<any>> => {
      return this.request('GET', '/strategy/overview');
    },
  };

  // 回测API
  backtest = {
    // 运行回测
    run: async (request: BacktestRequest): Promise<ApiResponse<BacktestResult>> => {
      return this.request('POST', '/backtest/run', request);
    },

    // 获取回测历史
    getHistory: async (params: {
      limit?: number;
      symbol?: string;
    }): Promise<ApiResponse<BacktestResult[]>> => {
      return this.request('GET', '/backtest/history', null, {
        limit: params.limit || 20,
        symbol: params.symbol,
      });
    },

    // 获取回测详情
    getDetail: async (backtestId: number): Promise<ApiResponse<BacktestResult & {
      trades: any[];
    }>> => {
      return this.request('GET', `/backtest/detail/${backtestId}`);
    },

    // 快速回测
    quickTest: async (params: {
      symbol: string;
      days?: number;
      initial_balance?: number;
    }): Promise<ApiResponse<BacktestResult>> => {
      return this.request('POST', '/backtest/quick-test', {
        symbol: params.symbol,
        days: params.days || 30,
        initial_balance: params.initial_balance || 10000,
      });
    },

    // 获取性能摘要
    getPerformanceSummary: async (limit?: number): Promise<ApiResponse<any>> => {
      return this.request('GET', '/backtest/performance-summary', null, {
        limit: limit || 10,
      });
    },

    // 删除回测记录
    delete: async (backtestId: number): Promise<ApiResponse<any>> => {
      return this.request('DELETE', `/backtest/delete/${backtestId}`);
    },
  };

  // 交易API
  trading = {
    // 获取账户信息
    getAccount: async (): Promise<AccountInfo> => {
      return this.request('GET', '/trading/account');
    },

    // 下单
    placeOrder: async (order: OrderRequest): Promise<ApiResponse<OrderInfo>> => {
      return this.request('POST', '/trading/order', order);
    },

    // 获取订单历史
    getOrders: async (params: {
      symbol?: string;
      limit?: number;
    }): Promise<ApiResponse<{
      orders: OrderInfo[];
      count: number;
    }>> => {
      return this.request('GET', '/trading/orders', null, {
        symbol: params.symbol,
        limit: params.limit || 20,
      });
    },

    // 获取持仓
    getPositions: async (): Promise<ApiResponse<{
      positions: any[];
      count: number;
    }>> => {
      return this.request('GET', '/trading/positions');
    },

    // 取消订单
    cancelOrder: async (orderId: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/trading/cancel-order/${orderId}`);
    },

    // 获取交易状态
    getStatus: async (): Promise<ApiResponse<any>> => {
      return this.request('GET', '/trading/trading-status');
    },

    // 模拟交易
    simulateTrade: async (params: {
      symbol: string;
      side: string;
      quantity: number;
      current_price: number;
    }): Promise<ApiResponse<any>> => {
      return this.request('POST', '/trading/simulate-trade', params);
    },
  };

  // 系统API
  system = {
    // 健康检查
    health: async (): Promise<ApiResponse<any>> => {
      return this.request('GET', '/');
    },
  };
}

// 导出单例实例
export const apiService = new ApiService();
export default apiService;
