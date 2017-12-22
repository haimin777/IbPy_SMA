# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 18:16:20 2017

@author: Haimin
"""

import time
from api.connect import ConnectIB


class AccountInfo:
    def __init__(self):
        self.tws_conn = None
        self.account_code = None
        self.position = 0
        self.balance = 1
        self.order_id = None
        self.open_orders = 0
        self.status_order = None        
        self.pos_list = []  # Активные позиции: тикер, размер позиции, рыночная стоимость, цена
        self.init_order_list = list()  # Открытые ордера на момент запуска
        self.trade_pos_list = {}

    def position_handler(self, msg):

        if msg.typeName == "nextValidId":
            print("order id = ", msg.order_id)
            self.order_id = msg.orderId

        elif msg.typeName == "orderStatus":

            print("___________order placed__________", "\n", "id: ",
                  msg.orderId, "order status: ", msg.status)
            self.current_order_status = msg.status
            sleep(1)

    def server_handler(self, msg):
        # print("Server Msg:", msg.typeName, "-", msg) # Для отладки выводим все сообщения системы

        if msg.typeName == "updatePortfolio":
            self.position = msg.position
            self.pos_list.append(msg.contract.m_symbol)
            self.pos_list.append(msg.position)
            self.pos_list.append(msg.marketValue)
            self.pos_list.append(msg.marketPrice)

        elif msg.typeName == "updateAccountValue" and msg.key == "LookAheadAvailableFunds-S":
            self.balance = msg.value

        elif msg.typeName == "orderStatus":
            self.open_orders = msg.remaining
            self.status_order = msg.status
            self.init_order_list.append(self.open_orders)
            self.init_order_list.append(msg.status)

        elif msg.typeName == "openOrder":
             self.init_order_list.append(msg.contract.m_symbol)
             self.init_order_list.append(msg.order.m_lmtPrice)

        elif msg.typeName == "nextValidId":
            print("order id = ", msg.orderId)
            self.order_id = msg.orderId


        elif msg.typeName == "position":  # запрос позиций в торговом цикле
            # print("POS here", "\n", msg.contract.m_symbol)
            self.trade_pos_list.update({msg.contract.m_symbol: msg.pos})


        elif msg.typeName == "error" and msg.id != -1:
            return

    def monitor_position(self):  # Отслеживаем открытые позиции и ордера
        print('Position:%s Bal:%s  Open orders:%s' % (self.position,
                                                      self.balance, self.open_orders))
       # print(self.init_order_list)

        print("_____________Open orders_____________", "\n")

        for i in range(0, len(self.init_order_list),4):
            for j in range(0,4):
                print(self.init_order_list[i+j], end=" ")
            print("\n")

        print("____________Open positions___________", "\n", self.pos_list)
        self.init_order_list.clear()
        self.pos_list.clear()

    def operation_status(self):  # выводим статус заявки, созданной алгоритмом

        print("______new order signal_______", "\n")
        self.tws_conn.reqopen_orders()
        self.tws_conn.registerAll(self.position_handler)

    def error_handler(self, msg):
        if msg.typeName == "error" and msg.id != -1:
            print("Server Error:", msg)

    def request_account_updates(self, account_code):
        self.tws_conn.reqAllOpenOrders()
        self.tws_conn.reqAccountUpdates(True, account_code)

    def register_callback_functions(self):
        # Assign server messages handling function.
        self.tws_conn.registerAll(self.server_handler)

        # Assign error handling function.
        self.tws_conn.register(self.error_handler, 'Error')

    def start_info(self, conect_ib):
        AccountInfo.__init__(AccountInfo)
        ConnectIB.connect(ConnectIB)
        self.tws_conn = ConnectIB.tws_conn
        self.tws_conn.registerAll(self.server_handler)
        time.sleep(1)
        self.register_callback_functions()
        time.sleep(1)
        self.request_account_updates(self.account_code)
        time.sleep(1)
        self.monitor_position()

    def trade_positions(self):  # вывод позиций в процессе работы
        self.tws_conn.reqPositions()
        time.sleep(1)
        self.register_callback_functions()
        print(self.trade_pos_list)
        return self.trade_pos_list

    def start(self, ConnectIB):
        try:
            AccountInfo.__init__(AccountInfo)
            ConnectIB.connect(ConnectIB)
            self.tws_conn = ConnectIB.tws_conn
            self.tws_conn.registerAll(self.server_handler)

            time.sleep(1)
            self.request_account_updates(self.account_code)
            time.sleep(1)
            self.monitor_position()
            self.trade_positions()

        finally:
            ConnectIB.disconnect(ConnectIB)
            print("disconnected")


if __name__ == "__main__":
    system = AccountInfo()
    system.start(ConnectIB)
    print(system.trade_pos_list)
