"""
🌙 Moon Dev's Autonomous Trading System - LIVE TRADING
Sistema de trading autônomo com análise LLM em tempo real
Built with love by Moon Dev 🚀
"""

import sys
import os
from termcolor import cprint

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.autonomous_trading_agent import main as run_autonomous_agent

if __name__ == "__main__":
    cprint("🌙 MOON DEV'S AUTONOMOUS TRADING SYSTEM", "white", "on_blue")
    cprint("🧠 Powered by LLM Autonomous Analysis", "white", "on_green")
    cprint("🏦 Trading on Bybit Exchange", "white", "on_cyan")
    cprint("⚠️  ATENÇÃO: Este sistema fará trades REAIS com dinheiro REAL!", "white", "on_red")
    
    print("\n" + "="*60)
    print("CARACTERÍSTICAS DO SISTEMA:")
    print("• Análise autônoma com LLM (sem regras fixas)")
    print("• Indicadores: RSI, 4 MME, DistanciaMM_Bands")
    print("• Decisões baseadas em contexto atual + histórico")
    print("• Trading 24/7 com intervalos configuráveis")
    print("• Gestão de risco integrada")
    print("="*60)
    
    # Confirmação de segurança
    print("\n🔐 CONFIRMAÇÕES DE SEGURANÇA:")
    print("1. Você configurou as APIs (DeepSeek + Bybit)?")
    print("2. Você testou com o script test_bybit_setup.py?")
    print("3. Você definiu limites na sua conta Bybit?")
    print("4. Você está ciente dos riscos de trading automatizado?")
    
    confirmation = input("\n✅ Digite 'CONFIRMO' para iniciar o trading autônomo: ")
    
    if confirmation.upper() != 'CONFIRMO':
        cprint("👋 Trading cancelado. Sempre teste antes de usar!", "white", "on_yellow")
        sys.exit(0)
    
    cprint("\n🚀 Iniciando sistema de trading autônomo...", "white", "on_green")
    
    try:
        run_autonomous_agent()
    except KeyboardInterrupt:
        cprint("\n👋 Sistema autônomo encerrado pelo usuário", "white", "on_yellow")
    except Exception as e:
        cprint(f"\n❌ Erro no sistema: {str(e)}", "white", "on_red")
        cprint("🔧 Verifique as configurações e tente novamente", "white", "on_blue")