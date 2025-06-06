# 🌙 Moon Dev's Bybit 24/7 Trading Setup

## 🚀 Quick Start

Este sistema permite trading automatizado 24/7 na Bybit usando IA DeepSeek para análise de mercado.

### 1. Configuração das APIs

#### DeepSeek AI API
1. Acesse [https://platform.deepseek.com](https://platform.deepseek.com)
2. Crie uma conta e obtenha sua API key
3. Adicione créditos à sua conta

#### Bybit API
1. Acesse [https://www.bybit.com](https://www.bybit.com)
2. Vá em Account & Security > API Management
3. Crie uma nova API key com permissões:
   - ✅ Read
   - ✅ Trade (Spot)
   - ❌ Withdraw (NÃO habilite para segurança)
4. Configure IP whitelist se possível
5. **IMPORTANTE**: Defina limites de trading na sua conta!

### 2. Instalação

```bash
# Clone o repositório (se ainda não fez)
git clone <repository-url>
cd Crypto-BOT

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas API keys
```

### 3. Configuração do .env

```env
# DeepSeek AI
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Bybit
BYBIT_API_KEY=your-bybit-api-key
BYBIT_API_SECRET=your-bybit-secret
```

### 4. Configuração de Trading

Edite `src/core/config.py` para ajustar:

```python
# Pares de trading
BYBIT_TRADING_PAIRS = [
    'BTCUSDT',
    'ETHUSDT', 
    'SOLUSDT',
    # Adicione mais pares conforme necessário
]

# Gestão de risco
CASH_PERCENTAGE = 20  # % manter em USDT
MAX_POSITION_PERCENTAGE = 30  # % máximo por posição
BYBIT_MAX_POSITION_SIZE = 500  # Tamanho máximo em USDT
```

### 5. Executar o Bot

```bash
# Para trading 24/7 na Bybit
python src/main_bybit.py
```

## 🛡️ Configurações de Segurança

### Limites Recomendados na Bybit:
- **Daily Trading Limit**: Defina um limite diário (ex: $1000)
- **Single Order Limit**: Limite por ordem (ex: $100)
- **IP Whitelist**: Configure se possível
- **2FA**: Sempre habilitado

### Configurações de Risco no Bot:
```python
# Em config.py
CASH_PERCENTAGE = 20  # Sempre manter 20% em cash
MAX_POSITION_PERCENTAGE = 30  # Máximo 30% em uma posição
RUN_INTERVAL_MINUTES = 15  # Frequência de análise
```

## 📊 Como Funciona

1. **Análise de Mercado**: DeepSeek AI analisa dados técnicos
2. **Decisões de Trading**: BUY/SELL/HOLD baseado em:
   - RSI, Moving Averages
   - Volume e momentum
   - Análise de tendência
3. **Gestão de Portfolio**: Aloca capital baseado em confiança
4. **Execução**: Trades automáticos na Bybit
5. **Repetição**: Ciclo a cada 15 minutos

## 🎯 Pares de Trading Suportados

Por padrão, o bot monitora:
- BTCUSDT (Bitcoin)
- ETHUSDT (Ethereum)
- SOLUSDT (Solana)
- ADAUSDT (Cardano)
- DOTUSDT (Polkadot)
- LINKUSDT (Chainlink)
- AVAXUSDT (Avalanche)
- MATICUSDT (Polygon)

## 📈 Monitoramento

O bot exibe em tempo real:
- ✅ Análises da IA
- 📊 Recomendações (BUY/SELL/HOLD)
- 💰 Alocação de portfolio
- 🔄 Execução de trades
- ⚠️ Erros e alertas

## ⚠️ Avisos Importantes

1. **TESTE PRIMEIRO**: Use valores pequenos para testar
2. **MONITORE**: Acompanhe o bot especialmente no início
3. **LIMITES**: Configure limites na Bybit
4. **BACKUP**: Mantenha backup das configurações
5. **RESPONSABILIDADE**: Trading envolve riscos - use por sua conta e risco

## 🔧 Troubleshooting

### Erro de API Key:
- Verifique se as keys estão corretas no .env
- Confirme permissões na Bybit
- Teste conectividade

### Erro de Trading:
- Verifique saldo suficiente
- Confirme limites de trading
- Verifique se o par está ativo

### Erro de IA:
- Verifique créditos DeepSeek
- Teste conectividade com a API

## 📞 Suporte

Para dúvidas sobre o código, abra uma issue no repositório.

**Lembre-se**: Este é um projeto experimental. Trading envolve riscos significativos!

---
*Built with love by Moon Dev 🌙*