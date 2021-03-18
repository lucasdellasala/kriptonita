import websocket, json, pprint, talib, numpy
from tabulate import tabulate
import csv
import config
import ssl
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05
SALDO = 0.10

closes = []

c = csv.writer(open('operaciones.csv', mode="a"), lineterminator='\n')
c.writerow(['ORDER SIDE','TRADE QUANTITY', 'CLOSE VALUE', 'TRADE SYMBOL', 'LAST RSI', 'SALDO'])

in_position = False
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

counterMsg = 0
def on_message(ws, message):
    global closes, in_position, counterMsg

    counterMsg = counterMsg + 1
    print('\rReceiving messages ({})'.format(counterMsg), end='')
    #for dot in range(counterMsg):
    #    print('.', end='')
    json_message = json.loads(message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        counterMsg = 0
        closeValue = float(candle['c'])
        openValue = float(candle['o'])
        closeTime = float(candle['T'])
        openTime = float(candle['t'])
        slope=round((closeValue-openValue)/(closeTime-openTime), 7)

        print('\n')
        print('{}\t{}\t{}\t{}\t{}'.format(openTime, closeTime, openValue, closeValue, slope))
        print('\n')
        

        closes.append(float(close))
        
        if len(closes) > RSI_PERIOD:
            print("Closes")     
            only_last_14_closes = closes[-14:]
            print(only_last_14_closes)
            print('\n')

            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)

            print("RSI LISTS:")
            if len(rsi) > 10:
                only_last_10_rsi = rsi[-10:]
                print(only_last_10_rsi)
                print('\n')
            else:
                print(rsi)
                print('\n')

            last_rsi = rsi[-1]
            print("The current rsi is {}".format(last_rsi))
            print('\n')

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    #print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    #order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    SALDO = SALDO - TRADE_QUANTITY
                    order_succeeded = True
                    order_operation = ["Sell",TRADE_QUANTITY,close,TRADE_SYMBOL,last_rsi, SALDO]
                    print("ORDER SUCCEEDED: SELL")
                    print(order_operation)
                    print('\n')

                    c.writerow(order_operation)

                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    #print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    #order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    SALDO = SALDO + TRADE_QUANTITY
                    order_succeeded = True
                    order_operation = ["Buy",TRADE_QUANTITY,close,TRADE_SYMBOL,last_rsi,SALDO]
                    print("ORDER SUCCEEDED: BUY")
                    print(order_operation)
                    print('\n')

                    c.writerow(order_operation)

                    if order_succeeded:
                        in_position = True
        else:
            print("Closes")        
            print(closes)
            print('\n')

def on_error(ws, error):
    print(error)
                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})