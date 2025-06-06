"""
🌙 Moon Dev's Autonomous Trading Backtest
Sistema de backtest para estratégia autônoma com LLM
Built with love by Moon Dev 🚀
"""

import sys
import os
from termcolor import cprint

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.backtest.autonomous_backtest import AutonomousBacktest

def run_custom_backtest():
    """
    Executa backtest personalizado com parâmetros do usuário
    """
    cprint("🧪 MOON DEV'S AUTONOMOUS TRADING BACKTEST", "white", "on_blue")
    cprint("🧠 Testando estratégia LLM autônoma", "white", "on_green")
    
    print("\n" + "="*60)
    print("CONFIGURAÇÃO DO BACKTEST:")
    print("="*60)
    
    # Configurações personalizáveis
    try:
        # Capital inicial
        capital = input("💰 Capital inicial (padrão: 10000): ").strip()
        initial_capital = float(capital) if capital else 10000
        
        # Período
        print("\n📅 Período do backtest:")
        start_date = input("Data início (YYYY-MM-DD, padrão: 2024-01-01): ").strip()
        if not start_date:
            start_date = "2024-01-01"
            
        end_date = input("Data fim (YYYY-MM-DD, padrão: 2024-03-01): ").strip()
        if not end_date:
            end_date = "2024-03-01"
        
        # Símbolos
        print("\n📊 Símbolos para trading:")
        print("Opções: BTCUSDT, ETHUSDT, SOLUSDT, ADAUSDT, DOTUSDT")
        symbols_input = input("Símbolos (separados por vírgula, padrão: BTCUSDT,ETHUSDT): ").strip()
        if symbols_input:
            symbols = [s.strip().upper() for s in symbols_input.split(',')]
        else:
            symbols = ['BTCUSDT', 'ETHUSDT']
        
        # Intervalo de análise
        interval = input("⏰ Intervalo de análise em horas (padrão: 12): ").strip()
        analysis_interval = int(interval) if interval else 12
        
        print("\n" + "="*60)
        print("RESUMO DA CONFIGURAÇÃO:")
        print(f"• Capital Inicial: ${initial_capital:,.2f}")
        print(f"• Período: {start_date} até {end_date}")
        print(f"• Símbolos: {', '.join(symbols)}")
        print(f"• Análise a cada: {analysis_interval} horas")
        print("="*60)
        
        confirm = input("\n✅ Confirmar e executar backtest? (s/N): ").strip().lower()
        if confirm != 's':
            cprint("👋 Backtest cancelado", "white", "on_yellow")
            return
        
        # Executa backtest
        cprint("\n🚀 Iniciando backtest...", "white", "on_green")
        
        backtest = AutonomousBacktest(initial_capital)
        results = backtest.run_backtest(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            analysis_interval=analysis_interval
        )
        
        # Resumo final
        cprint("\n🎉 BACKTEST CONCLUÍDO!", "white", "on_green")
        cprint(f"📈 Retorno Total: {results['total_return']:.2f}%", "white", "on_cyan")
        cprint(f"🎯 Win Rate: {results['win_rate']:.1f}%", "white", "on_cyan")
        cprint(f"📊 Total de Trades: {results['total_trades']}", "white", "on_cyan")
        cprint(f"📉 Max Drawdown: {results['max_drawdown']:.2f}%", "white", "on_cyan")
        
        if results['total_return'] > 0:
            cprint("🚀 Estratégia foi lucrativa no período testado!", "white", "on_green")
        else:
            cprint("⚠️ Estratégia teve prejuízo no período testado", "white", "on_yellow")
        
        cprint("\n📁 Arquivos CSV gerados com dados detalhados", "white", "on_blue")
        
    except ValueError as e:
        cprint(f"❌ Erro nos parâmetros: {str(e)}", "white", "on_red")
    except Exception as e:
        cprint(f"❌ Erro no backtest: {str(e)}", "white", "on_red")

def run_quick_demo():
    """
    Executa demo rápido do backtest
    """
    cprint("⚡ DEMO RÁPIDO - BACKTEST AUTÔNOMO", "white", "on_blue")
    
    # Configurações fixas para demo
    initial_capital = 10000
    start_date = "2024-01-01"
    end_date = "2024-02-01"  # Período menor para demo
    symbols = ['BTCUSDT']
    analysis_interval = 24  # Análise diária
    
    cprint(f"💰 Capital: ${initial_capital:,.2f}", "white", "on_cyan")
    cprint(f"📅 Período: {start_date} a {end_date}", "white", "on_cyan")
    cprint(f"📊 Símbolo: {symbols[0]}", "white", "on_cyan")
    cprint(f"⏰ Análise diária", "white", "on_cyan")
    
    try:
        backtest = AutonomousBacktest(initial_capital)
        results = backtest.run_backtest(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            analysis_interval=analysis_interval
        )
        
        cprint("\n⚡ DEMO CONCLUÍDO!", "white", "on_green")
        
    except Exception as e:
        cprint(f"❌ Erro no demo: {str(e)}", "white", "on_red")

if __name__ == "__main__":
    print("🌙 MOON DEV'S AUTONOMOUS BACKTEST SYSTEM")
    print("\nEscolha uma opção:")
    print("1. Backtest personalizado (configuração completa)")
    print("2. Demo rápido (configuração pré-definida)")
    print("3. Sair")
    
    choice = input("\nOpção (1-3): ").strip()
    
    if choice == "1":
        run_custom_backtest()
    elif choice == "2":
        run_quick_demo()
    elif choice == "3":
        cprint("👋 Até logo!", "white", "on_blue")
    else:
        cprint("❌ Opção inválida", "white", "on_red")