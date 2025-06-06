#!/usr/bin/env python3
"""
🔍 Teste de Formato CSV
Testa diferentes formatos de CSV para o backtest
Built with love by Moon Dev 🚀
"""

import sys
import os
import pandas as pd
from termcolor import cprint

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_csv_format(csv_file_path):
    """
    Testa e mostra o formato de um arquivo CSV
    """
    try:
        cprint(f"🔍 Analisando arquivo: {csv_file_path}", "white", "on_blue")
        
        if not os.path.exists(csv_file_path):
            cprint(f"❌ Arquivo não encontrado: {csv_file_path}", "white", "on_red")
            return False
        
        # Carrega CSV
        df = pd.read_csv(csv_file_path)
        
        cprint(f"📊 Arquivo carregado: {len(df)} linhas", "white", "on_green")
        
        # Mostra informações básicas
        print("\n" + "="*50)
        print("INFORMAÇÕES DO ARQUIVO:")
        print(f"Linhas: {len(df)}")
        print(f"Colunas: {len(df.columns)}")
        print("="*50)
        
        # Mostra colunas
        print("\nCOLUNAS ENCONTRADAS:")
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
        
        # Mostra primeiras linhas
        print("\nPRIMEIRAS 3 LINHAS:")
        print(df.head(3).to_string())
        
        # Testa detecção automática
        print("\n" + "="*50)
        print("TESTE DE DETECÇÃO AUTOMÁTICA:")
        print("="*50)
        
        from src.backtest.autonomous_backtest import AutonomousBacktest
        
        backtest = AutonomousBacktest(1000)
        try:
            processed_df = backtest.detect_and_fix_csv_format(df.copy())
            
            print("\nAPÓS PROCESSAMENTO:")
            print(f"Colunas: {list(processed_df.columns)}")
            print("\nPrimeiras 3 linhas processadas:")
            print(processed_df.head(3).to_string())
            
            cprint("\n✅ Formato detectado e corrigido com sucesso!", "white", "on_green")
            return True
            
        except Exception as e:
            cprint(f"\n❌ Erro no processamento: {str(e)}", "white", "on_red")
            return False
        
    except Exception as e:
        cprint(f"❌ Erro carregando arquivo: {str(e)}", "white", "on_red")
        return False

def main():
    """
    Função principal
    """
    if len(sys.argv) < 2:
        cprint("🔍 TESTE DE FORMATO CSV", "white", "on_blue")
        print("\nUso:")
        print("  python test_csv_format.py arquivo.csv")
        print("\nExemplos:")
        print("  python test_csv_format.py ETH-1d-1000wks-data.csv")
        print("  python test_csv_format.py /caminho/completo/para/arquivo.csv")
        return
    
    csv_file = sys.argv[1]
    
    # Se não for caminho absoluto, tenta encontrar o arquivo
    if not os.path.isabs(csv_file):
        # Tenta no diretório atual
        if os.path.exists(csv_file):
            csv_file = os.path.abspath(csv_file)
        # Tenta na pasta data/
        elif os.path.exists(f"data/{csv_file}"):
            csv_file = os.path.abspath(f"data/{csv_file}")
        # Tenta no diretório home do usuário
        elif os.path.exists(os.path.expanduser(f"~/{csv_file}")):
            csv_file = os.path.expanduser(f"~/{csv_file}")
    
    success = test_csv_format(csv_file)
    
    if success:
        cprint(f"\n🎉 Arquivo compatível! Você pode usar:", "white", "on_green")
        cprint(f"python autonomous_backtest.py {csv_file} --capital 1000", "white", "on_cyan")
    else:
        cprint(f"\n⚠️ Arquivo precisa de ajustes para ser compatível", "white", "on_yellow")

if __name__ == "__main__":
    main()