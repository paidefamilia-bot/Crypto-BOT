#!/usr/bin/env python3
"""
🌙 Moon Dev's Backtest Test Script
Testa o sistema de backtest com dados de exemplo
Built with love by Moon Dev 🚀
"""

import sys
import os
from termcolor import cprint

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_backtest_system():
    """
    Testa o sistema de backtest com dados de exemplo
    """
    cprint("🧪 TESTE DO SISTEMA DE BACKTEST", "white", "on_blue")
    
    # Verifica se arquivo de exemplo existe
    sample_file = "data/BTC-5m-sample-data.csv"
    if not os.path.exists(sample_file):
        cprint(f"❌ Arquivo de exemplo não encontrado: {sample_file}", "white", "on_red")
        cprint("💡 Execute este script do diretório raiz do projeto", "white", "on_yellow")
        return False
    
    try:
        from src.backtest.autonomous_backtest import AutonomousBacktest
        
        cprint("✅ Módulos importados com sucesso", "white", "on_green")
        
        # Teste básico de carregamento de dados
        cprint("\n📊 Testando carregamento de dados...", "white", "on_blue")
        
        backtest = AutonomousBacktest(1000)  # Capital pequeno para teste
        data, symbol = backtest.load_historical_data_from_csv(sample_file)
        
        cprint(f"✅ Dados carregados: {len(data)} velas para {symbol}", "white", "on_green")
        
        # Teste de preparação de indicadores
        cprint("\n📈 Testando cálculo de indicadores...", "white", "on_blue")
        
        processed_data = backtest.prepare_data_with_indicators(data)
        
        # Verifica se indicadores foram calculados
        required_indicators = ['RSI', 'MME_9', 'MME_21', 'MME_50', 'MME_200', 'DistanciaMM']
        missing_indicators = [ind for ind in required_indicators if ind not in processed_data.columns]
        
        if missing_indicators:
            cprint(f"❌ Indicadores ausentes: {missing_indicators}", "white", "on_red")
            return False
        
        cprint(f"✅ Todos os indicadores calculados: {len(processed_data)} velas processadas", "white", "on_green")
        
        # Mostra exemplo dos dados
        if len(processed_data) > 0:
            latest = processed_data.iloc[-1]
            cprint("\n📋 Exemplo dos dados processados:", "white", "on_cyan")
            print(f"Preço: ${latest['close']:.2f}")
            print(f"RSI: {latest['RSI']:.2f}")
            print(f"MME_9: ${latest['MME_9']:.2f}")
            print(f"MME_200: ${latest['MME_200']:.2f}")
            print(f"DistanciaMM: {latest['DistanciaMM']:.3f}%")
            print(f"Exaustão Bullish: {latest['Exaustao_Bullish']}")
            print(f"Exaustão Bearish: {latest['Exaustao_Bearish']}")
        
        cprint("\n🎉 TESTE CONCLUÍDO COM SUCESSO!", "white", "on_green")
        cprint("✅ Sistema de backtest está funcionando corretamente", "white", "on_green")
        cprint("\n💡 Para executar backtest completo:", "white", "on_blue")
        cprint("   python autonomous_backtest.py data/BTC-5m-sample-data.csv", "white", "on_cyan")
        
        return True
        
    except ImportError as e:
        cprint(f"❌ Erro de importação: {str(e)}", "white", "on_red")
        cprint("💡 Execute: pip install -r requirements.txt", "white", "on_yellow")
        return False
        
    except Exception as e:
        cprint(f"❌ Erro no teste: {str(e)}", "white", "on_red")
        return False

def check_dependencies():
    """
    Verifica dependências necessárias
    """
    cprint("🔍 Verificando dependências...", "white", "on_blue")
    
    required_packages = [
        'pandas',
        'numpy',
        'openai',
        'termcolor'
    ]
    
    # Teste pandas_ta separadamente (pode ter warning mas funciona)
    try:
        import pandas_ta as ta
        cprint("✅ pandas_ta", "white", "on_green")
        pandas_ta_ok = True
    except ImportError:
        cprint("❌ pandas_ta", "white", "on_red")
        pandas_ta_ok = False
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            cprint(f"✅ {package}", "white", "on_green")
        except ImportError:
            missing_packages.append(package)
            cprint(f"❌ {package}", "white", "on_red")
    
    if missing_packages or not pandas_ta_ok:
        if missing_packages:
            cprint(f"\n❌ Pacotes ausentes: {', '.join(missing_packages)}", "white", "on_red")
        if not pandas_ta_ok:
            cprint("❌ pandas_ta não pôde ser importado", "white", "on_red")
        cprint("💡 Execute: pip install -r requirements.txt", "white", "on_yellow")
        return False
    
    cprint("\n✅ Todas as dependências estão instaladas!", "white", "on_green")
    return True

if __name__ == "__main__":
    cprint("🌙 MOON DEV'S BACKTEST SYSTEM TEST", "white", "on_blue")
    
    # Verifica dependências primeiro
    if not check_dependencies():
        sys.exit(1)
    
    # Testa o sistema
    if test_backtest_system():
        cprint("\n🚀 Sistema pronto para uso!", "white", "on_green")
        sys.exit(0)
    else:
        cprint("\n❌ Problemas encontrados no sistema", "white", "on_red")
        sys.exit(1)