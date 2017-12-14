from connect import connect_ib
from account import account_info
from rand_trade import logic_random
from order import OrderIB
from time import sleep

def start(sec):
    #подключаемся и выводим начальные данные
    acc_inf = account_info()
    acc_inf.start_info(connect_ib)
    tws = connect_ib.tws_conn
    while True:

        positions = acc_inf.trade_positions()

        a = logic_random(positions, pos_volume= 20000)
        #print(a[1][0])
        if a != None:
            contract = OrderIB.create_contract(a[0],
                                                "CASH",
                                                "IDEALPRO",
                                                "USD")
            order = OrderIB.create_order(a[1][0], a[1][1], a[1][2])
            tws.placeOrder(acc_inf.order_ID,
                           contract,
                           order)
            acc_inf.order_ID +=1
            sleep(sec)
        else:
            sleep(sec)

if __name__ == "__main__":
    start(10)
    connect_ib.disconnect(connect_ib)