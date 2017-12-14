# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 18:16:20 2017

@author: Haimin
"""


from ib.opt import Connection, message, ibConnection
import time
from connect import connect_ib


class account_info:

    def __init__(self):

        self.tws_conn = None
        self.account_code = None
        self.position = 0
        self.balance = 1
        self.order_ID = None
        self.OpenOrders = 0
        self.statusOrder = None
        self.list1_orders = []  # Открытые ордера: Тикер и цена
        self.pos_list = []  # Активные позиции: тикер, размер позиции, рыночная стоимость, цена
        self.list2_orders = list()  # Открытые ордера: Объем и статус
        self.trade_pos_list = {}

    def position_handler(self, msg):

        if msg.typeName == "nextValidId":
            print("order id = ", msg.orderId)
            self.order_ID = msg.orderId

        elif msg.typeName == "orderStatus":

            print("___________order placed__________", "\n", "id: ",
                  msg.orderId, "order status: ", msg.status)
            self.current_order_status = msg.status
            sleep(1)


    def server_handler(self, msg):
        #print("Server Msg:", msg.typeName, "-", msg) # Для отладки выводим все сообщения системы

        if msg.typeName == "updatePortfolio":
            self.position = msg.position
            self.pos_list.append(msg.contract.m_symbol)
            self.pos_list.append(msg.position)
            self.pos_list.append(msg.marketValue)
            self.pos_list.append(msg.marketPrice)


        elif msg.typeName == "updateAccountValue" and msg.key == "LookAheadAvailableFunds-S":
            self.balance = msg.value

        elif msg.typeName == "orderStatus":
            self.OpenOrders = msg.remaining
            self.statusOrder = msg.status
            self.list2_orders.append(self.OpenOrders)
            self.list2_orders.append(msg.status)

        elif msg.typeName == "nextValidId":
            print("order id = ", msg.orderId)
            self.order_ID = msg.orderId

        elif msg.typeName == "openOrder":

            self.list1_orders.append(msg.contract.m_symbol)
            self.list1_orders.append(msg.order.m_lmtPrice)

        elif msg.typeName == "position":  # запрос позиций в торговом цикле
           # print("POS here", "\n", msg.contract.m_symbol)
            self.trade_pos_list.update({msg.contract.m_symbol :  msg.pos})


        elif msg.typeName == "error" and msg.id != -1:
            return

    def monitor_position(self):  # Отслеживаем открытые позиции и ордера
        print('Position:%s Bal:%s  Open orders:%s' % (self.position,
                                                      self.balance, self.OpenOrders))

        print("_____________Open orders_____________", "\n")

        for i in range(0, len(self.list1_orders), 2):
            print(self.list1_orders[i], self.list1_orders[i + 1], self.list2_orders[i], self.list2_orders[i + 1])

        print("____________Open positions___________", "\n", self.pos_list)
        self.list1_orders.clear()
        self.list2_orders.clear()
        self.pos_list.clear()

    def operation_status(self):  # выводим статус заявки, созданной алгоритмом

        print("______new order signal_______", "\n")
        self.tws_conn.reqOpenOrders()
        self.tws_conn.registerAll(self.position_handler)


        
    def error_handler(self, msg):
        if msg.typeName == "error" and msg.id != -1:
            print ("Server Error:", msg)
            
    def request_account_updates(self, account_code):
        self.tws_conn.reqAllOpenOrders()
        self.tws_conn.reqAccountUpdates(True, account_code)

    def register_callback_functions(self):
        # Assign server messages handling function.
        self.tws_conn.registerAll(self.server_handler)


        # Assign error handling function.
        self.tws_conn.register(self.error_handler, 'Error')
    def start_info(self, conect_ib):
        account_info.__init__(account_info)
        connect_ib.connect(connect_ib)
        self.tws_conn = connect_ib.tws_conn
        self.tws_conn.registerAll(self.server_handler)
        time.sleep(1)
        self.register_callback_functions()
        time.sleep(1)
        self.request_account_updates(self.account_code)
        time.sleep(1)
        self.monitor_position()

    def trade_positions(self):   #вывод позиций в процессе работы
        self.tws_conn.reqPositions()
        time.sleep(1)
        self.register_callback_functions()
        print(self.trade_pos_list)
        return self.trade_pos_list

    def start(self, connect_ib):
        try:
            account_info.__init__(account_info)
            #connect_ib.__init__(connect_ib)

            connect_ib.connect(connect_ib)
            self.tws_conn = connect_ib.tws_conn
            self.tws_conn.registerAll(self.server_handler)

            time.sleep(1)
            self.request_account_updates(self.account_code)
            time.sleep(1)
            self.monitor_position()
            #print(self.order_ID, "tttttt")
            self.trade_positions()

        finally:
            connect_ib.disconnect(connect_ib)
            print ("disconnected")

        
if __name__ == "__main__":
    system = account_info()
    system.start(connect_ib)
    print(system.trade_pos_list)

    
