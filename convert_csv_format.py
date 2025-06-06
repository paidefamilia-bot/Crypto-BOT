#!/usr/bin/env python3
"""
🔄 Conversor de Formato CSV
Converte diferentes formatos de CSV para o formato padrão do backtest
Built with love by Moon Dev 🚀
"""

import sys
import os
import pandas as pd
from termcolor import cprint
from datetime import datetime

def convert_csv_to_standard_format(input_file, output_file=None):
    """
    Converte CSV para formato padrão
    """
    try:
        cprint(f"🔄 Convertendo arquivo: {input_file}", "white", "on_blue")
        
        # Carrega arquivo
        df = pd.read_csv(input_file)
        cprint(f"📊 Carregado: {len(df)} linhas, {len(df.columns)} colunas", "white", "on_green")
        
        # Mostra colunas originais
        print(f"Colunas originais: {list(df.columns)}")
        
        # Mapas de colunas comuns
        column_mappings = {
            'timestamp': ['timestamp', 'time', 'datetime', 'date', 'Date', 'Time', 'Timestamp', 'unix', 'Unix'],
            'open': ['open', 'Open', 'OPEN', 'o', 'Open Price'],
            'high': ['high', 'High', 'HIGH', 'h', 'High Price'],
            'low': ['low', 'Low', 'LOW', 'l', 'Low Price'],
            'close': ['close', 'Close', 'CLOSE', 'c', 'price', 'Price', 'Close Price'],
            'volume': ['volume', 'Volume', 'VOLUME', 'vol', 'Vol', 'v', 'Volume USD']
        }
        
        # Cria novo DataFrame
        new_df = pd.DataFrame()
        
        # Mapeia colunas
        for standard_name, possible_names in column_mappings.items():
            found = False
            for possible_name in possible_names:
                if possible_name in df.columns:
                    new_df[standard_name] = df[possible_name]
                    cprint(f"✅ Mapeado: {possible_name} → {standard_name}", "white", "on_green")
                    found = True
                    break
            
            if not found and standard_name != 'volume':
                cprint(f"⚠️ Coluna {standard_name} não encontrada", "white", "on_yellow")
        
        # Tratamento especial para timestamp
        if 'timestamp' not in new_df.columns:
            cprint("⚠️ Timestamp não encontrado, criando baseado no índice", "white", "on_yellow")
            # Assume dados diários começando em 2020
            start_date = pd.Timestamp('2020-01-01')
            new_df['timestamp'] = [start_date + pd.Timedelta(days=i) for i in range(len(df))]
        else:
            # Converte timestamp
            try:
                # Se for unix timestamp
                if new_df['timestamp'].dtype in ['int64', 'float64']:
                    # Verifica se é em segundos ou milissegundos
                    sample_ts = new_df['timestamp'].iloc[0]
                    if sample_ts > 1e10:  # Milissegundos
                        new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms')
                    else:  # Segundos
                        new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='s')
                else:
                    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])
                cprint("✅ Timestamp convertido", "white", "on_green")
            except:
                cprint("❌ Erro convertendo timestamp", "white", "on_red")
                return False
        
        # Se não tem volume, cria sintético
        if 'volume' not in new_df.columns:
            cprint("⚠️ Volume não encontrado, criando sintético", "white", "on_yellow")
            new_df['volume'] = 1000000
        
        # Verifica OHLC
        ohlc_cols = ['open', 'high', 'low', 'close']
        missing_ohlc = [col for col in ohlc_cols if col not in new_df.columns]
        
        if missing_ohlc:
            if 'close' in new_df.columns:
                cprint("⚠️ Criando OHLC sintético a partir do close", "white", "on_yellow")
                if 'open' not in new_df.columns:
                    new_df['open'] = new_df['close'].shift(1).fillna(new_df['close'].iloc[0])
                if 'high' not in new_df.columns:
                    new_df['high'] = new_df[['open', 'close']].max(axis=1) * 1.002
                if 'low' not in new_df.columns:
                    new_df['low'] = new_df[['open', 'close']].min(axis=1) * 0.998
            else:
                cprint(f"❌ Não foi possível criar OHLC: {missing_ohlc}", "white", "on_red")
                return False
        
        # Ordena por timestamp
        new_df = new_df.sort_values('timestamp').reset_index(drop=True)
        
        # Remove linhas com NaN
        new_df = new_df.dropna()
        
        # Define arquivo de saída
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_converted.csv"
        
        # Salva arquivo convertido
        new_df.to_csv(output_file, index=False)
        
        cprint(f"✅ Arquivo convertido salvo: {output_file}", "white", "on_green")
        cprint(f"📊 Dados finais: {len(new_df)} linhas", "white", "on_cyan")
        
        # Mostra resumo
        print("\nRESUMO DA CONVERSÃO:")
        print(f"Período: {new_df['timestamp'].min()} a {new_df['timestamp'].max()}")
        print(f"Preço inicial: ${new_df['close'].iloc[0]:.2f}")
        print(f"Preço final: ${new_df['close'].iloc[-1]:.2f}")
        print(f"Colunas finais: {list(new_df.columns)}")
        
        cprint(f"\n🎉 Agora você pode usar:", "white", "on_green")
        cprint(f"python autonomous_backtest.py {output_file} --capital 1000", "white", "on_cyan")
        
        return True
        
    except Exception as e:
        cprint(f"❌ Erro na conversão: {str(e)}", "white", "on_red")
        return False

def main():
    """
    Função principal
    """
    if len(sys.argv) < 2:
        cprint("🔄 CONVERSOR DE FORMATO CSV", "white", "on_blue")
        print("\nUso:")
        print("  python convert_csv_format.py arquivo_entrada.csv [arquivo_saida.csv]")
        print("\nExemplos:")
        print("  python convert_csv_format.py ETH-1d-1000wks-data.csv")
        print("  python convert_csv_format.py dados.csv dados_convertidos.csv")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        cprint(f"❌ Arquivo não encontrado: {input_file}", "white", "on_red")
        return
    
    success = convert_csv_to_standard_format(input_file, output_file)
    
    if not success:
        cprint("❌ Falha na conversão", "white", "on_red")

if __name__ == "__main__":
    main()