import sys

sys.path.append('/home/haimin777/Quantum/IbPy_SMA/api')
sys.path.append('/home/haimin777/Quantum/IbPy_SMA/algorithms')
from connect import ConnectIB
from account import AccountInfo
from rand_trade import logic_random
from order import OrderIB
from time import sleep


def start(sec):
    # подключаемся и выводим начальные данные
    acc_inf = AccountInfo()
    acc_inf.start_info(ConnectIB)
    tws = ConnectIB.tws_conn
    while True:

        positions = acc_inf.trade_positions()
        trade = logic_random(positions, pos_volume=100000)

        if trade is not None:
            contract = OrderIB.create_contract(trade[0],
                                               "CASH",
                                               "IDEALPRO",
                                               "USD")
            order = OrderIB.create_order(trade[1][0], trade[1][1], trade[1][2])
            tws.placeOrder(acc_inf.order_ID,
                           contract,
                           order)
            acc_inf.order_ID += 1
            sleep(sec)
        else:
            sleep(sec)


if __name__ == "__main__":
    start(10)
    ConnectIB.disconnect(ConnectIB)
