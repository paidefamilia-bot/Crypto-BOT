# 🌙 Moon Dev's Autonomous Trading System - Guia Completo

## 🧠 Visão Geral

Este sistema implementa uma estratégia de trading **completamente autônoma** usando LLM (Large Language Model) para análise de mercado. Diferente de sistemas baseados em regras fixas, a IA analisa indicadores técnicos e toma decisões contextuais baseadas em padrões históricos e atuais.

## 🎯 Características Principais

### Análise Autônoma com LLM
- **Sem regras fixas**: A IA não segue regras como "se RSI > 70, então venda"
- **Análise contextual**: Considera estado atual + histórico dos indicadores
- **Decisões adaptativas**: Cada situação é analisada individualmente
- **Confluência de sinais**: Combina múltiplos indicadores para decisões

### Indicadores Técnicos Personalizados

1. **RSI (14 períodos)**
   - Mede força relativa dos movimentos
   - Identifica condições de sobrecompra/sobrevenda

2. **4 Médias Móveis Exponenciais**
   - MME_9: Tendência de curtíssimo prazo
   - MME_21: Tendência de curto prazo
   - MME_50: Tendência de médio prazo
   - MME_200: Tendência de longo prazo

3. **DistanciaMM_Bands (Indicador Personalizado)**
   - Calcula distância percentual do preço para MME_200
   - Aplica Bollinger Bands sobre essa distância
   - Identifica exaustão estatística de movimentos
   - Sinaliza possíveis reversões

## 🚀 Trading em Tempo Real

### Configuração

1. **APIs Necessárias**:
   ```bash
   # No arquivo .env
   DEEPSEEK_API_KEY=sk-your-deepseek-key
   BYBIT_API_KEY=your-bybit-api-key
   BYBIT_API_SECRET=your-bybit-secret
   ```

2. **Teste de Configuração**:
   ```bash
   python test_bybit_setup.py
   ```

3. **Execução**:
   ```bash
   python run_autonomous_trading.py
   ```

### Características do Sistema Real

- **Trading 24/7**: Funciona continuamente
- **Múltiplos pares**: BTC, ETH, SOL, ADA, etc.
- **Gestão de risco**: Limites automáticos de posição
- **Execução automática**: Compra/venda baseada na análise da IA
- **Monitoramento**: Logs detalhados de todas as decisões

## 🧪 Sistema de Backtest

### Uso Básico

```bash
# Backtest com um arquivo
python autonomous_backtest.py BTC-5m-30wks-data.csv

# Backtest com múltiplos arquivos
python autonomous_backtest.py BTC-5m-30wks-data.csv ETH-1h-12wks-data.csv

# Backtest com configurações personalizadas
python autonomous_backtest.py BTC-5m-30wks-data.csv --capital 50000 --confidence-min 70 --interval 12
```

### Parâmetros Disponíveis

- `--capital`: Capital inicial (padrão: $10,000)
- `--interval`: Intervalo de análise em períodos (padrão: 24)
- `--confidence-min`: Confiança mínima para trades (padrão: 60%)
- `--output-prefix`: Prefixo para arquivos de saída

### Formato dos Dados CSV

```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,45000.0,45100.0,44900.0,45050.0,1234567.89
2024-01-01 00:05:00,45050.0,45200.0,45000.0,45150.0,987654.32
...
```

**Colunas obrigatórias**:
- `timestamp`: Data/hora (YYYY-MM-DD HH:MM:SS)
- `open`, `high`, `low`, `close`: Preços OHLC
- `volume`: Volume negociado

## 🎯 Como a IA Toma Decisões

### Processo de Análise

1. **Coleta de Dados**:
   - Valores atuais de todos os indicadores
   - Histórico dos últimos 1, 3, 5, 10, 20 períodos
   - Mudanças recentes e momentum

2. **Análise Contextual**:
   - Avalia confluência entre indicadores
   - Identifica padrões e divergências
   - Considera força da tendência atual
   - Analisa sinais de exaustão estatística

3. **Tomada de Decisão**:
   - **BUY**: Quando identifica oportunidade de alta
   - **SELL**: Quando identifica necessidade de saída
   - **HOLD**: Quando não há sinal claro
   - **Confiança**: Nível de certeza (0-100%)

### Exemplos de Análise da IA

**Cenário Bullish**:
```
RSI: 45 (neutro, mas subindo)
MME: Alinhamento bullish (9>21>50>200)
DistanciaMM: +2.5% (acima da média, mas dentro das bandas)
Histórico: RSI vinha de 35, tendência se fortalecendo
Decisão: BUY (confiança: 75%)
```

**Cenário de Exaustão**:
```
RSI: 78 (sobrecomprado)
MME: Ainda bullish, mas preço muito acima da MME_9
DistanciaMM: +8.2% (acima da banda superior - exaustão)
Histórico: Movimento parabólico nos últimos períodos
Decisão: SELL (confiança: 85%)
```

## 📊 Interpretação dos Resultados

### Métricas do Backtest

- **Retorno Total**: Performance geral da estratégia
- **Win Rate**: Percentual de trades lucrativos
- **Sharpe Ratio**: Retorno ajustado ao risco
- **Max Drawdown**: Maior perda consecutiva
- **Total de Trades**: Frequência de operações

### Avaliação da Performance

**Excelente** (>10% retorno):
- Estratégia muito lucrativa
- Considere usar com capital real

**Bom** (0-10% retorno):
- Estratégia lucrativa
- Teste com valores menores primeiro

**Neutro** (-5% a 0%):
- Performance marginal
- Ajuste parâmetros ou período

**Ruim** (<-5%):
- Estratégia não funcionou no período
- Revise configurações

## ⚠️ Gestão de Risco

### Configurações Recomendadas

**Iniciante**:
```python
CASH_PERCENTAGE = 50%        # 50% sempre em cash
MAX_POSITION_PERCENTAGE = 15%  # Máximo 15% por posição
CONFIDENCE_MIN = 70%         # Só opera com alta confiança
```

**Intermediário**:
```python
CASH_PERCENTAGE = 30%        # 30% em cash
MAX_POSITION_PERCENTAGE = 25%  # Máximo 25% por posição
CONFIDENCE_MIN = 60%         # Confiança moderada
```

**Avançado**:
```python
CASH_PERCENTAGE = 20%        # 20% em cash
MAX_POSITION_PERCENTAGE = 35%  # Máximo 35% por posição
CONFIDENCE_MIN = 55%         # Confiança mais baixa
```

### Limites na Exchange

**Sempre configure na Bybit**:
- Limite diário de trading
- Limite por ordem individual
- IP whitelist (se possível)
- 2FA sempre habilitado

## 🔧 Troubleshooting

### Problemas Comuns

**Erro de API**:
- Verifique keys no .env
- Confirme permissões na Bybit
- Teste conectividade

**Poucos trades no backtest**:
- Reduza `--confidence-min`
- Diminua `--interval`
- Verifique qualidade dos dados

**Performance ruim**:
- Teste diferentes períodos
- Ajuste parâmetros de risco
- Verifique se dados têm qualidade

### Logs e Debugging

O sistema gera arquivos CSV detalhados:
- `backtest_trades_YYYYMMDD_HHMMSS.csv`: Todos os trades
- `backtest_portfolio_YYYYMMDD_HHMMSS.csv`: Evolução do portfolio
- `backtest_decisions_YYYYMMDD_HHMMSS.csv`: Todas as decisões da IA

## 💡 Dicas de Uso

### Para Backtest

1. **Use dados de qualidade**: Mínimo 500 velas, sem gaps
2. **Teste múltiplos períodos**: Bull market, bear market, sideways
3. **Varie os parâmetros**: Teste diferentes configurações
4. **Analise os logs**: Entenda as decisões da IA

### Para Trading Real

1. **Comece pequeno**: Use valores baixos inicialmente
2. **Monitore ativamente**: Especialmente nas primeiras horas
3. **Configure limites**: Na exchange e no bot
4. **Mantenha logs**: Para análise posterior

## 📈 Próximos Passos

1. **Execute backtest** com seus dados históricos
2. **Analise resultados** e ajuste parâmetros
3. **Teste em ambiente real** com valores pequenos
4. **Monitore performance** e faça ajustes
5. **Escale gradualmente** conforme ganha confiança

---

**⚠️ AVISO IMPORTANTE**: Trading envolve riscos significativos. Este sistema é experimental e não garante lucros. Use sempre gestão de risco adequada e nunca invista mais do que pode perder.

*Built with love by Moon Dev 🌙*