"""
🌙 Moon Dev's Custom Trading Rules Example
Example of how to implement custom trading rules with the Bybit system
Built with love by Moon Dev 🚀
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.bybit_trading_agent import BybitTradingAgent
from src.exchanges.bybit_client import BybitClient
from termcolor import cprint
import pandas as pd

class CustomTradingRules(BybitTradingAgent):
    """
    Exemplo de como estender o agente base com regras personalizadas
    """
    
    def __init__(self):
        super().__init__()
        cprint("🎯 Custom Trading Rules Agent initialized!", "white", "on_blue")
    
    def custom_risk_filter(self, symbol, market_data, action, confidence):
        """
        Filtro de risco personalizado - adicione suas próprias regras aqui
        """
        latest = market_data.iloc[-1]
        
        # Regra 1: Não comprar se RSI > 70 (sobrecomprado)
        if action == "BUY" and latest['RSI'] > 70:
            cprint(f"🚫 {symbol}: RSI muito alto ({latest['RSI']:.1f}) - cancelando compra", "white", "on_yellow")
            return "HOLD", confidence * 0.5
        
        # Regra 2: Não vender se RSI < 30 (sobrevendido)
        if action == "SELL" and latest['RSI'] < 30:
            cprint(f"🚫 {symbol}: RSI muito baixo ({latest['RSI']:.1f}) - cancelando venda", "white", "on_yellow")
            return "HOLD", confidence * 0.5
        
        # Regra 3: Reduzir confiança se volume está baixo
        avg_volume = market_data['volume'].tail(20).mean()
        if latest['volume'] < avg_volume * 0.5:
            cprint(f"⚠️ {symbol}: Volume baixo - reduzindo confiança", "white", "on_yellow")
            confidence *= 0.7
        
        # Regra 4: Não operar se volatilidade muito alta
        price_volatility = market_data['close'].tail(10).std() / market_data['close'].tail(10).mean()
        if price_volatility > 0.05:  # 5% de volatilidade
            cprint(f"⚠️ {symbol}: Alta volatilidade ({price_volatility:.1%}) - reduzindo confiança", "white", "on_yellow")
            confidence *= 0.6
        
        return action, confidence
    
    def analyze_market_data(self, symbol, market_data):
        """
        Override da análise para incluir regras personalizadas
        """
        # Primeiro, faz a análise padrão com IA
        analysis = super().analyze_market_data(symbol, market_data)
        
        if analysis and not self.recommendations_df.empty:
            # Pega a última recomendação
            last_rec = self.recommendations_df.iloc[-1]
            original_action = last_rec['action']
            original_confidence = last_rec['confidence']
            
            # Aplica filtros personalizados
            filtered_action, filtered_confidence = self.custom_risk_filter(
                symbol, market_data, original_action, original_confidence
            )
            
            # Atualiza a recomendação se mudou
            if filtered_action != original_action or filtered_confidence != original_confidence:
                self.recommendations_df.iloc[-1, self.recommendations_df.columns.get_loc('action')] = filtered_action
                self.recommendations_df.iloc[-1, self.recommendations_df.columns.get_loc('confidence')] = filtered_confidence
                
                cprint(f"🔄 {symbol}: Regra personalizada aplicada - {original_action} -> {filtered_action}", "white", "on_cyan")
        
        return analysis
    
    def momentum_strategy(self, symbol, market_data):
        """
        Estratégia de momentum personalizada
        """
        latest = market_data.iloc[-1]
        
        # Calcula momentum de diferentes períodos
        momentum_1h = latest['price_change_1h']
        momentum_4h = latest['price_change_4h']
        momentum_24h = latest['price_change_24h']
        
        # Regras de momentum
        strong_bullish = (momentum_1h > 0.02 and momentum_4h > 0.05 and 
                         latest['price_above_MA20'] and latest['MA20_above_MA40'])
        
        strong_bearish = (momentum_1h < -0.02 and momentum_4h < -0.05 and 
                         not latest['price_above_MA20'])
        
        if strong_bullish and latest['RSI'] < 65:
            return "BUY", 85
        elif strong_bearish and latest['RSI'] > 35:
            return "SELL", 80
        else:
            return "HOLD", 50
    
    def mean_reversion_strategy(self, symbol, market_data):
        """
        Estratégia de reversão à média
        """
        latest = market_data.iloc[-1]
        
        # Calcula desvio da média móvel
        ma20_deviation = (latest['close'] - latest['MA20']) / latest['MA20']
        
        # Reversão à média quando preço está muito longe da MA20
        if ma20_deviation < -0.05 and latest['RSI'] < 35:  # Muito abaixo da média
            return "BUY", 75
        elif ma20_deviation > 0.05 and latest['RSI'] > 65:  # Muito acima da média
            return "SELL", 75
        else:
            return "HOLD", 40

def run_custom_strategy():
    """
    Exemplo de como executar com estratégias personalizadas
    """
    cprint("🌙 Moon Dev's Custom Trading Strategy Demo", "white", "on_blue")
    
    # Símbolos para testar
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    
    # Inicializa agente personalizado
    agent = CustomTradingRules()
    
    for symbol in test_symbols:
        cprint(f"\n📊 Analisando {symbol}...", "white", "on_green")
        
        # Pega dados de mercado
        market_data = agent.get_market_data_from_bybit(symbol)
        
        if market_data is not None:
            # Análise padrão com IA + regras personalizadas
            ai_analysis = agent.analyze_market_data(symbol, market_data)
            
            # Estratégias adicionais
            momentum_action, momentum_conf = agent.momentum_strategy(symbol, market_data)
            mean_rev_action, mean_rev_conf = agent.mean_reversion_strategy(symbol, market_data)
            
            cprint(f"🤖 IA + Regras: {agent.recommendations_df.iloc[-1]['action']} (conf: {agent.recommendations_df.iloc[-1]['confidence']}%)", "white", "on_cyan")
            cprint(f"📈 Momentum: {momentum_action} (conf: {momentum_conf}%)", "white", "on_blue")
            cprint(f"🔄 Mean Reversion: {mean_rev_action} (conf: {mean_rev_conf}%)", "white", "on_magenta")
            
            print("\n" + "="*50)
    
    # Mostra resumo das recomendações
    if not agent.recommendations_df.empty:
        cprint("\n📋 Resumo das Recomendações:", "white", "on_blue")
        print(agent.recommendations_df[['symbol', 'action', 'confidence']].to_string(index=False))

if __name__ == "__main__":
    # Este é apenas um exemplo/demo - não executa trades reais
    cprint("⚠️ DEMO MODE - Nenhum trade será executado", "white", "on_yellow")
    run_custom_strategy()