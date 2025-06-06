"""
🌙 Moon Dev's Bybit Setup Test
Test script to verify all components are working
Built with love by Moon Dev 🚀
"""

import os
import sys
from dotenv import load_dotenv
from termcolor import cprint

def test_environment():
    """Test environment variables"""
    cprint("🔍 Testing environment variables...", "white", "on_blue")
    
    load_dotenv()
    
    required_vars = [
        'DEEPSEEK_API_KEY',
        'BYBIT_API_KEY', 
        'BYBIT_API_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        cprint(f"❌ Missing environment variables: {', '.join(missing_vars)}", "white", "on_red")
        cprint("📝 Please check your .env file", "white", "on_yellow")
        return False
    else:
        cprint("✅ All environment variables found!", "white", "on_green")
        return True

def test_deepseek_api():
    """Test DeepSeek API connection"""
    cprint("\n🤖 Testing DeepSeek AI API...", "white", "on_blue")
    
    try:
        import openai
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Simple test request
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "Say 'Hello Moon Dev!' if you can hear me."}
            ],
            max_tokens=50
        )
        
        if response.choices[0].message.content:
            cprint("✅ DeepSeek AI API working!", "white", "on_green")
            cprint(f"🤖 Response: {response.choices[0].message.content}", "white", "on_cyan")
            return True
        else:
            cprint("❌ DeepSeek API returned empty response", "white", "on_red")
            return False
            
    except Exception as e:
        cprint(f"❌ DeepSeek API error: {str(e)}", "white", "on_red")
        return False

def test_bybit_api():
    """Test Bybit API connection"""
    cprint("\n🏦 Testing Bybit API...", "white", "on_blue")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.exchanges.bybit_client import BybitClient
        
        client = BybitClient()
        
        # Test getting account balance
        balance = client.get_account_balance()
        if balance:
            cprint("✅ Bybit API connection successful!", "white", "on_green")
            cprint("💰 Account balance retrieved", "white", "on_cyan")
            return True
        else:
            cprint("❌ Could not retrieve account balance", "white", "on_red")
            return False
            
    except Exception as e:
        cprint(f"❌ Bybit API error: {str(e)}", "white", "on_red")
        return False

def test_market_data():
    """Test market data retrieval"""
    cprint("\n📊 Testing market data retrieval...", "white", "on_blue")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.exchanges.bybit_client import BybitClient
        
        client = BybitClient()
        
        # Test getting ticker price
        price = client.get_ticker_price('BTCUSDT')
        if price:
            cprint(f"✅ Market data working! BTC price: ${price:.2f}", "white", "on_green")
            
            # Test getting kline data
            klines = client.get_kline_data('BTCUSDT', '15', 10)
            if klines:
                cprint(f"✅ Kline data retrieved! Got {len(klines)} candles", "white", "on_green")
                return True
            else:
                cprint("❌ Could not retrieve kline data", "white", "on_red")
                return False
        else:
            cprint("❌ Could not retrieve ticker price", "white", "on_red")
            return False
            
    except Exception as e:
        cprint(f"❌ Market data error: {str(e)}", "white", "on_red")
        return False

def test_dependencies():
    """Test required Python packages"""
    cprint("\n📦 Testing Python dependencies...", "white", "on_blue")
    
    required_packages = [
        'pandas',
        'numpy', 
        'requests',
        'openai',
        'termcolor',
        'pandas_ta'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        cprint(f"❌ Missing packages: {', '.join(missing_packages)}", "white", "on_red")
        cprint("📝 Run: pip install -r requirements.txt", "white", "on_yellow")
        return False
    else:
        cprint("✅ All required packages installed!", "white", "on_green")
        return True

def main():
    """Run all tests"""
    cprint("🌙 Moon Dev's Bybit Setup Test", "white", "on_blue")
    cprint("=" * 50, "white")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Environment", test_environment),
        ("DeepSeek AI", test_deepseek_api),
        ("Bybit API", test_bybit_api),
        ("Market Data", test_market_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            cprint(f"❌ {test_name} test failed with exception: {str(e)}", "white", "on_red")
            results.append((test_name, False))
    
    # Summary
    cprint("\n" + "=" * 50, "white")
    cprint("📋 Test Results Summary:", "white", "on_blue")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        color = "green" if passed else "red"
        cprint(f"{test_name}: {status}", "white", f"on_{color}")
        if not passed:
            all_passed = False
    
    if all_passed:
        cprint("\n🎉 All tests passed! You're ready to trade!", "white", "on_green")
        cprint("🚀 Run: python src/main_bybit.py", "white", "on_cyan")
    else:
        cprint("\n⚠️ Some tests failed. Please fix the issues before trading.", "white", "on_yellow")
        cprint("📖 Check BYBIT_SETUP.md for help", "white", "on_blue")

if __name__ == "__main__":
    main()