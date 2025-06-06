#!/usr/bin/env python3
"""
🌙 Moon Dev's Autonomous Trading Backtest - Main Script
Execute backtest with CSV data files
Built with love by Moon Dev 🚀

Usage:
    python autonomous_backtest.py BTC-5m-30wks-data.csv
    python autonomous_backtest.py BTC-5m-30wks-data.csv ETH-1h-12wks-data.csv
    python autonomous_backtest.py data/BTC-5m-30wks-data.csv --capital 50000 --confidence-min 70
"""

import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importa e executa o backtest
from src.backtest.autonomous_backtest import main

if __name__ == "__main__":
    main()