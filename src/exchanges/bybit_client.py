"""
🌙 Moon Dev's Bybit Integration
Bybit API client for 24/7 trading
Built with love by Moon Dev 🚀
"""

import os
import time
import hmac
import hashlib
import requests
import json
from datetime import datetime
from termcolor import colored, cprint
from dotenv import load_dotenv

load_dotenv()

class BybitClient:
    def __init__(self):
        """Initialize Bybit client with API credentials"""
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET")
        self.base_url = "https://api.bybit.com"
        
        if not self.api_key or not self.api_secret:
            raise ValueError("🚨 BYBIT_API_KEY and BYBIT_API_SECRET must be set in environment variables!")
        
        cprint("🚀 Moon Dev's Bybit Client initialized!", "white", "on_blue")
    
    def _generate_signature(self, params, timestamp):
        """Generate signature for Bybit API authentication"""
        param_str = timestamp + self.api_key + "5000" + '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method, endpoint, params=None):
        """Make authenticated request to Bybit API"""
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '5000',
            'Content-Type': 'application/json'
        }
        
        if method == 'GET':
            if params:
                query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
                headers['X-BAPI-SIGN'] = self._generate_signature(params, timestamp)
                url = f"{self.base_url}{endpoint}?{query_string}"
            else:
                headers['X-BAPI-SIGN'] = self._generate_signature({}, timestamp)
                url = f"{self.base_url}{endpoint}"
            
            response = requests.get(url, headers=headers)
        else:
            headers['X-BAPI-SIGN'] = self._generate_signature(params, timestamp)
            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, headers=headers, json=params)
        
        return response.json()
    
    def get_account_balance(self):
        """Get account balance"""
        try:
            response = self._make_request('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
            if response.get('retCode') == 0:
                return response['result']
            else:
                cprint(f"❌ Error getting balance: {response.get('retMsg')}", "white", "on_red")
                return None
        except Exception as e:
            cprint(f"❌ Exception getting balance: {str(e)}", "white", "on_red")
            return None
    
    def get_ticker_price(self, symbol):
        """Get current ticker price for a symbol"""
        try:
            response = self._make_request('GET', '/v5/market/tickers', {'category': 'spot', 'symbol': symbol})
            if response.get('retCode') == 0 and response['result']['list']:
                return float(response['result']['list'][0]['lastPrice'])
            return None
        except Exception as e:
            cprint(f"❌ Error getting ticker for {symbol}: {str(e)}", "white", "on_red")
            return None
    
    def get_kline_data(self, symbol, interval='15', limit=200):
        """Get kline/candlestick data"""
        try:
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = self._make_request('GET', '/v5/market/kline', params)
            if response.get('retCode') == 0:
                return response['result']['list']
            return None
        except Exception as e:
            cprint(f"❌ Error getting kline data for {symbol}: {str(e)}", "white", "on_red")
            return None
    
    def place_order(self, symbol, side, order_type, qty, price=None):
        """Place an order on Bybit"""
        try:
            params = {
                'category': 'spot',
                'symbol': symbol,
                'side': side,  # 'Buy' or 'Sell'
                'orderType': order_type,  # 'Market' or 'Limit'
                'qty': str(qty)
            }
            
            if order_type == 'Limit' and price:
                params['price'] = str(price)
            
            response = self._make_request('POST', '/v5/order/create', params)
            
            if response.get('retCode') == 0:
                cprint(f"✅ Order placed successfully: {response['result']['orderId']}", "white", "on_green")
                return response['result']
            else:
                cprint(f"❌ Order failed: {response.get('retMsg')}", "white", "on_red")
                return None
                
        except Exception as e:
            cprint(f"❌ Exception placing order: {str(e)}", "white", "on_red")
            return None
    
    def get_open_orders(self, symbol=None):
        """Get open orders"""
        try:
            params = {'category': 'spot'}
            if symbol:
                params['symbol'] = symbol
                
            response = self._make_request('GET', '/v5/order/realtime', params)
            if response.get('retCode') == 0:
                return response['result']['list']
            return []
        except Exception as e:
            cprint(f"❌ Error getting open orders: {str(e)}", "white", "on_red")
            return []
    
    def cancel_order(self, symbol, order_id):
        """Cancel an order"""
        try:
            params = {
                'category': 'spot',
                'symbol': symbol,
                'orderId': order_id
            }
            response = self._make_request('POST', '/v5/order/cancel', params)
            if response.get('retCode') == 0:
                cprint(f"✅ Order cancelled: {order_id}", "white", "on_green")
                return True
            else:
                cprint(f"❌ Cancel failed: {response.get('retMsg')}", "white", "on_red")
                return False
        except Exception as e:
            cprint(f"❌ Exception cancelling order: {str(e)}", "white", "on_red")
            return False
    
    def get_position_value(self, symbol):
        """Get current position value for a symbol"""
        try:
            balance = self.get_account_balance()
            if balance and 'list' in balance:
                for account in balance['list']:
                    if 'coin' in account:
                        for coin in account['coin']:
                            if coin['coin'] == symbol.replace('USDT', ''):
                                return float(coin['walletBalance']) * self.get_ticker_price(symbol)
            return 0.0
        except Exception as e:
            cprint(f"❌ Error getting position value: {str(e)}", "white", "on_red")
            return 0.0
    
    def market_buy(self, symbol, usdt_amount):
        """Execute market buy order"""
        try:
            current_price = self.get_ticker_price(symbol)
            if not current_price:
                return None
            
            qty = usdt_amount / current_price
            # Round to appropriate decimal places (usually 6 for most coins)
            qty = round(qty, 6)
            
            cprint(f"🛒 Market Buy: {qty} {symbol} at ~${current_price:.6f}", "white", "on_blue")
            return self.place_order(symbol, 'Buy', 'Market', qty)
            
        except Exception as e:
            cprint(f"❌ Error in market buy: {str(e)}", "white", "on_red")
            return None
    
    def market_sell(self, symbol, qty=None):
        """Execute market sell order"""
        try:
            if qty is None:
                # Sell all available balance
                balance = self.get_account_balance()
                if balance and 'list' in balance:
                    for account in balance['list']:
                        if 'coin' in account:
                            for coin in account['coin']:
                                if coin['coin'] == symbol.replace('USDT', ''):
                                    qty = float(coin['walletBalance'])
                                    break
            
            if qty and qty > 0:
                qty = round(qty, 6)
                current_price = self.get_ticker_price(symbol)
                cprint(f"🔴 Market Sell: {qty} {symbol} at ~${current_price:.6f}", "white", "on_red")
                return self.place_order(symbol, 'Sell', 'Market', qty)
            else:
                cprint(f"⚠️ No balance to sell for {symbol}", "white", "on_yellow")
                return None
                
        except Exception as e:
            cprint(f"❌ Error in market sell: {str(e)}", "white", "on_red")
            return None