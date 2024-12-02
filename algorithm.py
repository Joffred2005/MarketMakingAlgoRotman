# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 09:35:00 2024

@author: Oriana.Rahman
"""

import requests
from time import sleep
import numpy as np
import pandas as pd

# Creates a session object to manage and persist settings across multiple API requests
s = requests.Session()
s.headers.update({'X-API-key': ' '}) # Adds an API key to the session headers for authentication

# Global variables for managing risk and order constraints
MAX_LONG_EXPOSURE = 250000  # Maximum allowable long position exposure
MAX_SHORT_EXPOSURE = -250000  # Maximum allowable short position exposure
ORDER_LIMIT = 5000  # Maximum allowable order size per transaction

# Function to fetch the current tick and status of the case
def get_tick():
    resp = s.get('http://localhost:9999/v1/case')  # Sends a GET request to fetch case details
    if resp.ok:  # Checks if the request was successful
        case = resp.json()  # Parses the response JSON
        return case['tick'], case['status']  # Returns the current tick and case status

# Function to get the best bid and ask prices for a given ticker
def get_bid_ask(ticker):
    payload = {'ticker': ticker}  # Defines the request parameters for the ticker
    resp = s.get ('http://localhost:9999/v1/securities/book', params=payload)  # Sends a GET request to fetch the order book
    if resp.ok:  # Checks if the request was successful
        book = resp.json()  # Parses the response JSON
        bid_side_book = book['bids']  # Extracts the bid-side order book
        ask_side_book = book['asks']  # Extracts the ask-side order book
        
        bid_prices_book = [item['price'] for item in bid_side_book]  # Gets all bid prices
        ask_prices_book = [item['price'] for item in ask_side_book]  # Gets all ask prices
        
        bid_volume_book = [item['quantity'] for item in bid_side_book]
        ask_volume_book = [item['quantity'] for item in ask_side_book]

        bidVol = np.sum(bid_volume_book)
        askVol = np.sum(ask_volume_book)
        

        if bidVol > askVol:
            trend = bidVol/askVol
        else:
            trend = -1*(askVol/bidVol)

        best_bid_price = bid_prices_book[0]  # Selects the best (highest) bid price
        best_ask_price = ask_prices_book[0]  # Selects the best (lowest) ask price

        return best_bid_price, best_ask_price, trend  # Returns the best bid and ask prices

# Function to get the time and sales data (trade quantities) for a given ticker
def get_time_sales(ticker):
    payload = {'ticker': ticker}  # Defines the request parameters for the ticker
    resp = s.get ('http://localhost:9999/v1/securities/tas', params=payload)  # Sends a GET request to fetch the time and sales data
    if resp.ok:  # Checks if the request was successful
        book = resp.json()  # Parses the response JSON
        time_sales_book = [item["quantity"] for item in book]  # Extracts the quantities from the time and sales data
        return time_sales_book  # Returns the trade quantities

# Function to calculate the total position across all securities
def get_long_position():
    resp = s.get ('http://localhost:9999/v1/securities')  # Sends a GET request to fetch securities data
    if resp.ok:  # Checks if the request was successful
        book = resp.json()  # Parses the response JSON
        pos1 = book[0]['position'] # OWL
        pos2 = book[1]['position'] # CROW
        pos3 = book[2]['position'] # DOVE
        pos4 = book[3]['position'] # DUCK

        # No contribution to long if negative
        if (pos1<0):
            pos1 = 0
        if (pos2<0):
            pos2 = 0
        if (pos3<0):
            pos3 = 0
        if (pos4<0):
            pos4 = 0

        return pos1+pos2+pos3+pos4 # Returns the sum of positions for all securities
    
def get_short_position():
    resp = s.get ('http://localhost:9999/v1/securities')  # Sends a GET request to fetch securities data
    if resp.ok:  # Checks if the request was successful
        book = resp.json()  # Parses the response JSON
        pos1 = book[0]['position'] # OWL
        pos2 = book[1]['position'] # CROW
        pos3 = book[2]['position'] # DOVE
        pos4 = book[3]['position'] # DUCK

        # No contribution to long if negative
        if (pos1>0):
            pos1 = 0
        if (pos2>0):
            pos2 = 0
        if (pos3>0):
            pos3 = 0
        if (pos4>0):
            pos4 = 0

        return pos1+pos2+pos3+pos4 # Returns the sum of positions for all securities
    
def indPos(security):
    resp = s.get ('http://localhost:9999/v1/securities')  # Sends a GET request to fetch securities data
    if resp.ok:  # Checks if the request was successful
        book = resp.json()  # Parses the response JSON
        pos1 = book[0]['position'] # OWL
        pos2 = book[1]['position'] # CROW
        pos3 = book[2]['position'] # DOVE
        pos4 = book[3]['position'] # DUCK

    if (security == 'OWL'):
        return pos1
    if (security == 'CROW'):
        return pos2
    if (security == 'DOVE'):
        return pos3
    if (security == 'DUCK'):
        return pos4

# def velocity(ticker_symbol, current_tick):
    



# Function to get the open buy and sell orders for a given ticker
def get_open_orders(ticker):
    payload = {'ticker': ticker}  # Defines the request parameters for the ticker
    resp = s.get ('http://localhost:9999/v1/orders', params=payload)  # Sends a GET request to fetch open orders
    if resp.ok:  # Checks if the request was successful
        orders = resp.json()  # Parses the response JSON
        buy_orders = [item for item in orders if item["action"] == "BUY"]  # Filters for buy orders
        sell_orders = [item for item in orders if item["action"] == "SELL"]  # Filters for sell orders
        return buy_orders, sell_orders  # Returns the lists of buy and sell orders

# Function to get the status of a specific order by its ID
def get_order_status(order_id):
    resp = s.get ('http://localhost:9999/v1/orders' + '/' + str(order_id))  # Sends a GET request to fetch the status of a specific order
    if resp.ok:  # Checks if the request was successful
        order = resp.json()  # Parses the response JSON
        return order['status']  # Returns the status of the order
    
def get_moving_average(security, currentTick):
    if (security == 'OWL'):
        if currentTick < 10:
            return owl_prices[currentTick]
        if (owl_prices[currentTick-10] == 0):
            pastTick = currentTick-9
        else:
            pastTick = currentTick-10
        if (owl_prices[currentTick] == 0):
            currentTick-=1
        movingAve = (owl_prices[currentTick] + owl_prices[pastTick])/2
        return movingAve
    
    if (security == 'CROW'):
        if currentTick < 10:
            return crow_prices[currentTick]
        if (crow_prices[currentTick-10] == 0):
            pastTick = currentTick-9
        else:
            pastTick = currentTick-10
        if (crow_prices[currentTick] == 0):
            currentTick-=1
        movingAve = (crow_prices[currentTick] + crow_prices[pastTick])/2
        return movingAve
    
    if (security == 'DUCK'):
        if currentTick < 10:
            return duck_prices[currentTick]
        if (duck_prices[currentTick-10] == 0):
            pastTick = currentTick-9
        else:
            pastTick = currentTick-10
        if (duck_prices[currentTick] == 0):
            currentTick-=1
        movingAve = (duck_prices[currentTick] + duck_prices[pastTick])/2
        return movingAve
    
    if (security == 'DOVE'):
        if currentTick < 10:
            return dove_prices[currentTick]
        if (dove_prices[currentTick-10] == 0):
            pastTick = currentTick-9
        else:
            pastTick = currentTick-10
        if (dove_prices[currentTick] == 0):
            currentTick-=1
        movingAve = (dove_prices[currentTick] + dove_prices[pastTick])/2
        return movingAve

def adjusted_order (movingAvePrice, currentPrice):
    adjustedPrice = abs(movingAvePrice - currentPrice)/movingAvePrice
    return 1-adjustedPrice

# Check for bid-ask spreads and make trades based on difference
def market_making (ticker_symbol, buy_price, sell_price):
    difference = sell_price - buy_price
    if (ticker_symbol == 'DUCK'): # +0.03/share to trade (less difference cuz less volatile)
        if (difference > 0.40): # Most people will attempt to take advantage when spreads are large, reduce profit intake to ensure that some profit is made
            buy = buy_price + 0.08
            sell = sell_price - 0.08
            return buy, sell
        if (difference > 0.20):
            buy = buy_price + 0.05
            sell = sell_price -0.05
            return buy, sell
    if (ticker_symbol =='DOVE'):
        if (difference > 0.20):
            buy = buy_price + 0.05
            sell = sell_price - 0.05
            return buy, sell
        
    if (ticker_symbol == 'OWL'): # +0.04/share to trade (less difference cuz less volatile)
        if (difference > 0.40):
            buy = buy_price + 0.19
            sell = sell_price - 0.19
            return buy, sell
        # if (difference > 0.30): #changed
        #     buy = buy_price + 0.14
        #     sell = sell_price - 0.14
        #     return buy, sell
    if (ticker_symbol == 'CROW'): # +0.03/share to trade (less difference cuz less volatile)
        if (difference > 0.40): # Most people will attempt to take advantage when spreads are large, reduce profit intake to ensure that some profit is made
            buy = buy_price + 0.10
            sell = sell_price - 0.10
            return buy, sell
        if (difference > 0.20):
            buy = buy_price + 0.05
            sell = sell_price -0.05
            return buy, sell
        # if (difference > 0.20):
        #     buy = buy_price + 0.08
        #     sell = sell_price - 0.08
        #     return buy, sell
        # if (difference > 0.40):
        #     buy = buy_price + 0.08
        #     sell = sell_price - 0.08
        #     return buy, sell
        # if (difference > 0.05): # Small profit available
        #     buy = buy_price + 0.02
        #     sell = sell_price - 0.02
        #     return buy, sell
    return 0, 0
    # if (ticker_symbol == 'CROW'): # -0.03/share to trade (need a bigger difference to take advantage)
    # if (ticker_symbol == 'DOVE'): # -0.04/share to trade (need a bigger difference to take advantage)
    

def place_order(ticker, order_type, quantity, price, action):
    """
    Helper function to place orders.
    """
    resp = s.post(
        'http://localhost:9999/v1/orders',
        params={
            'ticker': ticker,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'action': action
        }
    )
    if resp.status_code != 200:
        print(f"Error placing {action} order: {resp.status_code}, {resp.text}")
    return resp

owl_prices = np.zeros(600, dtype=float)
crow_prices = np.zeros(600, dtype=float)
dove_prices = np.zeros(600, dtype=float)
duck_prices = np.zeros(600, dtype=float)
    
def main():
    tick, status = get_tick()
    ticker_list = ['OWL','CROW','DOVE','DUCK']

    while status == 'ACTIVE':        

        for i in range(4):
            buy_price_owl, sell_price_owl, trendOwl = get_bid_ask('OWL')
            buy_price_crow, sell_price_crow, trendCrow = get_bid_ask('CROW')
            buy_price_dove, sell_price_dove, trendDove = get_bid_ask('DOVE')
            buy_price_duck, sell_price_duck, trendDuck = get_bid_ask('DUCK')
            
            # current_ave_owl = get_moving_average(buy_price_owl, past_price_owl)
            # current_ave_crow = get_moving_average(buy_price_crow, past_price_crow)
            # current_ave_dove = get_moving_average(buy_price_dove, past_price_dove)
            # current_ave_duck = get_moving_average(buy_price_duck, past_price_duck)      
            
            tick1, status1 = get_tick()           
            print("%d %d \n", tick1, status1)

            crowAve = get_moving_average('CROW', tick)
            owlAve = get_moving_average('OWL', tick)
            doveAve = get_moving_average('DOVE', tick)
            duckAve = get_moving_average('DUCK', tick)
            if crowAve < buy_price_crow/2 + 1:
                crowAve=buy_price_crow
            if owlAve < buy_price_owl/2 + 1:
                owlAve=buy_price_owl
            if doveAve < buy_price_dove/2 + 1:
                doveAve=buy_price_dove
            if duckAve < buy_price_duck/2 + 1:
                duckAve=buy_price_duck

            print(crowAve)
            print(buy_price_crow)
            print(owlAve)
            print(buy_price_owl)
            print(duckAve)
            print(buy_price_duck)
            print(doveAve)
            print(buy_price_dove)
            
            # past_price_owl = buy_price_owl
            # past_price_crow = buy_price_crow
            # past_price_dove = buy_price_dove
            # past_price_duck = buy_price_duck

            ticker_symbol = ticker_list[i]
            long_position = get_long_position()
            short_position = get_short_position()
            best_bid_price, best_ask_price, hi= get_bid_ask('OWL')

            grossPos = long_position+abs(short_position)

            crow_prices[tick1] = buy_price_crow
            owl_prices[tick1] = buy_price_owl
            dove_prices[tick1] = buy_price_dove
            duck_prices[tick1] = buy_price_duck

            adjusted_buy_duck, adjusted_sell_duck = market_making('DUCK', buy_price_duck, sell_price_duck)
            adjusted_buy_dove, adjusted_sell_dove = market_making('DOVE', buy_price_dove, sell_price_dove)
            adjusted_buy_owl, adjusted_sell_owl = market_making('OWL', buy_price_owl, sell_price_owl)
            adjusted_buy_crow, adjusted_sell_crow = market_making('CROW', buy_price_crow, sell_price_crow)

            if abs(duckAve - buy_price_duck) < 1 and abs(indPos('DUCK'))<20000:
                if adjusted_buy_duck != 0 and adjusted_sell_duck != 0:
                    # if (indPos('DUCK') > 5000):
                    #     place_order('DUCK', 'LIMIT', 2000, adjusted_sell_duck-0.10, 'SELL')
                    #     place_order('DUCK', 'LIMIT', 500, adjusted_buy_duck, 'BUY')
                    #     print("bought for more")
                    #     # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 3000, 'price': adjusted_sell_owl-0.15, 'action': 'SELL'})
                    #     # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 500, 'price': adjusted_buy_owl, 'action': 'BUY'})
                    # elif (indPos('DUCK') < -5000):
                    #     place_order('DUCK', 'LIMIT', 500, adjusted_sell_duck, 'SELL')
                    #     place_order('DUCK', 'LIMIT', 2000, adjusted_buy_duck+0.10, 'BUY')
                    #     print("sold for less")
                    #     # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 3000, 'price': adjusted_buy_owl+0.15, 'action': 'BUY'})
                    #     # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 500, 'price': adjusted_sell_owl, 'action': 'SELL'})
                    # else:
                        place_order('DUCK', 'LIMIT', 2000, adjusted_sell_duck, 'SELL')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_buy_duck, 'BUY')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_sell_duck, 'SELL')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_buy_duck, 'BUY')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_sell_duck, 'SELL')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_buy_duck, 'BUY')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_sell_duck, 'SELL')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_buy_duck, 'BUY')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_sell_duck, 'SELL')
                        place_order('DUCK', 'LIMIT', 2000, adjusted_buy_duck, 'BUY')
                    # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 2000, 'price': adjusted_buy_owl, 'action': 'BUY'})
                    # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 2000, 'price': adjusted_sell_owl, 'action': 'SELL'})
                elif (abs(indPos('DUCK'))>1000):
                    if indPos('DUCK') < 0:
                        place_order('DUCK', 'MARKET', 1000, buy_price_duck, 'BUY')
                    if indPos('DUCK') > 0:
                        place_order('DUCK', 'MARKET', 1000, sell_price_duck, 'SELL')
            elif (abs(indPos('DUCK'))>1000):
                if indPos('DUCK') < 0:
                    place_order('DUCK', 'MARKET', 1000, buy_price_duck, 'BUY')
                if indPos('DUCK') > 0:
                    place_order('DUCK', 'MARKET', 1000, sell_price_duck, 'SELL')
            if abs(doveAve - buy_price_dove) < 0.75:
                if adjusted_buy_dove != 0 and adjusted_sell_dove != 0:
                    if (indPos('DOVE') > 5000):
                        place_order('DOVE', 'LIMIT', 2000, adjusted_sell_dove-0.10, 'SELL')
                        place_order('DOVE', 'LIMIT', 500, adjusted_buy_dove, 'BUY')
                        print("bought for more")
                        # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 3000, 'price': adjusted_sell_owl-0.15, 'action': 'SELL'})
                        # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 500, 'price': adjusted_buy_owl, 'action': 'BUY'})
                    elif (indPos('DOVE') < -5000):
                        place_order('DOVE', 'LIMIT', 500, adjusted_sell_dove, 'SELL')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_buy_dove+0.10, 'BUY')
                        print("sold for less")
                        # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 3000, 'price': adjusted_buy_owl+0.15, 'action': 'BUY'})
                        # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 500, 'price': adjusted_sell_owl, 'action': 'SELL'})
                    else:
                        place_order('DOVE', 'LIMIT', 2000, adjusted_sell_dove, 'SELL')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_buy_dove, 'BUY')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_sell_dove, 'SELL')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_buy_dove, 'BUY')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_sell_dove, 'SELL')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_buy_dove, 'BUY')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_sell_dove, 'SELL')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_buy_dove, 'BUY')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_sell_dove, 'SELL')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_buy_dove, 'BUY')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_sell_dove, 'SELL')
                        place_order('DOVE', 'LIMIT', 2000, adjusted_buy_dove, 'BUY')
                elif (abs(indPos('DOVE'))>1000):
                    if indPos('DOVE') < 0:
                        place_order('DOVE', 'MARKET', 1000, buy_price_dove, 'BUY')
                    if indPos('DOVE') > 0:
                        place_order('DOVE', 'MARKET', 1000, sell_price_dove, 'SELL')
                    
            elif (abs(indPos('DOVE'))>1000):
                if indPos('DOVE') < 0:
                    place_order('DOVE', 'MARKET', 1000, buy_price_dove, 'BUY')
                if indPos('DOVE') > 0:
                    place_order('DOVE', 'MARKET', 1000, sell_price_dove, 'SELL')
            
            # if abs(owlAve - buy_price_owl) < 2.5:
            #     if adjusted_buy_owl != 0 and adjusted_sell_owl != 0:
            #         if (indPos('OWL') > 5000):
            #             place_order('OWL', 'LIMIT', 2000, adjusted_sell_owl-0.10, 'SELL')
            #             place_order('OWL', 'LIMIT', 500, adjusted_buy_owl, 'BUY')
            #             print("bought for more owl")
            #             # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 3000, 'price': adjusted_sell_owl-0.15, 'action': 'SELL'})
            #             # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 500, 'price': adjusted_buy_owl, 'action': 'BUY'})
            #         elif (indPos('OWL') < -5000):
            #             place_order('OWL', 'LIMIT', 500, adjusted_sell_owl, 'SELL')
            #             place_order('OWL', 'LIMIT', 2000, adjusted_buy_owl+0.10, 'BUY')
            #             print("sold for less owl")
            #             # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 3000, 'price': adjusted_buy_owl+0.15, 'action': 'BUY'})
            #             # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 500, 'price': adjusted_sell_owl, 'action': 'SELL'})
            #         else:
            #             place_order('OWL', 'LIMIT', 2000, adjusted_sell_owl, 'SELL')
            #             place_order('OWL', 'LIMIT', 2000, adjusted_buy_owl, 'BUY')
            #             place_order('OWL', 'LIMIT', 2000, adjusted_sell_owl, 'SELL')
            #             place_order('OWL', 'LIMIT', 2000, adjusted_buy_owl, 'BUY')
            #             place_order('OWL', 'LIMIT', 2000, adjusted_sell_owl, 'SELL')
            #             place_order('OWL', 'LIMIT', 2000, adjusted_buy_owl, 'BUY')
            #     elif (abs(indPos('OWL'))>=1000):
            #         if indPos('OWL') < 0:
            #             place_order('OWL', 'MARKET', 1000, buy_price_owl, 'BUY')
            #         elif indPos('OWL') > 0:
            #             place_order('OWL', 'MARKET', 1000, sell_price_owl, 'SELL')
            # elif (abs(indPos('OWL'))>=1000):
            #         if indPos('OWL') < 0:
            #             place_order('OWL', 'MARKET', 1000, buy_price_owl, 'BUY')
            #         elif indPos('OWL') > 0:
            #             place_order('OWL', 'MARKET', 1000, sell_price_owl, 'SELL')

            if abs(crowAve - buy_price_crow) < 2.5:
                if adjusted_buy_crow != 0 and adjusted_sell_crow != 0:
                    if (indPos('CROW') > 5000):
                        place_order('CROW', 'LIMIT', 2000, adjusted_sell_crow-0.10, 'SELL')
                        place_order('CROW', 'LIMIT', 500, adjusted_buy_crow, 'BUY')
                        print("bought for more CROW")
                        # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 3000, 'price': adjusted_sell_owl-0.15, 'action': 'SELL'})
                        # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 500, 'price': adjusted_buy_owl, 'action': 'BUY'})
                    elif (indPos('CROW') < -5000):
                        place_order('CROW', 'LIMIT', 500, adjusted_sell_crow, 'SELL')
                        place_order('CROW', 'LIMIT', 2000, adjusted_buy_crow+0.10, 'BUY')
                        print("sold for less crow")
                        # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 3000, 'price': adjusted_buy_owl+0.15, 'action': 'BUY'})
                        # resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': 500, 'price': adjusted_sell_owl, 'action': 'SELL'})
                    else:
                        place_order('CROW', 'LIMIT', 2000, adjusted_sell_crow, 'SELL')
                        place_order('CROW', 'LIMIT', 2000, adjusted_buy_crow, 'BUY')
                        place_order('CROW', 'LIMIT', 2000, adjusted_sell_crow, 'SELL')
                        place_order('CROW', 'LIMIT', 2000, adjusted_buy_crow, 'BUY')
                        place_order('CROW', 'LIMIT', 2000, adjusted_sell_crow, 'SELL')
                        place_order('CROW', 'LIMIT', 2000, adjusted_buy_crow, 'BUY')
                        place_order('CROW', 'LIMIT', 2000, adjusted_sell_crow, 'SELL')
                        place_order('CROW', 'LIMIT', 2000, adjusted_buy_crow, 'BUY')
                        place_order('CROW', 'LIMIT', 2000, adjusted_sell_crow, 'SELL')
                        place_order('CROW', 'LIMIT', 2000, adjusted_buy_crow, 'BUY')
                        place_order('CROW', 'LIMIT', 2000, adjusted_sell_crow, 'SELL')
                        place_order('CROW', 'LIMIT', 2000, adjusted_buy_crow, 'BUY')
                elif (abs(indPos('CROW'))>=1000):
                    if indPos('CROW') < 0:
                        place_order('CROW', 'MARKET', 1000, buy_price_crow, 'BUY')
                    elif indPos('CROW') > 0:
                        place_order('CROW', 'MARKET', 1000, sell_price_crow, 'SELL')
                elif (abs(indPos('CROW'))>=1000):
                        if indPos('CROW') < 0:
                            place_order('CROW', 'MARKET', 1000, buy_price_crow, 'BUY')
                        elif indPos('CROW') > 0:
                            place_order('CROW', 'MARKET', 1000, sell_price_crow, 'SELL')
            # if (tick<40):
            #     if trendOwl > -50000:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_owl, 'action': 'BUY'})
                    
            #     if trendCrow > -50000:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'CROW', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_crow, 'action': 'BUY'})

            #     if trendDove > -50000:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DOVE', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_dove, 'action': 'BUY'})

            #     if trendDuck > -50000:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DUCK', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_duck, 'action': 'BUY'})

            #     if trendOwl < 50000:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_owl, 'action': 'SELL'})
                    
            #     if trendCrow < 50000:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'CROW', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_crow, 'action': 'SELL'})

            #     if trendDove < 50000:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DOVE', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_dove, 'action': 'SELL'})

            #     if trendDuck < 50000:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DUCK', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_duck, 'action': 'SELL'})

            # if (tick>40) and grossPos < 250000:
            #     if trendOwl > -50000 and buy_price_owl < owlAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_owl-0.01, 'action': 'BUY'})
                    
            #     if trendCrow > -50000 and buy_price_crow < crowAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'CROW', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_crow-0.01, 'action': 'BUY'})

            #     if trendDove > -50000 and buy_price_dove < doveAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DOVE', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_dove-0.01, 'action': 'BUY'})

            #     if trendDuck > -50000 and buy_price_duck < duckAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DUCK', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_duck-0.01, 'action': 'BUY'})

            #     if trendOwl < 50000 and buy_price_owl > owlAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_owl+0.01, 'action': 'SELL'})
                    
            #     if trendCrow < 50000 and buy_price_crow > crowAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'CROW', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_crow+0.01, 'action': 'SELL'})

            #     if trendDove < 50000 and buy_price_dove > doveAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DOVE', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_dove+0.01, 'action': 'SELL'})

            #     if trendDuck < 50000 and buy_price_duck > duckAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DUCK', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_duck+0.01, 'action': 'SELL'})

            # else: 
            #     if trendOwl > -50000 and indPos('OWL') < 0 and buy_price_owl < owlAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_owl, 'action': 'BUY'})
                    
            #     if trendCrow > -50000 and indPos('CROW') < 0 and buy_price_crow < crowAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'CROW', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_crow, 'action': 'BUY'})

            #     if trendDove > -50000 and indPos('DOVE') < 0 and buy_price_dove < doveAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DOVE', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_dove, 'action': 'BUY'})

            #     if trendDuck > -50000 and indPos('DUCK') < 0 and buy_price_duck < duckAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DUCK', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': buy_price_duck, 'action': 'BUY'})
            
            #     if trendOwl < 50000 and indPos('OWL') > 0 and buy_price_owl > owlAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'OWL', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_owl, 'action': 'SELL'})
                    
            #     if trendCrow < 50000 and indPos('CROW') > 0 and buy_price_crow > crowAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'CROW', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_crow, 'action': 'SELL'})

            #     if trendDove < 50000 and indPos('DOVE') > 0 and buy_price_dove > doveAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DOVE', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_dove, 'action': 'SELL'})

            #     if trendDuck < 50000 and indPos('DUCK') > 0 and buy_price_duck > duckAve:
            #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'DUCK', 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': sell_price_duck, 'action': 'SELL'})

            # if position > MAX_SHORT_EXPOSURE:
            #     resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_symbol, 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price, 'action': 'SELL'})

            #took out sleep here

            s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_symbol})

        tick, status = get_tick()

if __name__ == '__main__':
    main()
