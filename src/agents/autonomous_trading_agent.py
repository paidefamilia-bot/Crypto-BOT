"""
🌙 Moon Dev's Autonomous Trading Agent
LLM-based autonomous trading with custom indicators
Built with love by Moon Dev 🚀
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import openai
import pandas as pd
import json
import numpy as np
from termcolor import colored, cprint
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

from src.core.config import *
from src.exchanges.bybit_client import BybitClient
from src.indicators.custom_indicators import TechnicalIndicators, create_autonomous_llm_prompt

# Load environment variables
load_dotenv()

class AutonomousTradingAgent:
    def __init__(self):
        """Initialize the Autonomous Trading Agent with LLM analysis"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("🚨 DEEPSEEK_API_KEY not found in environment variables!")
            
        # Initialize DeepSeek client
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Initialize Bybit client
        self.bybit = BybitClient()
        
        # Trading decisions storage
        self.decisions_df = pd.DataFrame(columns=[
            'timestamp', 'symbol', 'decision', 'confidence', 'reasoning', 
            'current_price', 'rsi', 'distancia_mm', 'exaustao_status'
        ])
        
        cprint("🤖 Moon Dev's Autonomous Trading Agent initialized!", "white", "on_blue")
        cprint("🧠 Using LLM for autonomous market analysis", "white", "on_green")
        
    def get_market_data_with_indicators(self, symbol, interval='15', limit=300):
        """
        Obtém dados de mercado e calcula todos os indicadores necessários
        """
        try:
            # Pega dados do Bybit
            kline_data = self.bybit.get_kline_data(symbol, interval, limit)
            if not kline_data:
                return None
            
            # Converte para DataFrame
            df_data = []
            for kline in reversed(kline_data):  # Bybit retorna mais recente primeiro
                df_data.append({
                    'timestamp': int(kline[0]),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                })
            
            df = pd.DataFrame(df_data)
            
            # Calcula todos os indicadores
            df = TechnicalIndicators.calculate_all_indicators(df, 'close')
            
            return df
            
        except Exception as e:
            cprint(f"❌ Error getting market data for {symbol}: {str(e)}", "white", "on_red")
            return None
    
    def autonomous_market_analysis(self, symbol, market_data):
        """
        Análise autônoma do mercado usando LLM
        """
        try:
            # Prepara dados para análise da LLM
            analysis_data = TechnicalIndicators.prepare_llm_analysis_data(market_data)
            if not analysis_data:
                cprint(f"⚠️ Dados insuficientes para análise de {symbol}", "white", "on_yellow")
                return None
            
            # Cria prompt com dados estruturados
            base_prompt = create_autonomous_llm_prompt()
            
            # Formata os dados para a LLM
            data_summary = f"""
ANÁLISE DE MERCADO PARA {symbol}

PREÇO ATUAL: ${analysis_data['symbol_info']['current_price']}

INDICADORES ATUAIS:
• RSI: {analysis_data['current_indicators']['RSI']['value']} - {analysis_data['current_indicators']['RSI']['interpretation']}

• MME_9: ${analysis_data['current_indicators']['MME_9']['value']} (preço {analysis_data['current_indicators']['MME_9']['price_position']})
• MME_21: ${analysis_data['current_indicators']['MME_21']['value']} (preço {analysis_data['current_indicators']['MME_21']['price_position']})
• MME_50: ${analysis_data['current_indicators']['MME_50']['value']} (preço {analysis_data['current_indicators']['MME_50']['price_position']})
• MME_200: ${analysis_data['current_indicators']['MME_200']['value']} (preço {analysis_data['current_indicators']['MME_200']['price_position']})

• DistanciaMM_Bands:
  - Distância da MME_200: {analysis_data['current_indicators']['DistanciaMM_Bands']['distancia_percentual']}%
  - Banda Superior: {analysis_data['current_indicators']['DistanciaMM_Bands']['banda_superior']}%
  - Banda Inferior: {analysis_data['current_indicators']['DistanciaMM_Bands']['banda_inferior']}%
  - Exaustão Bullish: {analysis_data['current_indicators']['DistanciaMM_Bands']['exaustao_bullish']}
  - Exaustão Bearish: {analysis_data['current_indicators']['DistanciaMM_Bands']['exaustao_bearish']}
  - Zona Normal: {analysis_data['current_indicators']['DistanciaMM_Bands']['zona_normal']}

• Contexto de Tendência:
  - Alinhamento Bullish (MME 9>21>50>200): {analysis_data['current_indicators']['contexto_tendencia']['alinhamento_bullish']}
  - Alinhamento Bearish (MME 9<21<50<200): {analysis_data['current_indicators']['contexto_tendencia']['alinhamento_bearish']}

ANÁLISE HISTÓRICA:
"""
            
            # Adiciona dados históricos
            for period, data in analysis_data['historical_analysis'].items():
                data_summary += f"""
{period.replace('_', ' ').title()}:
  - RSI: {data['RSI']} | DistanciaMM: {data['DistanciaMM']}%
  - Exaustão Bull: {data['exaustao_bullish']} | Exaustão Bear: {data['exaustao_bearish']}
  - Alinhamento Bull: {data['alinhamento_bullish']} | Alinhamento Bear: {data['alinhamento_bearish']}
  - Preço: ${data['preco']}
"""
            
            # Adiciona mudanças recentes se disponível
            if 'mudancas_recentes' in analysis_data:
                data_summary += f"""
MUDANÇAS RECENTES (5 períodos):
• RSI: {analysis_data['mudancas_recentes']['RSI_mudanca_5_periodos']} pontos
• DistanciaMM: {analysis_data['mudancas_recentes']['DistanciaMM_mudanca_5_periodos']}%
"""
            
            # Faz a análise com a LLM
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": base_prompt},
                    {"role": "user", "content": data_summary}
                ],
                max_tokens=1500,
                temperature=0.3  # Baixa temperatura para análise mais consistente
            )
            
            analysis_result = response.choices[0].message.content
            lines = analysis_result.split('\n')
            decision = lines[0].strip().upper() if lines else "HOLD"
            
            # Valida a decisão
            if decision not in ['BUY', 'SELL', 'HOLD']:
                decision = "HOLD"
            
            # Extrai nível de confiança
            confidence = 50  # Default
            for line in lines:
                if any(word in line.lower() for word in ['confiança', 'confidence', 'certeza']):
                    try:
                        numbers = [int(s) for s in line.split() if s.isdigit()]
                        if numbers:
                            confidence = min(max(numbers[0], 0), 100)  # Entre 0-100
                    except:
                        pass
            
            # Armazena a decisão
            current_data = analysis_data['current_indicators']
            new_decision = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'decision': decision,
                'confidence': confidence,
                'reasoning': '\n'.join(lines[1:]) if len(lines) > 1 else "Análise não detalhada",
                'current_price': analysis_data['symbol_info']['current_price'],
                'rsi': current_data['RSI']['value'],
                'distancia_mm': current_data['DistanciaMM_Bands']['distancia_percentual'],
                'exaustao_status': f"Bull:{current_data['DistanciaMM_Bands']['exaustao_bullish']}, Bear:{current_data['DistanciaMM_Bands']['exaustao_bearish']}"
            }
            
            self.decisions_df = pd.concat([
                self.decisions_df,
                pd.DataFrame([new_decision])
            ], ignore_index=True)
            
            cprint(f"🧠 Análise autônoma completa para {symbol}: {decision} (confiança: {confidence}%)", "white", "on_green")
            return analysis_result
            
        except Exception as e:
            cprint(f"❌ Error in autonomous analysis for {symbol}: {str(e)}", "white", "on_red")
            return None
    
    def execute_autonomous_decision(self, symbol, decision, confidence, current_price):
        """
        Executa a decisão autônoma da LLM
        """
        try:
            # Só executa se confiança for alta o suficiente
            min_confidence = 60  # Mínimo 60% de confiança
            
            if confidence < min_confidence:
                cprint(f"⚠️ {symbol}: Confiança muito baixa ({confidence}%) - não executando", "white", "on_yellow")
                return False
            
            # Pega posição atual
            current_position_value = self.bybit.get_position_value(symbol)
            
            if decision == "BUY":
                # Calcula tamanho da posição baseado na confiança
                max_position = BYBIT_MAX_POSITION_SIZE
                position_size = max_position * (confidence / 100) * 0.5  # Máximo 50% mesmo com 100% confiança
                
                # Só compra se não temos posição significativa
                if current_position_value < position_size * 0.8:
                    buy_amount = position_size - current_position_value
                    if buy_amount >= BYBIT_MIN_TRADE_SIZE:
                        cprint(f"🛒 {symbol}: Executando compra de ${buy_amount:.2f} (confiança: {confidence}%)", "white", "on_green")
                        result = self.bybit.market_buy(symbol, buy_amount)
                        return result is not None
                else:
                    cprint(f"⏸️ {symbol}: Posição já adequada para BUY", "white", "on_blue")
                    
            elif decision == "SELL":
                # Vende posição se temos algo significativo
                if current_position_value >= BYBIT_MIN_TRADE_SIZE:
                    cprint(f"🔴 {symbol}: Executando venda de posição (${current_position_value:.2f})", "white", "on_red")
                    result = self.bybit.market_sell(symbol)
                    return result is not None
                else:
                    cprint(f"⏸️ {symbol}: Sem posição significativa para vender", "white", "on_blue")
                    
            elif decision == "HOLD":
                cprint(f"⏸️ {symbol}: Mantendo posição atual", "white", "on_blue")
                
            return True
            
        except Exception as e:
            cprint(f"❌ Error executing decision for {symbol}: {str(e)}", "white", "on_red")
            return False
    
    def run_autonomous_cycle(self, trading_pairs):
        """
        Executa um ciclo completo de análise autônoma
        """
        cprint(f"\n🔄 Iniciando ciclo de análise autônoma - {datetime.now().strftime('%H:%M:%S')}", "white", "on_blue")
        
        cycle_results = []
        
        for symbol in trading_pairs:
            try:
                cprint(f"\n📊 Analisando {symbol}...", "white", "on_cyan")
                
                # Pega dados de mercado com indicadores
                market_data = self.get_market_data_with_indicators(symbol)
                
                if market_data is not None and len(market_data) > 200:
                    # Análise autônoma
                    analysis = self.autonomous_market_analysis(symbol, market_data)
                    
                    if analysis and not self.decisions_df.empty:
                        # Pega última decisão
                        last_decision = self.decisions_df.iloc[-1]
                        
                        print(f"\n🧠 Análise LLM para {symbol}:")
                        print(f"Decisão: {last_decision['decision']}")
                        print(f"Confiança: {last_decision['confidence']}%")
                        print(f"RSI: {last_decision['rsi']}")
                        print(f"DistanciaMM: {last_decision['distancia_mm']}%")
                        print(f"Status Exaustão: {last_decision['exaustao_status']}")
                        print("\nRaciocínio:")
                        print(last_decision['reasoning'][:500] + "..." if len(last_decision['reasoning']) > 500 else last_decision['reasoning'])
                        
                        # Executa decisão
                        executed = self.execute_autonomous_decision(
                            symbol, 
                            last_decision['decision'], 
                            last_decision['confidence'],
                            last_decision['current_price']
                        )
                        
                        cycle_results.append({
                            'symbol': symbol,
                            'decision': last_decision['decision'],
                            'confidence': last_decision['confidence'],
                            'executed': executed
                        })
                        
                        print("\n" + "="*60)
                    else:
                        cprint(f"⚠️ Falha na análise de {symbol}", "white", "on_yellow")
                else:
                    cprint(f"⚠️ Dados insuficientes para {symbol}", "white", "on_yellow")
                    
                # Pequena pausa entre análises
                time.sleep(2)
                
            except Exception as e:
                cprint(f"❌ Erro analisando {symbol}: {str(e)}", "white", "on_red")
        
        # Resumo do ciclo
        if cycle_results:
            cprint("\n📋 Resumo do Ciclo:", "white", "on_blue")
            summary_df = pd.DataFrame(cycle_results)
            print(summary_df.to_string(index=False))
            
            # Salva decisões
            if not self.decisions_df.empty:
                filename = f"autonomous_decisions_{datetime.now().strftime('%Y%m%d')}.csv"
                self.decisions_df.to_csv(filename, index=False)
                cprint(f"💾 Decisões salvas em {filename}", "white", "on_green")

def main():
    """
    Função principal para trading autônomo 24/7
    """
    cprint("🌙 Moon Dev's Autonomous Trading System", "white", "on_blue")
    cprint("🧠 LLM-Based Autonomous Market Analysis", "white", "on_green")
    cprint("⚠️ Sistema de trading autônomo - use com responsabilidade!", "white", "on_yellow")
    
    # Pares para trading
    TRADING_PAIRS = [
        'BTCUSDT',
        'ETHUSDT',
        'SOLUSDT',
        'ADAUSDT'
    ]
    
    # Intervalo entre ciclos (em minutos)
    CYCLE_INTERVAL = 30
    
    # Inicializa agente
    agent = AutonomousTradingAgent()
    
    cprint(f"🎯 Monitorando {len(TRADING_PAIRS)} pares de trading", "white", "on_blue")
    cprint(f"⏰ Ciclos a cada {CYCLE_INTERVAL} minutos", "white", "on_blue")
    
    while True:
        try:
            # Executa ciclo de análise
            agent.run_autonomous_cycle(TRADING_PAIRS)
            
            # Aguarda próximo ciclo
            cprint(f"\n😴 Aguardando {CYCLE_INTERVAL} minutos para próximo ciclo...", "white", "on_blue")
            time.sleep(CYCLE_INTERVAL * 60)
            
        except KeyboardInterrupt:
            cprint("\n👋 Sistema autônomo sendo encerrado...", "white", "on_yellow")
            break
        except Exception as e:
            cprint(f"❌ Erro no ciclo principal: {str(e)}", "white", "on_red")
            cprint("🔄 Tentando novamente em 5 minutos...", "white", "on_yellow")
            time.sleep(300)

if __name__ == "__main__":
    main()