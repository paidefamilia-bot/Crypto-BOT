"""
🌙 Moon Dev's Bybit Trading Agent with DeepSeek AI
24/7 Trading Agent for Bybit Exchange
Built with love by Moon Dev 🚀
"""

# ⏰ Run Configuration
RUN_INTERVAL_MINUTES = 15  # How often the AI agent runs

# 🎯 Trading Strategy Prompt - The Secret Sauce! 
TRADING_PROMPT = """
You are Moon Dev's AI Trading Assistant 🌙

Analyze the provided market data and make a trading decision based on these criteria:
1. Price action relative to MA20 and MA40
2. RSI levels and trend
3. Volume patterns
4. Recent price movements
5. Market momentum and volatility

Respond in this exact format:
1. First line must be one of: BUY, SELL, or HOLD (in caps)
2. Then explain your reasoning, including:
   - Technical analysis
   - Risk factors
   - Market conditions
   - Confidence level (as a percentage, e.g. 75%)

Remember: Moon Dev always prioritizes risk management! 🛡️
Focus on high-probability setups with good risk/reward ratios.
"""

# 💰 Portfolio Allocation Prompt
ALLOCATION_PROMPT = """
You are Moon Dev's Portfolio Allocation Assistant 🌙

Given the total portfolio size and trading recommendations, allocate capital efficiently.
Consider:
1. Position sizing based on confidence levels
2. Risk distribution across different assets
3. Keep cash buffer as specified
4. Maximum allocation per position
5. Current market volatility

Format your response as a Python dictionary:
{
    "BTCUSDT": allocated_amount,  # In USDT
    "ETHUSDT": allocated_amount,  # In USDT
    ...
    "USDT": remaining_cash  # Cash buffer
}

Remember:
- Total allocations must not exceed total_size
- Higher confidence should get larger allocations
- Never allocate more than {MAX_POSITION_PERCENTAGE}% to a single position
- Keep at least {CASH_PERCENTAGE}% in USDT as safety buffer
- Only allocate to BUY recommendations
- Consider correlation between assets
"""

import openai
import os
import pandas as pd
import json
import numpy as np
from termcolor import colored, cprint
from dotenv import load_dotenv
from ..core.config import *
from ..exchanges.bybit_client import BybitClient
from datetime import datetime, timedelta
import time

# Load environment variables
load_dotenv()

class BybitTradingAgent:
    def __init__(self):
        """Initialize the AI Trading Agent with Moon Dev's magic ✨"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("🚨 DEEPSEEK_API_KEY not found in environment variables!")
            
        # Initialize DeepSeek client (OpenAI compatible)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Initialize Bybit client
        self.bybit = BybitClient()
        
        self.recommendations_df = pd.DataFrame(columns=['symbol', 'action', 'confidence', 'reasoning'])
        cprint("🤖 Moon Dev's Bybit AI Trading Agent initialized with DeepSeek!", "white", "on_blue")
        
    def get_market_data_from_bybit(self, symbol, interval='15', limit=100):
        """Get market data from Bybit and format for analysis"""
        try:
            kline_data = self.bybit.get_kline_data(symbol, interval, limit)
            if not kline_data:
                return None
            
            # Convert Bybit kline data to DataFrame
            df_data = []
            for kline in reversed(kline_data):  # Bybit returns newest first, we want oldest first
                df_data.append({
                    'timestamp': int(kline[0]),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                })
            
            df = pd.DataFrame(df_data)
            
            # Calculate technical indicators
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA40'] = df['close'].rolling(window=40).mean()
            df['RSI'] = self._calculate_rsi(df['close'], 14)
            
            # Price position indicators
            df['price_above_MA20'] = df['close'] > df['MA20']
            df['price_above_MA40'] = df['close'] > df['MA40']
            df['MA20_above_MA40'] = df['MA20'] > df['MA40']
            
            # Recent performance
            df['price_change_1h'] = df['close'].pct_change(4)  # 4 periods of 15min = 1h
            df['price_change_4h'] = df['close'].pct_change(16)  # 16 periods = 4h
            df['price_change_24h'] = df['close'].pct_change(96)  # 96 periods = 24h
            
            return df
            
        except Exception as e:
            cprint(f"❌ Error getting market data for {symbol}: {str(e)}", "white", "on_red")
            return None
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze_market_data(self, symbol, market_data):
        """Analyze market data using DeepSeek AI"""
        try:
            # Prepare market data summary for AI
            latest = market_data.iloc[-1]
            recent_data = market_data.tail(10)
            
            market_summary = f"""
Symbol: {symbol}
Current Price: ${latest['close']:.6f}
24h Change: {latest['price_change_24h']*100:.2f}%
4h Change: {latest['price_change_4h']*100:.2f}%
1h Change: {latest['price_change_1h']*100:.2f}%

Technical Indicators:
- RSI: {latest['RSI']:.2f}
- MA20: ${latest['MA20']:.6f}
- MA40: ${latest['MA40']:.6f}
- Price above MA20: {latest['price_above_MA20']}
- Price above MA40: {latest['price_above_MA40']}
- MA20 above MA40: {latest['MA20_above_MA40']}

Recent Volume: {latest['volume']:.2f}
Recent High: ${recent_data['high'].max():.6f}
Recent Low: ${recent_data['low'].min():.6f}

Last 10 candles close prices:
{recent_data['close'].tolist()}
"""
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an expert cryptocurrency trading analyst."},
                    {"role": "user", "content": f"{TRADING_PROMPT}\n\nMarket Data to Analyze:\n{market_summary}"}
                ],
                max_tokens=1024,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            lines = analysis.split('\n')
            action = lines[0].strip() if lines else "HOLD"
            
            # Extract confidence from the response
            confidence = 50  # Default
            for line in lines:
                if 'confidence' in line.lower():
                    try:
                        confidence = int(''.join(filter(str.isdigit, line)))
                    except:
                        confidence = 50
            
            # Add to recommendations DataFrame
            reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else "No detailed reasoning provided"
            self.recommendations_df = pd.concat([
                self.recommendations_df,
                pd.DataFrame([{
                    'symbol': symbol,
                    'action': action,
                    'confidence': confidence,
                    'reasoning': reasoning
                }])
            ], ignore_index=True)
            
            cprint(f"🎯 DeepSeek AI Analysis Complete for {symbol}!", "white", "on_green")
            return analysis
            
        except Exception as e:
            cprint(f"❌ Error in AI analysis: {str(e)}", "white", "on_red")
            # Still add to DataFrame even on error
            self.recommendations_df = pd.concat([
                self.recommendations_df,
                pd.DataFrame([{
                    'symbol': symbol,
                    'action': "HOLD",
                    'confidence': 0,
                    'reasoning': f"Error during analysis: {str(e)}"
                }])
            ], ignore_index=True)
            return None
    
    def allocate_portfolio(self, total_usdt):
        """Allocate portfolio based on recommendations using DeepSeek AI"""
        try:
            # Filter to only include BUY recommendations
            buy_df = self.recommendations_df[self.recommendations_df['action'] == 'BUY'].copy()
            if buy_df.empty:
                cprint("🤔 No BUY recommendations - keeping everything in USDT", "white", "on_blue")
                return {"USDT": total_usdt}
            
            # Calculate maximum position size
            max_position_size = total_usdt * (MAX_POSITION_PERCENTAGE / 100)
            cash_buffer = total_usdt * (CASH_PERCENTAGE / 100)
            
            cprint(f"🎯 Maximum position size: ${max_position_size:.2f} ({MAX_POSITION_PERCENTAGE}% of ${total_usdt:.2f})", "white", "on_blue")
            cprint(f"💰 Cash buffer: ${cash_buffer:.2f} ({CASH_PERCENTAGE}%)", "white", "on_blue")
            
            recommendations_str = buy_df.to_string()
            
            allocation_prompt = ALLOCATION_PROMPT.format(
                MAX_POSITION_PERCENTAGE=MAX_POSITION_PERCENTAGE,
                CASH_PERCENTAGE=CASH_PERCENTAGE
            )
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an expert portfolio allocation specialist."},
                    {"role": "user", "content": f"{allocation_prompt}\n\nTotal Size: ${total_usdt}\nMax Position Size: ${max_position_size}\nCash Buffer: ${cash_buffer}\n\nRecommendations:\n{recommendations_str}"}
                ],
                max_tokens=1024,
                temperature=0.3
            )
            
            allocation_str = response.choices[0].message.content
            
            # Extract the dictionary from the response
            try:
                start_idx = allocation_str.find('{')
                end_idx = allocation_str.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = allocation_str[start_idx:end_idx]
                    allocation_dict = json.loads(json_str)
                    
                    # Validate and cap allocations
                    total_allocated = 0
                    for symbol, amount in list(allocation_dict.items()):
                        if symbol != 'USDT':
                            if amount > max_position_size:
                                cprint(f"⚠️ Capping {symbol} allocation from ${amount:.2f} to ${max_position_size:.2f}", "white", "on_yellow")
                                allocation_dict[symbol] = max_position_size
                            total_allocated += allocation_dict[symbol]
                    
                    # Ensure we have enough cash buffer
                    remaining_cash = total_usdt - total_allocated
                    if remaining_cash < cash_buffer:
                        cprint(f"⚠️ Adjusting allocations to maintain cash buffer", "white", "on_yellow")
                        # Reduce allocations proportionally
                        reduction_factor = (total_usdt - cash_buffer) / total_allocated
                        for symbol in allocation_dict:
                            if symbol != 'USDT':
                                allocation_dict[symbol] *= reduction_factor
                        remaining_cash = cash_buffer
                    
                    allocation_dict['USDT'] = remaining_cash
                    
                    return allocation_dict
                else:
                    raise ValueError("Could not find valid JSON in response")
                
            except Exception as e:
                cprint(f"❌ Error parsing allocation response: {str(e)}", "white", "on_red")
                cprint(f"Raw response: {allocation_str}", "white", "on_yellow")
                return {"USDT": total_usdt}
                
        except Exception as e:
            cprint(f"❌ Error in portfolio allocation: {str(e)}", "white", "on_red")
            return {"USDT": total_usdt}
    
    def execute_trades(self, allocation_dict):
        """Execute trades based on allocation"""
        try:
            cprint("\n🚀 Moon Dev executing trades on Bybit...", "white", "on_blue")
            
            for symbol, target_amount in allocation_dict.items():
                if symbol == 'USDT':
                    cprint(f"💵 Keeping ${target_amount:.2f} in USDT as buffer", "white", "on_blue")
                    continue
                
                try:
                    # Get current position value
                    current_value = self.bybit.get_position_value(symbol)
                    
                    cprint(f"\n🎯 {symbol}: Target ${target_amount:.2f}, Current ${current_value:.2f}", "white", "on_cyan")
                    
                    # Calculate difference
                    difference = target_amount - current_value
                    
                    if abs(difference) > 5:  # Only trade if difference > $5
                        if difference > 0:
                            # Need to buy more
                            cprint(f"🛒 Buying ${difference:.2f} worth of {symbol}", "white", "on_green")
                            result = self.bybit.market_buy(symbol, difference)
                            if result:
                                cprint(f"✅ Buy order executed for {symbol}", "white", "on_green")
                        else:
                            # Need to sell some
                            cprint(f"🔴 Selling ${abs(difference):.2f} worth of {symbol}", "white", "on_red")
                            # Calculate quantity to sell based on current price
                            current_price = self.bybit.get_ticker_price(symbol)
                            if current_price:
                                qty_to_sell = abs(difference) / current_price
                                result = self.bybit.market_sell(symbol, qty_to_sell)
                                if result:
                                    cprint(f"✅ Sell order executed for {symbol}", "white", "on_green")
                    else:
                        cprint(f"⏸️ Position already at target size for {symbol}", "white", "on_yellow")
                
                except Exception as e:
                    cprint(f"❌ Error executing trade for {symbol}: {str(e)}", "white", "on_red")
                
                # Small delay between trades
                time.sleep(2)
                
        except Exception as e:
            cprint(f"❌ Error executing trades: {str(e)}", "white", "on_red")

def main():
    """Main function to run the Bybit trading agent continuously"""
    cprint("🌙 Moon Dev Bybit AI Trading System Starting Up! 🚀", "white", "on_blue")
    cprint("🤖 Powered by DeepSeek AI and Bybit Exchange", "white", "on_green")
    
    # Trading pairs to monitor
    TRADING_PAIRS = [
        'BTCUSDT',
        'ETHUSDT', 
        'SOLUSDT',
        'ADAUSDT',
        'DOTUSDT'
    ]
    
    INTERVAL = RUN_INTERVAL_MINUTES * 60  # Convert minutes to seconds
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cprint(f"\n⏰ AI Agent Run Starting at {current_time}", "white", "on_green")
            
            # Initialize AI agent
            agent = BybitTradingAgent()
            
            # Get account balance
            balance = agent.bybit.get_account_balance()
            total_usdt = 1000  # Default, should be calculated from actual balance
            
            if balance:
                # Calculate total USDT value
                total_usdt = 0
                for account in balance.get('list', []):
                    for coin in account.get('coin', []):
                        if coin['coin'] == 'USDT':
                            total_usdt += float(coin['walletBalance'])
                        else:
                            # Convert other coins to USDT value
                            symbol = f"{coin['coin']}USDT"
                            price = agent.bybit.get_ticker_price(symbol)
                            if price:
                                total_usdt += float(coin['walletBalance']) * price
            
            cprint(f"💰 Total Portfolio Value: ${total_usdt:.2f} USDT", "white", "on_green")
            
            # Analyze each trading pair
            for symbol in TRADING_PAIRS:
                cprint(f"\n🤖 AI Agent Analyzing: {symbol}", "white", "on_green")
                
                # Get market data from Bybit
                market_data = agent.get_market_data_from_bybit(symbol)
                if market_data is not None:
                    analysis = agent.analyze_market_data(symbol, market_data)
                    if analysis:
                        print(f"\n📈 Analysis for {symbol}:")
                        print(analysis)
                        print("\n" + "="*50 + "\n")
                else:
                    cprint(f"⚠️ Could not get market data for {symbol}", "white", "on_yellow")
            
            # Show recommendations summary
            if not agent.recommendations_df.empty:
                cprint("\n📊 Moon Dev's Trading Recommendations:", "white", "on_blue")
                summary_df = agent.recommendations_df[['symbol', 'action', 'confidence']].copy()
                print(summary_df.to_string(index=False))
                
                # Calculate optimal portfolio allocation
                cprint("\n💰 Calculating optimal portfolio allocation...", "white", "on_blue")
                allocation = agent.allocate_portfolio(total_usdt)
                
                if allocation:
                    cprint("\n💼 Moon Dev's Portfolio Allocation:", "white", "on_blue")
                    print(json.dumps(allocation, indent=4))
                    
                    # Execute trades
                    cprint("\n🎯 Executing trades...", "white", "on_blue")
                    agent.execute_trades(allocation)
                    
                    cprint("✅ Trading cycle completed!", "white", "on_green")
            else:
                cprint("⚠️ No recommendations generated this cycle", "white", "on_yellow")
            
            # Wait for next cycle
            cprint(f"\n😴 Moon Dev sleeping for {RUN_INTERVAL_MINUTES} minutes until next analysis...", "white", "on_blue")
            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            cprint("\n👋 Moon Dev AI Trading System shutting down gracefully...", "white", "on_yellow")
            break
        except Exception as e:
            cprint(f"❌ Error in main loop: {str(e)}", "white", "on_red")
            cprint("🔧 Moon Dev will retry in 5 minutes...", "white", "on_yellow")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    main()