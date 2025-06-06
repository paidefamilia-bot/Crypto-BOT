"""
🌙 Moon Dev Bybit AI Trading System
Main entry point for 24/7 Bybit trading with DeepSeek AI
Built with love by Moon Dev 🚀
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.bybit_trading_agent import main as run_bybit_agent

if __name__ == "__main__":
    print("🚀 Starting Moon Dev's Bybit AI Trading System...")
    print("🤖 Powered by DeepSeek AI")
    print("🏦 Trading on Bybit Exchange")
    print("💫 Remember: Moon Dev says trade safe and smart!")
    print("⚠️  IMPORTANT: This will trade with REAL money on Bybit!")
    print("🛡️  Make sure your API keys have appropriate permissions and limits!")
    
    # Safety confirmation
    confirmation = input("\n🔐 Type 'START' to begin 24/7 trading: ")
    if confirmation.upper() != 'START':
        print("👋 Trading cancelled. Stay safe!")
        sys.exit(0)
    
    try:
        run_bybit_agent()
    except KeyboardInterrupt:
        print("\n👋 Moon Dev Bybit AI Trading System shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print("🔧 Moon Dev suggests checking the logs and trying again!")