"""
🌙 Moon Dev's Autonomous Trading Backtest
Backtest system for LLM-based autonomous trading strategy
Built with love by Moon Dev 🚀
"""

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import openai
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from termcolor import colored, cprint
from dotenv import load_dotenv

from src.indicators.custom_indicators import TechnicalIndicators, create_autonomous_llm_prompt

# Load environment variables
load_dotenv()

class AutonomousBacktest:
    def __init__(self, initial_capital=10000):
        """
        Initialize backtest system
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            cprint("⚠️ DEEPSEEK_API_KEY não encontrada! Usando modo simulado.", "white", "on_yellow")
            cprint("💡 Para usar a LLM real, configure: export DEEPSEEK_API_KEY=sua_chave", "white", "on_cyan")
            self.client = None
            self.simulation_mode = True
        else:
            # Initialize DeepSeek client
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            self.simulation_mode = False
        
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # {symbol: {'quantity': float, 'avg_price': float}}
        self.trade_history = []
        self.portfolio_history = []
        self.decisions_history = []
        
        cprint("🧪 Moon Dev's Autonomous Backtest System initialized!", "white", "on_blue")
        cprint(f"💰 Capital inicial: ${initial_capital:,.2f}", "white", "on_green")
    
    def detect_and_fix_csv_format(self, df):
        """
        Detecta e corrige automaticamente diferentes formatos de CSV
        """
        cprint("🔍 Detectando formato do CSV...", "white", "on_blue")
        
        # Mostra as primeiras colunas para debug
        print(f"Colunas encontradas: {list(df.columns)}")
        
        # Mapas de colunas comuns
        column_mappings = {
            # Formato padrão
            'timestamp': ['timestamp', 'time', 'datetime', 'date', 'Date', 'Time', 'Timestamp'],
            'open': ['open', 'Open', 'OPEN', 'o'],
            'high': ['high', 'High', 'HIGH', 'h'],
            'low': ['low', 'Low', 'LOW', 'l'],
            'close': ['close', 'Close', 'CLOSE', 'c', 'price', 'Price'],
            'volume': ['volume', 'Volume', 'VOLUME', 'vol', 'Vol', 'v']
        }
        
        # Se não tem timestamp, tenta usar index como timestamp
        if not any(col in df.columns for col in column_mappings['timestamp']):
            cprint("⚠️ Coluna de timestamp não encontrada, usando índice", "white", "on_yellow")
            # Cria timestamp baseado no índice (assumindo dados diários)
            start_date = pd.Timestamp('2020-01-01')
            df['timestamp'] = [start_date + pd.Timedelta(days=i) for i in range(len(df))]
        
        # Mapeia colunas para formato padrão
        new_df = df.copy()
        for standard_name, possible_names in column_mappings.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    if standard_name != possible_name:
                        new_df[standard_name] = df[possible_name]
                        cprint(f"✅ Mapeado: {possible_name} → {standard_name}", "white", "on_green")
                    break
        
        # Se ainda falta volume, cria volume sintético
        if 'volume' not in new_df.columns:
            cprint("⚠️ Volume não encontrado, criando volume sintético", "white", "on_yellow")
            new_df['volume'] = 1000000  # Volume fixo
        
        # Verifica se temos pelo menos OHLC
        ohlc_cols = ['open', 'high', 'low', 'close']
        missing_ohlc = [col for col in ohlc_cols if col not in new_df.columns]
        
        if missing_ohlc:
            # Se só temos close/price, cria OHLC sintético
            if 'close' in new_df.columns:
                cprint("⚠️ Criando OHLC sintético a partir do preço de fechamento", "white", "on_yellow")
                new_df['open'] = new_df['close'].shift(1).fillna(new_df['close'].iloc[0])
                new_df['high'] = new_df[['open', 'close']].max(axis=1) * 1.001  # +0.1%
                new_df['low'] = new_df[['open', 'close']].min(axis=1) * 0.999   # -0.1%
            else:
                raise ValueError(f"Não foi possível criar OHLC. Colunas ausentes: {missing_ohlc}")
        
        # Remove colunas desnecessárias (mantém apenas as padronizadas)
        standard_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        columns_to_keep = [col for col in standard_columns if col in new_df.columns]
        new_df = new_df[columns_to_keep].copy()
        
        cprint(f"✅ Formato detectado e corrigido: {len(new_df)} linhas", "white", "on_green")
        return new_df
    
    def load_historical_data_from_csv(self, csv_file_path):
        """
        Carrega dados históricos de arquivo CSV
        """
        try:
            cprint(f"📊 Carregando dados de {csv_file_path}...", "white", "on_blue")
            
            # Verifica se arquivo existe
            if not os.path.exists(csv_file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {csv_file_path}")
            
            # Carrega CSV
            df = pd.read_csv(csv_file_path)
            
            # Detecta formato do CSV automaticamente
            df = self.detect_and_fix_csv_format(df)
            
            # Verifica colunas obrigatórias após conversão
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Colunas obrigatórias ausentes após conversão: {missing_columns}")
            
            # Converte timestamp para datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Ordena por timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Converte colunas numéricas
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove linhas com NaN
            df = df.dropna().reset_index(drop=True)
            
            # Validações básicas
            if len(df) < 500:
                cprint(f"⚠️ Aviso: Poucos dados ({len(df)} velas). Recomendado: >500", "white", "on_yellow")
            
            # Verifica consistência OHLC
            invalid_ohlc = df[(df['high'] < df['low']) | 
                             (df['high'] < df['open']) | 
                             (df['high'] < df['close']) |
                             (df['low'] > df['open']) | 
                             (df['low'] > df['close'])]
            
            if len(invalid_ohlc) > 0:
                cprint(f"⚠️ Encontradas {len(invalid_ohlc)} velas com OHLC inconsistente", "white", "on_yellow")
                # Corrige automaticamente
                df['high'] = df[['open', 'high', 'low', 'close']].max(axis=1)
                df['low'] = df[['open', 'high', 'low', 'close']].min(axis=1)
            
            # Extrai símbolo do nome do arquivo
            filename = os.path.basename(csv_file_path)
            if filename.startswith('BTC'):
                symbol = 'BTCUSDT'
            elif filename.startswith('ETH'):
                symbol = 'ETHUSDT'
            elif filename.startswith('SOL'):
                symbol = 'SOLUSDT'
            else:
                # Tenta extrair do nome do arquivo
                symbol = filename.split('-')[0].upper() + 'USDT'
            
            # Informações do dataset
            start_date = df['timestamp'].min()
            end_date = df['timestamp'].max()
            duration = end_date - start_date
            
            cprint(f"✅ Dados carregados com sucesso!", "white", "on_green")
            cprint(f"📊 Símbolo detectado: {symbol}", "white", "on_cyan")
            cprint(f"📅 Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}", "white", "on_cyan")
            cprint(f"⏰ Duração: {duration.days} dias ({len(df)} velas)", "white", "on_cyan")
            cprint(f"💰 Preço inicial: ${df.iloc[0]['close']:.2f}", "white", "on_cyan")
            cprint(f"💰 Preço final: ${df.iloc[-1]['close']:.2f}", "white", "on_cyan")
            
            return df, symbol
            
        except Exception as e:
            cprint(f"❌ Erro carregando dados: {str(e)}", "white", "on_red")
            raise
    
    def prepare_data_with_indicators(self, df):
        """
        Prepara dados com todos os indicadores necessários
        """
        # Calcula todos os indicadores
        df = TechnicalIndicators.calculate_all_indicators(df, 'close')
        
        # Remove linhas com NaN (início dos dados onde indicadores não podem ser calculados)
        df = df.dropna().reset_index(drop=True)
        
        return df
    
    def autonomous_analysis_for_backtest(self, symbol, market_data, current_idx):
        """
        Análise autônoma para backtest (similar ao trading real, mas otimizada)
        """
        try:
            # Pega dados até o índice atual (simula dados disponíveis no momento)
            available_data = market_data.iloc[:current_idx+1].copy()
            
            if len(available_data) < 220:  # Precisa de dados suficientes
                return "HOLD", 0, "Dados insuficientes para análise"
            
            # Prepara dados para análise
            analysis_data = TechnicalIndicators.prepare_llm_analysis_data(available_data)
            if not analysis_data:
                return "HOLD", 0, "Falha preparando dados para análise"
            
            # Cria prompt simplificado para backtest (mais eficiente)
            base_prompt = create_autonomous_llm_prompt()
            
            # Dados resumidos para a LLM
            current = analysis_data['current_indicators']
            data_summary = f"""
BACKTEST ANALYSIS - {symbol}
Preço: ${analysis_data['symbol_info']['current_price']}

INDICADORES:
• RSI: {current['RSI']['value']}
• MME_9: ${current['MME_9']['value']} (preço {current['MME_9']['price_position']})
• MME_21: ${current['MME_21']['value']} (preço {current['MME_21']['price_position']})
• MME_50: ${current['MME_50']['value']} (preço {current['MME_50']['price_position']})
• MME_200: ${current['MME_200']['value']} (preço {current['MME_200']['price_position']})

• DistanciaMM: {current['DistanciaMM_Bands']['distancia_percentual']}%
• Banda Superior: {current['DistanciaMM_Bands']['banda_superior']}%
• Banda Inferior: {current['DistanciaMM_Bands']['banda_inferior']}%
• Exaustão Bullish: {current['DistanciaMM_Bands']['exaustao_bullish']}
• Exaustão Bearish: {current['DistanciaMM_Bands']['exaustao_bearish']}

• Alinhamento Bullish: {current['contexto_tendencia']['alinhamento_bullish']}
• Alinhamento Bearish: {current['contexto_tendencia']['alinhamento_bearish']}

HISTÓRICO (últimos 5 períodos):
"""
            
            # Adiciona dados históricos resumidos
            for period in [1, 3, 5]:
                if f'{period}_periodos_atras' in analysis_data['historical_analysis']:
                    hist = analysis_data['historical_analysis'][f'{period}_periodos_atras']
                    data_summary += f"• {period}p atrás: RSI={hist['RSI']}, Dist={hist['DistanciaMM']}%, Bull={hist['alinhamento_bullish']}\n"
            
            if self.simulation_mode:
                # Análise simulada baseada em indicadores técnicos
                decision, confidence, reasoning = self.simulate_llm_analysis(analysis_data)
            else:
                # Análise com LLM real
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": base_prompt},
                        {"role": "user", "content": data_summary}
                    ],
                    max_tokens=800,
                    temperature=0.2  # Baixa temperatura para consistência
                )
                
                analysis_result = response.choices[0].message.content
                lines = analysis_result.split('\n')
                decision = lines[0].strip().upper() if lines else "HOLD"
                
                if decision not in ['BUY', 'SELL', 'HOLD']:
                    decision = "HOLD"
                
                # Extrai confiança
                confidence = 50
                for line in lines:
                    if any(word in line.lower() for word in ['confiança', 'confidence']):
                        try:
                            numbers = [int(s) for s in line.split() if s.isdigit()]
                            if numbers:
                                confidence = min(max(numbers[0], 0), 100)
                        except:
                            pass
                
                reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else "Análise resumida"
            
            return decision, confidence, reasoning
            
        except Exception as e:
            print(f"❌ Erro na análise: {str(e)}")
            return "HOLD", 0, f"Erro: {str(e)}"
    
    def simulate_llm_analysis(self, analysis_data):
        """
        Simula análise da LLM usando indicadores técnicos
        """
        try:
            current = analysis_data['current_indicators']
            
            # Extrai valores dos indicadores
            rsi = current['RSI']['value']
            distancia_mm = current['DistanciaMM_Bands']['distancia_percentual']
            exaustao_bullish = current['DistanciaMM_Bands']['exaustao_bullish']
            exaustao_bearish = current['DistanciaMM_Bands']['exaustao_bearish']
            alinhamento_bullish = current['contexto_tendencia']['alinhamento_bullish']
            alinhamento_bearish = current['contexto_tendencia']['alinhamento_bearish']
            
            # Lógica de decisão simulada
            decision = "HOLD"
            confidence = 50
            reasoning = "Análise simulada baseada em indicadores técnicos"
            
            # Sinais de compra
            buy_signals = 0
            if rsi < 30:  # RSI sobrevenda
                buy_signals += 2
            elif rsi < 40:
                buy_signals += 1
            
            if exaustao_bearish:  # Exaustão bearish
                buy_signals += 2
            
            if alinhamento_bullish:  # Alinhamento bullish das MME
                buy_signals += 1
            
            if distancia_mm < -2:  # Preço muito abaixo da média
                buy_signals += 1
            
            # Sinais de venda
            sell_signals = 0
            if rsi > 70:  # RSI sobrecompra
                sell_signals += 2
            elif rsi > 60:
                sell_signals += 1
            
            if exaustao_bullish:  # Exaustão bullish
                sell_signals += 2
            
            if alinhamento_bearish:  # Alinhamento bearish das MME
                sell_signals += 1
            
            if distancia_mm > 2:  # Preço muito acima da média
                sell_signals += 1
            
            # Determina decisão
            if buy_signals >= 3 and buy_signals > sell_signals:
                decision = "BUY"
                confidence = min(50 + (buy_signals * 10), 85)
                reasoning = f"Sinais de compra: RSI={rsi:.1f}, DistMM={distancia_mm:.1f}%, ExaustãoBear={exaustao_bearish}, AlinhBull={alinhamento_bullish}"
            elif sell_signals >= 3 and sell_signals > buy_signals:
                decision = "SELL"
                confidence = min(50 + (sell_signals * 10), 85)
                reasoning = f"Sinais de venda: RSI={rsi:.1f}, DistMM={distancia_mm:.1f}%, ExaustãoBull={exaustao_bullish}, AlinhBear={alinhamento_bearish}"
            else:
                decision = "HOLD"
                confidence = 40
                reasoning = f"Sinais mistos: Buy={buy_signals}, Sell={sell_signals}, RSI={rsi:.1f}"
            
            return decision, confidence, reasoning
            
        except Exception as e:
            return "HOLD", 0, f"Erro na simulação: {str(e)}"
    
    def execute_backtest_trade(self, symbol, decision, confidence, price, timestamp):
        """
        Executa trade no backtest
        """
        if confidence < 60:  # Só opera com confiança alta
            return False
        
        commission = 0.001  # 0.1% de comissão
        min_trade_size = 100  # Mínimo $100 por trade
        
        if decision == "BUY":
            # Calcula tamanho da posição baseado na confiança
            max_position_size = self.current_capital * 0.2  # Máximo 20% do capital
            position_size = max_position_size * (confidence / 100) * 0.5
            
            if position_size >= min_trade_size:
                # Executa compra
                quantity = position_size / price
                cost = position_size * (1 + commission)
                
                if cost <= self.current_capital:
                    self.current_capital -= cost
                    
                    if symbol in self.positions:
                        # Adiciona à posição existente
                        old_qty = self.positions[symbol]['quantity']
                        old_avg = self.positions[symbol]['avg_price']
                        new_qty = old_qty + quantity
                        new_avg = ((old_qty * old_avg) + (quantity * price)) / new_qty
                        
                        self.positions[symbol] = {
                            'quantity': new_qty,
                            'avg_price': new_avg
                        }
                    else:
                        # Nova posição
                        self.positions[symbol] = {
                            'quantity': quantity,
                            'avg_price': price
                        }
                    
                    # Registra trade
                    self.trade_history.append({
                        'timestamp': timestamp,
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': quantity,
                        'price': price,
                        'value': position_size,
                        'commission': position_size * commission,
                        'confidence': confidence
                    })
                    
                    return True
        
        elif decision == "SELL" and symbol in self.positions:
            # Vende toda a posição
            quantity = self.positions[symbol]['quantity']
            value = quantity * price
            commission_cost = value * commission
            net_value = value - commission_cost
            
            self.current_capital += net_value
            
            # Registra trade
            self.trade_history.append({
                'timestamp': timestamp,
                'symbol': symbol,
                'action': 'SELL',
                'quantity': quantity,
                'price': price,
                'value': value,
                'commission': commission_cost,
                'confidence': confidence
            })
            
            # Remove posição
            del self.positions[symbol]
            return True
        
        return False
    
    def calculate_portfolio_value(self, current_prices):
        """
        Calcula valor total do portfolio
        """
        total_value = self.current_capital
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position_value = position['quantity'] * current_prices[symbol]
                total_value += position_value
        
        return total_value
    
    def run_backtest_from_csv(self, csv_files, analysis_interval=24, confidence_min=60):
        """
        Executa backtest completo usando arquivos CSV
        """
        cprint(f"🚀 Iniciando backtest com dados CSV", "white", "on_blue")
        cprint(f"📊 Arquivos: {', '.join(csv_files)}", "white", "on_cyan")
        cprint(f"⏰ Análise a cada {analysis_interval} períodos", "white", "on_cyan")
        cprint(f"🎯 Confiança mínima: {confidence_min}%", "white", "on_cyan")
        
        # Carrega dados de todos os arquivos CSV
        all_data = {}
        symbols = []
        
        for csv_file in csv_files:
            try:
                data, symbol = self.load_historical_data_from_csv(csv_file)
                processed_data = self.prepare_data_with_indicators(data)
                all_data[symbol] = processed_data
                symbols.append(symbol)
                
                cprint(f"✅ {symbol}: {len(processed_data)} velas processadas", "white", "on_green")
                
            except Exception as e:
                cprint(f"❌ Erro processando {csv_file}: {str(e)}", "white", "on_red")
                continue
        
        if not all_data:
            raise ValueError("Nenhum arquivo CSV foi carregado com sucesso!")
        
        # Encontra o menor dataset para sincronizar
        min_length = min(len(data) for data in all_data.values())
        cprint(f"📏 Usando {min_length} velas para sincronização", "white", "on_blue")
        
        # Atualiza confiança mínima
        self.confidence_min = confidence_min
        
        # Executa backtest
        trades_executed = 0
        for i in range(220, min_length, analysis_interval):  # Começa após ter dados suficientes
            # Pega timestamp do primeiro dataset
            current_timestamp = list(all_data.values())[0].iloc[i]['timestamp']
            current_prices = {}
            
            # Pega preços atuais de todos os símbolos
            for symbol in symbols:
                current_prices[symbol] = all_data[symbol].iloc[i]['close']
            
            # Calcula valor do portfolio
            portfolio_value = self.calculate_portfolio_value(current_prices)
            self.portfolio_history.append({
                'timestamp': current_timestamp,
                'portfolio_value': portfolio_value,
                'cash': self.current_capital,
                'positions_value': portfolio_value - self.current_capital
            })
            
            # Análise para cada símbolo
            for symbol in symbols:
                try:
                    decision, confidence, reasoning = self.autonomous_analysis_for_backtest(
                        symbol, all_data[symbol], i
                    )
                    
                    # Debug: mostra algumas decisões para verificar
                    if i % (analysis_interval * 50) == 0:  # A cada 50 análises
                        print(f"🔍 Debug - {symbol}: {decision} (conf: {confidence}%) - {reasoning[:100]}...")
                    
                    if decision and decision != "HOLD" and confidence >= confidence_min:
                        # Registra decisão
                        self.decisions_history.append({
                            'timestamp': current_timestamp,
                            'symbol': symbol,
                            'decision': decision,
                            'confidence': confidence,
                            'price': current_prices[symbol],
                            'reasoning': reasoning[:200] + "..." if len(reasoning) > 200 else reasoning
                        })
                        
                        # Executa trade
                        executed = self.execute_backtest_trade(
                            symbol, decision, confidence, 
                            current_prices[symbol], current_timestamp
                        )
                        
                        if executed:
                            trades_executed += 1
                            print(f"✅ {current_timestamp.strftime('%Y-%m-%d %H:%M')} - {symbol}: {decision} @ ${current_prices[symbol]:.2f} (conf: {confidence}%)")
                
                except Exception as e:
                    print(f"❌ Erro analisando {symbol} em {current_timestamp}: {str(e)}")
            
            # Progress update
            if i % (analysis_interval * 20) == 0:
                progress = (i / min_length) * 100
                print(f"📈 Progresso: {progress:.1f}% - Portfolio: ${portfolio_value:,.2f} - Trades: {trades_executed}")
        
        # Fecha todas as posições no final
        final_prices = {symbol: all_data[symbol].iloc[-1]['close'] for symbol in symbols}
        final_portfolio_value = self.calculate_portfolio_value(final_prices)
        
        cprint(f"\n🏁 Backtest concluído!", "white", "on_green")
        cprint(f"📊 Total de trades executados: {trades_executed}", "white", "on_cyan")
        
        return self.generate_backtest_report(final_portfolio_value)
    
    def generate_backtest_report(self, final_value):
        """
        Gera relatório completo do backtest
        """
        # Métricas básicas
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        total_trades = len(self.trade_history)
        
        # Análise de trades
        if self.trade_history:
            trades_df = pd.DataFrame(self.trade_history)
            buy_trades = trades_df[trades_df['action'] == 'BUY']
            sell_trades = trades_df[trades_df['action'] == 'SELL']
            
            # Calcula P&L por trade
            pnl_trades = []
            for _, sell in sell_trades.iterrows():
                symbol = sell['symbol']
                # Encontra compras correspondentes (simplificado)
                symbol_buys = buy_trades[buy_trades['symbol'] == symbol]
                if not symbol_buys.empty:
                    avg_buy_price = symbol_buys['price'].mean()
                    pnl = (sell['price'] - avg_buy_price) / avg_buy_price * 100
                    pnl_trades.append(pnl)
            
            win_rate = len([p for p in pnl_trades if p > 0]) / len(pnl_trades) * 100 if pnl_trades else 0
            avg_win = np.mean([p for p in pnl_trades if p > 0]) if pnl_trades else 0
            avg_loss = np.mean([p for p in pnl_trades if p < 0]) if pnl_trades else 0
        else:
            # Sem trades executados
            buy_trades = pd.DataFrame()
            sell_trades = pd.DataFrame()
            pnl_trades = []
            win_rate = 0
            avg_win = 0
            avg_loss = 0
        
        # Portfolio performance
        portfolio_df = pd.DataFrame(self.portfolio_history)
        if not portfolio_df.empty:
            portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
            sharpe_ratio = portfolio_df['returns'].mean() / portfolio_df['returns'].std() * np.sqrt(365*24) if portfolio_df['returns'].std() > 0 else 0
            max_drawdown = ((portfolio_df['portfolio_value'] / portfolio_df['portfolio_value'].cummax()) - 1).min() * 100
        else:
            sharpe_ratio = 0
            max_drawdown = 0
        
        # Relatório
        report = f"""
🌙 MOON DEV'S AUTONOMOUS TRADING BACKTEST REPORT

📊 PERFORMANCE GERAL:
• Capital Inicial: ${self.initial_capital:,.2f}
• Capital Final: ${final_value:,.2f}
• Retorno Total: {total_return:.2f}%
• Sharpe Ratio: {sharpe_ratio:.2f}
• Max Drawdown: {max_drawdown:.2f}%

📈 ESTATÍSTICAS DE TRADING:
• Total de Trades: {total_trades}
• Trades Lucrativos: {len([p for p in pnl_trades if p > 0])}
• Win Rate: {win_rate:.1f}%
• Ganho Médio: {avg_win:.2f}%
• Perda Média: {avg_loss:.2f}%

💰 POSIÇÕES FINAIS:
"""
        
        for symbol, position in self.positions.items():
            report += f"• {symbol}: {position['quantity']:.6f} @ ${position['avg_price']:.2f}\n"
        
        if not self.positions:
            report += "• Nenhuma posição aberta\n"
        
        report += f"\n💵 Cash Final: ${self.current_capital:,.2f}"
        
        print(report)
        
        # Salva dados detalhados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.trade_history:
            trades_df.to_csv(f'backtest_trades_{timestamp}.csv', index=False)
            cprint(f"💾 Trades salvos em backtest_trades_{timestamp}.csv", "white", "on_green")
        
        if self.portfolio_history:
            portfolio_df.to_csv(f'backtest_portfolio_{timestamp}.csv', index=False)
            cprint(f"💾 Portfolio salvos em backtest_portfolio_{timestamp}.csv", "white", "on_green")
        
        if self.decisions_history:
            decisions_df = pd.DataFrame(self.decisions_history)
            decisions_df.to_csv(f'backtest_decisions_{timestamp}.csv', index=False)
            cprint(f"💾 Decisões salvas em backtest_decisions_{timestamp}.csv", "white", "on_green")
        
        return {
            'final_value': final_value,
            'total_return': total_return,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }

def main():
    """
    Executa backtest com argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="🌙 Moon Dev's Autonomous Trading Backtest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python autonomous_backtest.py BTC-5m-30wks-data.csv
  python autonomous_backtest.py BTC-5m-30wks-data.csv ETH-1h-12wks-data.csv
  python autonomous_backtest.py BTC-5m-30wks-data.csv --capital 50000 --confidence-min 70
  python autonomous_backtest.py data/BTC-5m-30wks-data.csv --interval 12 --capital 25000
        """
    )
    
    parser.add_argument(
        'csv_files', 
        nargs='+', 
        help='Arquivos CSV com dados históricos (ex: BTC-5m-30wks-data.csv)'
    )
    
    parser.add_argument(
        '--capital', 
        type=float, 
        default=10000,
        help='Capital inicial em USD (padrão: 10000)'
    )
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=24,
        help='Intervalo de análise em períodos (padrão: 24)'
    )
    
    parser.add_argument(
        '--confidence-min', 
        type=int, 
        default=60,
        help='Confiança mínima para executar trades (padrão: 60%%)'
    )
    
    parser.add_argument(
        '--output-prefix', 
        type=str, 
        default='',
        help='Prefixo para arquivos de saída (ex: "test_")'
    )
    
    args = parser.parse_args()
    
    # Validações
    if args.capital <= 0:
        cprint("❌ Capital deve ser maior que zero", "white", "on_red")
        return
    
    if args.interval <= 0:
        cprint("❌ Intervalo deve ser maior que zero", "white", "on_red")
        return
    
    if not (0 <= args.confidence_min <= 100):
        cprint("❌ Confiança mínima deve estar entre 0 e 100", "white", "on_red")
        return
    
    # Verifica se arquivos existem
    missing_files = []
    for csv_file in args.csv_files:
        if not os.path.exists(csv_file):
            # Tenta encontrar na pasta data/
            data_path = os.path.join('data', csv_file)
            if os.path.exists(data_path):
                # Substitui pelo caminho correto
                idx = args.csv_files.index(csv_file)
                args.csv_files[idx] = data_path
            else:
                missing_files.append(csv_file)
    
    if missing_files:
        cprint(f"❌ Arquivos não encontrados: {', '.join(missing_files)}", "white", "on_red")
        cprint("💡 Verifique se os arquivos estão no diretório atual ou na pasta 'data/'", "white", "on_yellow")
        return
    
    # Exibe configurações
    cprint("🧪 MOON DEV'S AUTONOMOUS TRADING BACKTEST", "white", "on_blue")
    cprint("🧠 Estratégia LLM Autônoma com Indicadores Personalizados", "white", "on_green")
    
    print("\n" + "="*60)
    print("CONFIGURAÇÕES DO BACKTEST:")
    print(f"💰 Capital Inicial: ${args.capital:,.2f}")
    print(f"📊 Arquivos CSV: {len(args.csv_files)}")
    for i, file in enumerate(args.csv_files, 1):
        print(f"   {i}. {file}")
    print(f"⏰ Intervalo de Análise: {args.interval} períodos")
    print(f"🎯 Confiança Mínima: {args.confidence_min}%")
    if args.output_prefix:
        print(f"📁 Prefixo de Saída: {args.output_prefix}")
    print("="*60)
    
    try:
        # Inicializa backtest
        backtest = AutonomousBacktest(args.capital)
        
        # Executa backtest
        results = backtest.run_backtest_from_csv(
            csv_files=args.csv_files,
            analysis_interval=args.interval,
            confidence_min=args.confidence_min
        )
        
        # Resultados finais
        cprint("\n🎉 BACKTEST CONCLUÍDO COM SUCESSO!", "white", "on_green")
        print("\n" + "="*50)
        print("RESUMO DOS RESULTADOS:")
        print(f"📈 Retorno Total: {results['total_return']:.2f}%")
        print(f"🎯 Win Rate: {results['win_rate']:.1f}%")
        print(f"📊 Total de Trades: {results['total_trades']}")
        print(f"📉 Max Drawdown: {results['max_drawdown']:.2f}%")
        print(f"⚡ Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print("="*50)
        
        # Avaliação da performance
        if results['total_return'] > 10:
            cprint("🚀 EXCELENTE! Estratégia muito lucrativa!", "white", "on_green")
        elif results['total_return'] > 0:
            cprint("✅ BOM! Estratégia lucrativa no período", "white", "on_green")
        elif results['total_return'] > -5:
            cprint("⚠️ NEUTRO. Pequena perda no período", "white", "on_yellow")
        else:
            cprint("❌ ATENÇÃO! Perda significativa no período", "white", "on_red")
        
        if results['win_rate'] > 60:
            cprint(f"🎯 Excelente win rate de {results['win_rate']:.1f}%!", "white", "on_green")
        elif results['win_rate'] > 50:
            cprint(f"✅ Bom win rate de {results['win_rate']:.1f}%", "white", "on_green")
        else:
            cprint(f"⚠️ Win rate baixo: {results['win_rate']:.1f}%", "white", "on_yellow")
        
        cprint("\n📁 Arquivos CSV detalhados foram gerados", "white", "on_blue")
        cprint("💡 Analise os resultados antes de usar em trading real!", "white", "on_yellow")
        
    except Exception as e:
        cprint(f"\n❌ Erro durante o backtest: {str(e)}", "white", "on_red")
        cprint("🔧 Verifique os dados e configurações", "white", "on_yellow")

if __name__ == "__main__":
    main()