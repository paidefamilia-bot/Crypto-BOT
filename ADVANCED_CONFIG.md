# 🌙 Moon Dev's Advanced Configuration Guide

## 🎯 Configurações Avançadas para Trading 24/7

### 1. Ajuste de Parâmetros de Risco

#### Em `src/core/config.py`:

```python
# Gestão de Risco Conservadora
CASH_PERCENTAGE = 30  # 30% sempre em USDT
MAX_POSITION_PERCENTAGE = 20  # Máximo 20% por posição
RUN_INTERVAL_MINUTES = 30  # Análise a cada 30 min

# Gestão de Risco Agressiva  
CASH_PERCENTAGE = 10  # 10% em USDT
MAX_POSITION_PERCENTAGE = 40  # Máximo 40% por posição
RUN_INTERVAL_MINUTES = 5  # Análise a cada 5 min
```

### 2. Personalização de Pares de Trading

```python
# Foco em Major Coins (Baixo Risco)
BYBIT_TRADING_PAIRS = [
    'BTCUSDT',
    'ETHUSDT',
    'BNBUSDT'
]

# Portfolio Diversificado (Médio Risco)
BYBIT_TRADING_PAIRS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT',
    'ADAUSDT', 'DOTUSDT', 'LINKUSDT',
    'AVAXUSDT', 'MATICUSDT'
]

# Altcoins + DeFi (Alto Risco)
BYBIT_TRADING_PAIRS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT',
    'UNIUSDT', 'AAVEUSDT', 'COMPUSDT',
    'SUSHIUSDT', 'CRVUSDT'
]
```

### 3. Configuração de Prompts da IA

#### Prompt Conservador:
```python
TRADING_PROMPT = """
You are a CONSERVATIVE trading assistant. 
Prioritize capital preservation over profits.
Only recommend BUY when:
- RSI < 50
- Strong uptrend confirmed
- Low volatility
- Confidence > 80%

Recommend SELL when:
- Any sign of trend reversal
- RSI > 60
- Confidence < 70%
"""
```

#### Prompt Agressivo:
```python
TRADING_PROMPT = """
You are an AGGRESSIVE trading assistant.
Look for high-probability momentum plays.
Recommend BUY when:
- Strong momentum signals
- Breaking resistance levels
- High volume confirmation
- Confidence > 60%

Quick profit-taking on 5-10% gains.
"""
```

### 4. Configurações de Horário

#### Trading apenas em horários específicos:
```python
# Em bybit_trading_agent.py, adicione no main():

from datetime import datetime

def is_trading_hours():
    """Define horários de trading"""
    now = datetime.now()
    hour = now.hour
    
    # Trading apenas durante horários de alta liquidez
    # 8h-12h e 14h-18h (UTC)
    return (8 <= hour <= 12) or (14 <= hour <= 18)

# No loop principal:
if not is_trading_hours():
    cprint("😴 Fora do horário de trading - aguardando...", "white", "on_blue")
    time.sleep(3600)  # Espera 1 hora
    continue
```

### 5. Stop Loss e Take Profit Automático

```python
# Adicione na classe BybitTradingAgent:

def check_stop_loss_take_profit(self):
    """Verifica stop loss e take profit para posições abertas"""
    for symbol in BYBIT_TRADING_PAIRS:
        current_value = self.bybit.get_position_value(symbol)
        if current_value > BYBIT_MIN_TRADE_SIZE:
            
            # Pega preço atual
            current_price = self.bybit.get_ticker_price(symbol)
            
            # Aqui você implementaria a lógica de SL/TP
            # baseada no preço de entrada armazenado
```

### 6. Configuração de Notificações

#### Telegram Bot (opcional):
```python
import requests

def send_telegram_alert(message):
    """Envia alerta via Telegram"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        requests.post(url, data=data)

# Use no código:
send_telegram_alert(f"🚀 Trade executado: {symbol} - {action}")
```

### 7. Backup e Logging

```python
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    filename=f'trading_log_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# No código:
logging.info(f"Trade executed: {symbol} - {action} - ${amount}")
```

### 8. Configuração de Múltiplas Estratégias

```python
# Em config.py
STRATEGY_WEIGHTS = {
    'ai_analysis': 0.4,      # 40% peso para análise IA
    'momentum': 0.3,         # 30% peso para momentum
    'mean_reversion': 0.2,   # 20% peso para reversão
    'volume_analysis': 0.1   # 10% peso para volume
}

# Combinar sinais de múltiplas estratégias
def combine_strategies(ai_signal, momentum_signal, mean_rev_signal, volume_signal):
    weighted_score = (
        ai_signal * STRATEGY_WEIGHTS['ai_analysis'] +
        momentum_signal * STRATEGY_WEIGHTS['momentum'] +
        mean_rev_signal * STRATEGY_WEIGHTS['mean_reversion'] +
        volume_signal * STRATEGY_WEIGHTS['volume_analysis']
    )
    return weighted_score
```

### 9. Configuração de Ambiente de Produção

#### Usando Docker:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/main_bybit.py"]
```

#### Usando systemd (Linux):
```ini
[Unit]
Description=Moon Dev Bybit Trading Bot
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/home/trader/Crypto-BOT
ExecStart=/usr/bin/python3 src/main_bybit.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 10. Monitoramento e Alertas

```python
# Métricas para monitorar
MONITORING_METRICS = {
    'daily_pnl': 0,
    'total_trades': 0,
    'win_rate': 0,
    'max_drawdown': 0,
    'sharpe_ratio': 0
}

def calculate_performance_metrics():
    """Calcula métricas de performance"""
    # Implementar cálculo de métricas
    pass

def check_risk_limits():
    """Verifica se limites de risco foram ultrapassados"""
    if MONITORING_METRICS['daily_pnl'] < -500:  # Perda diária > $500
        cprint("🚨 LIMITE DE RISCO ATINGIDO - PARANDO TRADING", "white", "on_red")
        return False
    return True
```

## 🛡️ Checklist de Segurança

- [ ] Limites configurados na Bybit
- [ ] API keys com permissões mínimas
- [ ] Backup das configurações
- [ ] Monitoramento ativo
- [ ] Stop loss configurado
- [ ] Teste com valores pequenos
- [ ] Logs habilitados
- [ ] Alertas configurados

## 📊 Configurações Recomendadas por Perfil

### Iniciante:
- CASH_PERCENTAGE: 50%
- MAX_POSITION_PERCENTAGE: 15%
- RUN_INTERVAL_MINUTES: 60
- Apenas BTC/ETH

### Intermediário:
- CASH_PERCENTAGE: 30%
- MAX_POSITION_PERCENTAGE: 25%
- RUN_INTERVAL_MINUTES: 30
- Top 10 cryptos

### Avançado:
- CASH_PERCENTAGE: 20%
- MAX_POSITION_PERCENTAGE: 35%
- RUN_INTERVAL_MINUTES: 15
- Portfolio diversificado

---
*Lembre-se: Sempre teste suas configurações com valores pequenos primeiro!*