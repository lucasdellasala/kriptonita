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

# Usar estos valores de closes para probar el Sell o el Buy, quizas haya que actualizar los valores al valor del ETH actual
#closesParaProbarSell = [1800.95, 1800.52, 1810.88, 1811.94, 1812.0, 1813.71, 1814.06, 1815.19, 1816.21, 1817.85, 1818.07, 1825.32, 1828.01, 1830.18]
#closesParaProbarBuy = [1890.95, 1880.52, 1870.88, 1861.94, 1852.0, 1843.71, 1834.06, 1833.19, 1832.21, 1831.85, 1831.07, 1830.32, 1829.01, 1828.18]

closes =[]

c = csv.writer(open('operaciones.csv', mode="a"), lineterminator='\n')
c.writerow(['ORDER SIDE','CLOSE TIME','TRADE QUANTITY', 'CLOSE VALUE', 'TRADE SYMBOL', 'LAST RSI', 'SALDO'])

can_i_buy = True
buys = 0
sells = 0
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

counterMsg = 0
def on_message(ws, message):
    global closes, buys, sells, can_i_buy, counterMsg, SALDO, RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD, TRADE_SYMBOL, TRADE_QUANTITY

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
            print('Ultimo movimiento: ')

            last_rsi = rsi[-1]
            print("The current rsi is {}".format(last_rsi))
            print('\n')

            if last_rsi > RSI_OVERBOUGHT:
                if SALDO >= TRADE_QUANTITY:
                    #print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    #order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    SALDO = SALDO - TRADE_QUANTITY
                    order_succeeded = True
                    order_operation = ["Sell",closeTime,TRADE_QUANTITY,closeValue,TRADE_SYMBOL,last_rsi, SALDO]
                    print("ORDER SUCCEEDED: SELL")
                    print(order_operation)
                    print('\n')

                    c.writerow(order_operation)
                    sells = sells + 1
                    can_i_buy = True
                else:
                    print("No tengo SALDO {}".format(TRADE_SYMBOL))
            if last_rsi < RSI_OVERSOLD:
                if can_i_buy:
                    print('HOLA')
                    #print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    #order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    SALDO = SALDO + TRADE_QUANTITY
                    order_succeeded = True
                    order_operation = ["Buy",closeTime,TRADE_QUANTITY,closeValue,TRADE_SYMBOL,last_rsi,SALDO]
                    print("ORDER SUCCEEDED: BUY")
                    print(order_operation)
                    print('\n')
                    
                    c.writerow(order_operation)
                    buys = buys + 1
                    can_i_buy = False
                else:
                    print("Puedo comprar una sola vez, el resto lo voy acumulando")


            print('Puedo comprar? ')
            print(can_i_buy)
            print('Saldo: ')
            print(SALDO)
            print('Nº de compras: {}'.format(buys))
            print('Nº de ventas: {}'.format(sells))
            print('\n')
                
        else:
            print("Closes")        
            print(closes)
            print('\n')
            print('Puedo comprar? ')
            print(can_i_buy)
            print('Saldo: ')
            print(SALDO)
            print('Nº de compras: {}'.format(buys))
            print('Nº de ventas: {}'.format(sells))
            print('\n')

def on_error(ws, error):
    print(error)
                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})