"""
🌙 Moon Dev's Custom Technical Indicators
Advanced indicators for LLM-based autonomous trading decisions
Built with love by Moon Dev 🚀
"""

import pandas as pd
import numpy as np
import pandas_ta as ta

class TechnicalIndicators:
    """
    Classe para calcular indicadores técnicos personalizados para análise autônoma da LLM
    """
    
    @staticmethod
    def calculate_ema_set(df, close_col='close'):
        """
        Calcula as 4 MME (9, 21, 50, 200 períodos)
        """
        df['MME_9'] = ta.ema(df[close_col], length=9)
        df['MME_21'] = ta.ema(df[close_col], length=21)
        df['MME_50'] = ta.ema(df[close_col], length=50)
        df['MME_200'] = ta.ema(df[close_col], length=200)
        
        return df
    
    @staticmethod
    def calculate_rsi(df, close_col='close', period=14):
        """
        Calcula RSI com período padrão de 14
        """
        df['RSI'] = ta.rsi(df[close_col], length=period)
        return df
    
    @staticmethod
    def calculate_distancia_mm_bands(df, close_col='close', mme_period=200, bb_period=200, bb_std=2):
        """
        Indicador personalizado DistanciaMM_Bands:
        1. Calcula a distância percentual do preço para MME_200
        2. Aplica Bollinger Bands sobre essa distância para identificar exaustão
        """
        # Garantir que temos a MME_200
        if 'MME_200' not in df.columns:
            df['MME_200'] = ta.ema(df[close_col], length=mme_period)
        
        # Distância percentual do preço para a MME_200
        df['DistanciaMM'] = ((df[close_col] - df['MME_200']) / df['MME_200']) * 100
        
        # Bollinger Bands aplicadas sobre a DistanciaMM
        bb_data = ta.bbands(df['DistanciaMM'], length=bb_period, std=bb_std)
        
        # Renomear as colunas das Bollinger Bands
        bb_cols = bb_data.columns
        df['DistanciaMM_Upper'] = bb_data[bb_cols[0]]  # Banda Superior
        df['DistanciaMM_Middle'] = bb_data[bb_cols[1]]  # Banda Média
        df['DistanciaMM_Lower'] = bb_data[bb_cols[2]]   # Banda Inferior
        
        # Sinais de exaustão estatística
        df['Exaustao_Bullish'] = df['DistanciaMM'] >= df['DistanciaMM_Upper']  # Muito acima da média
        df['Exaustao_Bearish'] = df['DistanciaMM'] <= df['DistanciaMM_Lower']  # Muito abaixo da média
        df['Zona_Normal'] = (df['DistanciaMM'] > df['DistanciaMM_Lower']) & (df['DistanciaMM'] < df['DistanciaMM_Upper'])
        
        return df
    
    @staticmethod
    def calculate_all_indicators(df, close_col='close'):
        """
        Calcula todos os indicadores necessários para análise da LLM
        """
        if df.empty or len(df) < 220:  # Precisa de pelo menos 220 velas para MME_200
            print(f"⚠️ Dados insuficientes: {len(df)} velas. Mínimo: 220")
            return df  # Retorna o DataFrame original mesmo sem indicadores
        
        try:
            # RSI (14 períodos)
            df = TechnicalIndicators.calculate_rsi(df, close_col, period=14)
            
            # 4 MME (9, 21, 50, 200)
            df = TechnicalIndicators.calculate_ema_set(df, close_col)
            
            # DistanciaMM_Bands (indicador personalizado)
            df = TechnicalIndicators.calculate_distancia_mm_bands(df, close_col)
            
            # Análises de contexto para a LLM
            df['Preco_Acima_MME_9'] = df[close_col] > df['MME_9']
            df['Preco_Acima_MME_21'] = df[close_col] > df['MME_21']
            df['Preco_Acima_MME_50'] = df[close_col] > df['MME_50']
            df['Preco_Acima_MME_200'] = df[close_col] > df['MME_200']
            
            # Alinhamento das MME para identificar tendência
            df['MME_Alinhamento_Bullish'] = (df['MME_9'] > df['MME_21']) & (df['MME_21'] > df['MME_50']) & (df['MME_50'] > df['MME_200'])
            df['MME_Alinhamento_Bearish'] = (df['MME_9'] < df['MME_21']) & (df['MME_21'] < df['MME_50']) & (df['MME_50'] < df['MME_200'])
            
            return df
            
        except Exception as e:
            print(f"❌ Erro calculando indicadores: {str(e)}")
            return df  # Retorna o DataFrame original
    
    @staticmethod
    def prepare_llm_analysis_data(df, lookback_periods=[1, 3, 5, 10, 20]):
        """
        Prepara os dados dos indicadores para análise da LLM
        Inclui valores atuais e histórico para análise multidimensional
        """
        if df.empty or len(df) < 220:  # Precisa de dados suficientes para indicadores
            return None
        
        latest_idx = len(df) - 1
        analysis_data = {
            'symbol_info': {
                'current_price': round(float(df.iloc[latest_idx]['close']), 6),
                'timestamp': latest_idx
            },
            'current_indicators': {},
            'historical_analysis': {}
        }
        
        # Dados atuais (última vela)
        current = df.iloc[latest_idx]
        analysis_data['current_indicators'] = {
            'RSI': {
                'value': round(float(current['RSI']), 2),
                'interpretation': 'Força relativa do movimento de preços (0-100). >70=sobrecompra, <30=sobrevenda'
            },
            'MME_9': {
                'value': round(float(current['MME_9']), 6),
                'price_position': 'acima' if current['Preco_Acima_MME_9'] else 'abaixo',
                'interpretation': 'Tendência de curtíssimo prazo'
            },
            'MME_21': {
                'value': round(float(current['MME_21']), 6),
                'price_position': 'acima' if current['Preco_Acima_MME_21'] else 'abaixo',
                'interpretation': 'Tendência de curto prazo'
            },
            'MME_50': {
                'value': round(float(current['MME_50']), 6),
                'price_position': 'acima' if current['Preco_Acima_MME_50'] else 'abaixo',
                'interpretation': 'Tendência de médio prazo'
            },
            'MME_200': {
                'value': round(float(current['MME_200']), 6),
                'price_position': 'acima' if current['Preco_Acima_MME_200'] else 'abaixo',
                'interpretation': 'Tendência de longo prazo - linha divisória bull/bear'
            },
            'DistanciaMM_Bands': {
                'distancia_percentual': round(float(current['DistanciaMM']), 3),
                'banda_superior': round(float(current['DistanciaMM_Upper']), 3),
                'banda_inferior': round(float(current['DistanciaMM_Lower']), 3),
                'exaustao_bullish': bool(current['Exaustao_Bullish']),
                'exaustao_bearish': bool(current['Exaustao_Bearish']),
                'zona_normal': bool(current['Zona_Normal']),
                'interpretation': 'Distância do preço da MME_200 com bandas de exaustão estatística'
            },
            'contexto_tendencia': {
                'alinhamento_bullish': bool(current['MME_Alinhamento_Bullish']),
                'alinhamento_bearish': bool(current['MME_Alinhamento_Bearish']),
                'interpretation': 'Alinhamento das MME indica força da tendência'
            }
        }
        
        # Análise histórica
        for period in lookback_periods:
            if latest_idx - period >= 0:
                hist_idx = latest_idx - period
                hist = df.iloc[hist_idx]
                
                analysis_data['historical_analysis'][f'{period}_periodos_atras'] = {
                    'RSI': round(float(hist['RSI']), 2),
                    'DistanciaMM': round(float(hist['DistanciaMM']), 3),
                    'exaustao_bullish': bool(hist['Exaustao_Bullish']),
                    'exaustao_bearish': bool(hist['Exaustao_Bearish']),
                    'alinhamento_bullish': bool(hist['MME_Alinhamento_Bullish']),
                    'alinhamento_bearish': bool(hist['MME_Alinhamento_Bearish']),
                    'preco': round(float(hist['close']), 6)
                }
        
        # Mudanças recentes para contexto
        if latest_idx >= 5:
            recent_rsi_change = current['RSI'] - df.iloc[latest_idx-5]['RSI']
            recent_distance_change = current['DistanciaMM'] - df.iloc[latest_idx-5]['DistanciaMM']
            
            analysis_data['mudancas_recentes'] = {
                'RSI_mudanca_5_periodos': round(float(recent_rsi_change), 2),
                'DistanciaMM_mudanca_5_periodos': round(float(recent_distance_change), 3),
                'interpretation': 'Mudanças nos últimos 5 períodos para identificar momentum'
            }
        
        return analysis_data

def create_autonomous_llm_prompt():
    """
    Cria o prompt para análise autônoma da LLM
    """
    prompt = """
Você é um trader quantitativo experiente com capacidade de análise autônoma de mercado. 

Sua tarefa é analisar os indicadores técnicos fornecidos e tomar uma decisão de trading baseada em sua interpretação dos dados, sem seguir regras fixas.

INDICADORES DISPONÍVEIS:

1. **RSI (Relative Strength Index)**
   - Mede a força relativa dos movimentos de preço
   - Valores entre 0-100
   - Considere não apenas os níveis absolutos, mas também a direção e momentum

2. **MME (Médias Móveis Exponenciais)**
   - MME_9: Reação rápida a mudanças de preço
   - MME_21: Tendência de curto prazo
   - MME_50: Tendência de médio prazo  
   - MME_200: Tendência de longo prazo e suporte/resistência psicológica
   - Analise o alinhamento, cruzamentos e posição do preço

3. **DistanciaMM_Bands (Indicador Personalizado)**
   - Mede quão "esticado" está o preço em relação à MME_200
   - Bandas de Bollinger aplicadas sobre essa distância identificam exaustão estatística
   - Exaustão_Bullish: Preço estatisticamente muito acima da média
   - Exaustão_Bearish: Preço estatisticamente muito abaixo da média
   - Zona_Normal: Movimento dentro de parâmetros estatísticos normais

METODOLOGIA DE ANÁLISE:
- Analise o contexto atual E o histórico recente dos indicadores
- Identifique padrões, divergências e confluências
- Considere o momentum e mudanças de direção
- Avalie a força da tendência atual
- Use a exaustão estatística para timing de entrada/saída
- Considere o risco/recompensa da operação

IMPORTANTE: 
- NÃO siga regras fixas como "RSI>70 = venda"
- Analise o CONTEXTO COMPLETO dos indicadores
- Considere a EVOLUÇÃO HISTÓRICA dos dados
- Tome decisões baseadas em CONFLUÊNCIA de sinais
- Seja AUTÔNOMO em sua análise

Responda APENAS com: BUY, SELL, ou HOLD

Depois explique detalhadamente sua análise considerando:
1. Estado atual de cada indicador
2. Evolução histórica relevante
3. Confluências ou divergências identificadas
4. Contexto de tendência
5. Timing da decisão baseado na exaustão estatística
6. Nível de confiança na decisão (0-100%)
"""
    return prompt