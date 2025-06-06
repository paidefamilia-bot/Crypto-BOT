#!/usr/bin/env python3
"""
Gera dados de exemplo para teste do backtest
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(symbol='BTC', periods=1000, start_price=42000):
    """
    Gera dados sintéticos para teste
    """
    # Data inicial
    start_date = datetime(2024, 1, 1)
    
    # Gera timestamps (5 minutos)
    timestamps = [start_date + timedelta(minutes=5*i) for i in range(periods)]
    
    # Gera preços com random walk realista
    np.random.seed(42)  # Para reproduzibilidade
    
    prices = [start_price]
    for i in range(1, periods):
        # Movimento aleatório com tendência sutil
        change_pct = np.random.normal(0.0002, 0.015)  # 0.02% média, 1.5% volatilidade
        new_price = prices[-1] * (1 + change_pct)
        
        # Evita preços muito baixos
        new_price = max(new_price, start_price * 0.3)
        prices.append(new_price)
    
    # Gera OHLC realista
    data = []
    for i, (timestamp, close) in enumerate(zip(timestamps, prices)):
        # Open é o close anterior (ou preço inicial)
        open_price = prices[i-1] if i > 0 else close
        
        # High e Low com variação realista
        volatility = abs(np.random.normal(0, 0.008))  # 0.8% volatilidade intrabar
        high = max(open_price, close) * (1 + volatility)
        low = min(open_price, close) * (1 - volatility)
        
        # Volume aleatório
        volume = np.random.uniform(500000, 3000000)
        
        data.append({
            'timestamp': timestamp,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': round(volume, 2)
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Gera dados de exemplo
    print("📊 Gerando dados de exemplo...")
    
    # BTC com 1000 velas (suficiente para todos os indicadores)
    btc_data = generate_sample_data('BTC', periods=1000, start_price=42000)
    btc_data.to_csv('data/BTC-5m-sample-1000.csv', index=False)
    print(f"✅ BTC: {len(btc_data)} velas salvas em data/BTC-5m-sample-1000.csv")
    
    # ETH com 800 velas
    eth_data = generate_sample_data('ETH', periods=800, start_price=2800)
    eth_data.to_csv('data/ETH-5m-sample-800.csv', index=False)
    print(f"✅ ETH: {len(eth_data)} velas salvas em data/ETH-5m-sample-800.csv")
    
    print("\n📈 Resumo dos dados gerados:")
    print(f"BTC - Período: {btc_data['timestamp'].min()} a {btc_data['timestamp'].max()}")
    print(f"BTC - Preço: ${btc_data['close'].iloc[0]:.2f} → ${btc_data['close'].iloc[-1]:.2f}")
    print(f"ETH - Período: {eth_data['timestamp'].min()} a {eth_data['timestamp'].max()}")
    print(f"ETH - Preço: ${eth_data['close'].iloc[0]:.2f} → ${eth_data['close'].iloc[-1]:.2f}")
    
    print("\n🧪 Agora você pode testar com:")
    print("python test_backtest.py")
    print("python autonomous_backtest.py data/BTC-5m-sample-1000.csv")