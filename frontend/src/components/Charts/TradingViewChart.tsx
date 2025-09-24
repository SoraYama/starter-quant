import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle } from 'lightweight-charts';
import { KLineData } from '@/types';

interface TradingViewChartProps {
  data: KLineData[];
  symbol: string;
  interval: string;
  height?: number;
  showVolume?: boolean;
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({
  data,
  symbol,
  interval,
  height = 400,
  showVolume = true,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
      layout: {
        background: { color: 'transparent' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#e1e1e1', style: LineStyle.Solid },
        horzLines: { color: '#e1e1e1', style: LineStyle.Solid },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#cccccc',
        scaleMargins: {
          top: 0.1,
          bottom: showVolume ? 0.3 : 0.1,
        },
      },
      timeScale: {
        borderColor: '#cccccc',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // 创建K线图系列
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    candlestickSeriesRef.current = candlestickSeries;

    // 创建成交量系列
    if (showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
      });

      volumeSeriesRef.current = volumeSeries;

      // 设置成交量价格比例
      volumeSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.7,
          bottom: 0,
        },
      });
    }

    // 响应式调整
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [height, showVolume]);

  // 更新数据
  useEffect(() => {
    if (!data || data.length === 0) return;
    if (!candlestickSeriesRef.current || !chartRef.current) return;

    try {
      // 转换K线数据，确保时间格式正确
      const candlestickData = data
        .filter(item => item.open_time && !isNaN(item.open_time))
        .map(item => {
          // 确保时间戳是有效的数字
          const timestamp = typeof item.open_time === 'number' ? item.open_time : parseInt(item.open_time);
          return {
            time: Math.floor(timestamp / 1000) as any,
            open: parseFloat(item.open_price) || 0,
            high: parseFloat(item.high_price) || 0,
            low: parseFloat(item.low_price) || 0,
            close: parseFloat(item.close_price) || 0,
          };
        })
        .filter(item => item.time > 0); // 过滤掉无效的时间戳

      if (candlestickData.length === 0) {
        console.warn('No valid chart data available');
        return;
      }

      candlestickSeriesRef.current.setData(candlestickData);

      // 设置成交量数据
      if (showVolume && volumeSeriesRef.current) {
        const volumeData = data
          .filter(item => item.open_time && !isNaN(item.open_time))
          .map(item => {
            const timestamp = typeof item.open_time === 'number' ? item.open_time : parseInt(item.open_time);
            return {
              time: Math.floor(timestamp / 1000) as any,
              value: parseFloat(item.volume) || 0,
              color: parseFloat(item.close_price) >= parseFloat(item.open_price) ? '#26a69a' : '#ef5350',
            };
          })
          .filter(item => item.time > 0);

        if (volumeData.length > 0) {
          volumeSeriesRef.current.setData(volumeData);
        }
      }

      // 自动调整视图范围
      chartRef.current.timeScale().fitContent();
    } catch (error) {
      console.error('Error updating chart data:', error);
    }
  }, [data, showVolume]);

  return (
    <div style={{ position: 'relative', width: '100%', height }}>
      <div 
        ref={chartContainerRef} 
        style={{ width: '100%', height: '100%' }}
      />
      <div 
        style={{
          position: 'absolute',
          top: 10,
          left: 10,
          color: '#666',
          fontSize: 14,
          fontWeight: 'bold',
          pointerEvents: 'none',
        }}
      >
        {symbol} - {interval}
      </div>
    </div>
  );
};

export default TradingViewChart;
