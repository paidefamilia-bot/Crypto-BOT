# 📊 Dados Históricos para Backtest

## Formato dos Arquivos CSV

Os arquivos CSV devem ter a seguinte estrutura:

```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,45000.0,45100.0,44900.0,45050.0,1234567.89
2024-01-01 00:05:00,45050.0,45200.0,45000.0,45150.0,987654.32
...
```

### Colunas Obrigatórias:
- **timestamp**: Data e hora no formato YYYY-MM-DD HH:MM:SS
- **open**: Preço de abertura
- **high**: Preço máximo
- **low**: Preço mínimo  
- **close**: Preço de fechamento
- **volume**: Volume negociado

## 🔧 Formatos Suportados

O sistema detecta automaticamente diferentes formatos de CSV:

### Nomes de Colunas Aceitos:
- **Timestamp**: `timestamp`, `time`, `datetime`, `date`, `Date`, `Time`, `unix`
- **Open**: `open`, `Open`, `OPEN`, `o`, `Open Price`
- **High**: `high`, `High`, `HIGH`, `h`, `High Price`
- **Low**: `low`, `Low`, `LOW`, `l`, `Low Price`
- **Close**: `close`, `Close`, `CLOSE`, `c`, `price`, `Price`, `Close Price`
- **Volume**: `volume`, `Volume`, `VOLUME`, `vol`, `Vol`, `v`, `Volume USD`

### Conversões Automáticas:
- ✅ **Unix Timestamp**: Converte automaticamente (segundos ou milissegundos)
- ✅ **Apenas Close**: Cria OHLC sintético a partir do preço de fechamento
- ✅ **Sem Volume**: Gera volume sintético
- ✅ **Sem Timestamp**: Usa índice para criar timestamps
- ✅ **Diferentes Capitalizações**: Detecta maiúsculas/minúsculas

### Exemplos de Nomes de Arquivo:
- `BTC-5m-30wks-data.csv` (Bitcoin, 5 minutos, 30 semanas)
- `ETH-1h-12wks-data.csv` (Ethereum, 1 hora, 12 semanas)
- `SOL-15m-8wks-data.csv` (Solana, 15 minutos, 8 semanas)

## Como Usar

### 🔍 Teste o Formato do Seu CSV
```bash
# Verifica se seu CSV é compatível
python test_csv_format.py ETH-1d-1000wks-data.csv
python test_csv_format.py /caminho/completo/para/arquivo.csv
```

### 🔄 Converta Formatos Incompatíveis
```bash
# Converte automaticamente para formato padrão
python convert_csv_format.py ETH-1d-1000wks-data.csv
python convert_csv_format.py dados.csv dados_convertidos.csv
```

### 🧪 Execute o Backtest
```bash
# Backtest com arquivo específico
python autonomous_backtest.py BTC-5m-30wks-data.csv

# Backtest com múltiplos arquivos
python autonomous_backtest.py BTC-5m-30wks-data.csv ETH-1h-12wks-data.csv

# Backtest com configurações personalizadas
python autonomous_backtest.py BTC-5m-30wks-data.csv --capital 50000 --confidence-min 70
```

## Fontes de Dados Recomendadas

1. **Binance API**: Para dados históricos gratuitos
2. **CoinGecko**: Para dados de múltiplas exchanges
3. **Yahoo Finance**: Para dados mais antigos
4. **TradingView**: Exportação manual de dados

## Preparação dos Dados

Certifique-se de que:
- Os dados estão ordenados cronologicamente
- Não há gaps significativos nos dados
- O volume está em formato numérico
- As datas estão no fuso horário correto (UTC recomendado)