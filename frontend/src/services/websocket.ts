/**
 * WebSocket服务
 * 管理实时数据连接和消息处理
 */

import { WebSocketMessage } from '@/types';

type EventCallback = (data: any) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private isConnecting = false;
  private eventListeners: Map<string, EventCallback[]> = new Map();
  private subscriptions: Set<string> = new Set();
  private connectionCallback: ((connected: boolean) => void) | null = null;

  constructor() {
    this.connect();
  }

  // 连接WebSocket
  public connect(): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
    
    console.log('Connecting to WebSocket:', wsUrl);

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  // 设置WebSocket事件处理器
  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected successfully');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.emit('connected', { connected: true });
      if (this.connectionCallback) {
        this.connectionCallback(true);
      }
      
      // 重新订阅之前的交易对
      this.subscriptions.forEach(symbol => {
        this.subscribe(symbol);
      });
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('WebSocket message received:', message);
        this.handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.isConnecting = false;
      this.emit('disconnected', { connected: false });
      if (this.connectionCallback) {
        this.connectionCallback(false);
      }
      
      if (event.code !== 1000) { // 非正常关闭
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.emit('error', { error });
    };
  }

  // 处理接收到的消息
  private handleMessage(message: WebSocketMessage): void {
    const { type, symbol, data } = message;

    switch (type) {
      case 'connection':
        this.emit('connection', data);
        break;
      
      case 'price_update':
        if (symbol) {
          this.emit(`price_${symbol}`, data);
          this.emit('price_update', { symbol, data });
        }
        break;
      
      case 'signal_update':
        if (symbol) {
          this.emit(`signal_${symbol}`, data);
          this.emit('signal_update', { symbol, data });
        }
        break;
      
      case 'market_update':
        this.emit('market_update', data);
        break;
      
      case 'subscription':
        this.emit('subscription', data);
        break;
      
      case 'error':
        this.emit('error', data);
        console.error('WebSocket server error:', data);
        break;
      
      case 'pong':
        this.emit('pong', data);
        break;
      
      case 'status':
        this.emit('status', data);
        break;
      
      default:
        console.warn('Unknown WebSocket message type:', type);
    }
  }

  // 发送消息
  private sendMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected, message not sent:', message);
    }
  }

  // 订阅交易对数据
  subscribe(symbol: string): void {
    this.subscriptions.add(symbol);
    this.sendMessage({
      type: 'subscribe',
      symbol: symbol.toUpperCase()
    });
  }

  // 取消订阅
  unsubscribe(symbol: string): void {
    this.subscriptions.delete(symbol);
    this.sendMessage({
      type: 'unsubscribe',
      symbol: symbol.toUpperCase()
    });
  }

  // Ping服务器
  ping(): void {
    this.sendMessage({
      type: 'ping'
    });
  }

  // 获取连接状态
  getStatus(): void {
    this.sendMessage({
      type: 'get_status'
    });
  }

  // 添加事件监听器
  on(event: string, callback: EventCallback): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  // 移除事件监听器
  off(event: string, callback?: EventCallback): void {
    if (!callback) {
      this.eventListeners.delete(event);
      return;
    }

    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  // 触发事件
  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket event callback:', error);
        }
      });
    }
  }

  // 安排重连
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('max_reconnect_attempts', { attempts: this.reconnectAttempts });
      return;
    }

    this.reconnectAttempts++;
    console.log(`Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectInterval}ms`);
    
    setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  // 手动重连
  reconnect(): void {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.connect();
  }

  // 断开连接
  public disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
    this.isConnecting = false;
    this.subscriptions.clear();
  }

  // 获取连接状态
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  // 获取当前订阅
  getSubscriptions(): string[] {
    return Array.from(this.subscriptions);
  }

  // 连接状态变化回调
  public onConnectionChange(callback: (connected: boolean) => void): void {
    this.connectionCallback = callback;
  }
}

export const websocketService = new WebSocketService();
export default websocketService;
