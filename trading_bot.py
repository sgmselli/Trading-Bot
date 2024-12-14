from alpaca_trade_api import REST
from time import sleep
from datetime import timedelta, datetime
import math

API_KEY = 'PKEFIA9SUV52SV7A7GMY'
API_SECRET = 'h2UPallsg8x51UPebd6eOiYQmyEJq9X8wvZIFzx0'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

api = REST(key_id=API_KEY, secret_key=API_SECRET, base_url=BASE_URL, api_version='v2')

#Get buying power your account has
def get_buying_power():
    account = api.get_account()
    return float(account.buying_power)

#Get the most recent price of our stock
def get_current_price(symbol):

    latest_trade = api.get_latest_trade(symbol)
    return latest_trade.price

#Get the previous days close price of our stock
def get_previous_close_price(symbol):

    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d') 

    bars = api.get_bars(symbol=symbol, timeframe='1Day', start=yesterday_str, end=yesterday_str).df

    if not bars.empty:
        return bars.iloc[0]['close']
    else:
        raise ValueError("No bars found.")

#Execute a buy or sell order
def execute_trade(symbol, qty, action):
    
    try:
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side=action,
            type='market',
            time_in_force='gtc'              
        )
        print(f"{action} order filled for {qty} stocks of {symbol}")
        return True

    except:
        print(f"Failed to execute {action} order for {qty} stocks of {symbol}")
        return False

#Constants
SYMBOL = 'AAPL'
BUY_PERCENTAGE = -0.01
SELL_PERCENTAGE = 0.02
INVESTMENT_PERCENTAGE = 0.5

#Variables
buy_price = 0
qty_owned = 0
has_position = False

#Buy the dip strategy
while True:

    try:
        previous_close_price = get_previous_close_price(SYMBOL)
        current_price = get_current_price(SYMBOL)

        percentage_change = (current_price - previous_close_price) / previous_close_price

        #Buy
        if not has_position and percentage_change <= BUY_PERCENTAGE:
            investment = INVESTMENT_PERCENTAGE*get_buying_power()
            qty_to_buy = math.floor(investment / current_price)

            if qty_to_buy > 0:
                trade = execute_trade(SYMBOL, qty_to_buy, 'buy')
                if trade:
                    print(f"Buying at {current_price} due to {percentage_change*100*-1:.2f}% dip")
                    has_position = True 
                    buy_price = current_price
                    qty_owned = qty_to_buy

            else:
                print(f"Not enough money to buy stock. You have {investment} and stock costs {current_price}.")
                
        #Sell
        elif has_position:

            buy_percentage_change = (current_price - buy_price) / buy_price

            if buy_percentage_change >= SELL_PERCENTAGE:
                trade = execute_trade(SYMBOL, qty_owned, 'sell')
                if trade:
                    print(f"Selling at {current_price} due to {buy_percentage_change*100:.2f}% rise")
                    has_position = False
                    buy_price = 0
        
        print(f"Successful iteration ran. Current price {current_price} vs last close price {previous_close_price} - let's make money.")
                
    except ValueError as e:
        print(f"An error occured: {e}")

    except Exception as e:
        print(f"An error occured: {e}")

    sleep(0.8)