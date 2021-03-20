import csv

c = csv.writer(open('operaciones.csv', mode="a"), lineterminator='\n')
c.writerow(['ORDER SIDE','CLOSE TIME','TRADE QUANTITY', 'CLOSE VALUE', 'TRADE SYMBOL', 'LAST RSI', 'SALDO'])


order_operation = ["Buy",123124,0.5,1820,"ETHUSDT",29.1,0.15]
print("ORDER SUCCEEDED: BUY")
print(order_operation)
print('\n')

c.writerow(order_operation)