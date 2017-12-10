# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 18:16:20 2017

@author: Haimin
"""

import histData  # через него получаем исторические данные как датафрейм

from order import OrderIB
# from account import AccountIB
import talib
from ib.opt import Connection, message, ibConnection

import datetime
from time import sleep
import random


class account_ib:
    def __init__(self, port=7496):
        self.client_id = 100
        #self.symbol = symbol
        self.port = port
        self.tws_conn = None
        self.account_code = None
        self.position = 0
        self.balance = 0
        self.order_ID = None
        self.OpenOrders = 0
        self.statusOrder = None
        self.list1_orders = []  # Открытые ордера: Тикер и цена
        self.pos_list = []  # Активные позиции: тикер, размер позиции, рыночная стоимость, цена
        self.list2_orders = list()  # Открытые ордера: Объем и статус
        self.current_order_status = None
        self.currency = ["EUR", "CHF", "AUD"]
        self.trade_pos_list = []

    def position_handler(self, msg):

        if msg.typeName == "nextValidId":
            print("order id = ", msg.orderId)
            self.order_ID = msg.orderId

        elif msg.typeName == "orderStatus":

            print("___________order placed__________", "\n", "id: ",
                  msg.orderId, "order status: ", msg.status)
            self.current_order_status = msg.status
            sleep(1)

            #elif msg.typeName == "orderStatus" and msg.orderId == self.order_ID-1:
            #print("___----___")

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

        elif msg.typeName == "position":  #запрос позиций в торговом цикле
           # print("POS here", "\n", msg.contract.m_symbol)

            self.trade_pos_list.append(msg.contract.m_symbol)
            self.trade_pos_list.append(msg.pos)


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

    def connect_to_tws(self):
        self.tws_conn = Connection.create(port=self.port,
                                          clientId=self.client_id)
        self.tws_conn.connect()

        print("Connected")

    def error_handler(self, msg):
        if msg.typeName == "error" and msg.id != -1:
            print("Server Error:", msg)

    def request_account_updates(self, account_code):
        self.tws_conn.reqAccountUpdates(True, account_code)
        self.tws_conn.reqAllOpenOrders()

    def disconnect_from_tws(self):
        if self.tws_conn is not None:
            self.tws_conn.disconnect()

    def register_callback_functions(self):
        # Assign server messages handling function.
        self.tws_conn.registerAll(self.server_handler)
        # self.tws_conn.registerAll(self.position_handler)
        # Assign error handling function.
        self.tws_conn.register(self.error_handler, 'Error')

    def cross_signal(self):  # функция для определения сигнала

        allow = random.randint(0,1)
        return allow

    def trade_logic(self, data_loader, pos_volume):

        allow = self.cross_signal()  # Проверяем сигнал на вход
        #allow = 1
        self.contract = OrderIB.create_contract(self.currency[random.randint(0, 2)],
                                                "CASH", "IDEALPRO", "USD")

        # Проверяем позицию по созданному контракту
        self.tws_conn.reqPositions()
        sleep(1)
        #print(self.trade_pos_list)
        print("placed order for:  ", self.contract.m_symbol)

        #print(self.trade_pos_list.index(self.contract.m_symbol))

        if allow == 1: # если есть сигнал на покупку
                    # и позиция по тикеру открыта, то идем дальше
            try:
                self.trade_pos_list.index(self.contract.m_symbol)
                print("\n", "opened long position", "\n")
            except ValueError: # если позиции нет то открываем
                 self.ib_order = OrderIB.create_order('MKT', pos_volume, 'BUY')
                 return self.ib_order

        elif allow == 0: #если сигнал на продажу и есть позиция по
                         # по этому тикеру, продаем имеющееся количество
            try:
                n = self.trade_pos_list.index(self.contract.m_symbol)
                print("\n", "signal to close long position", "\n", allow)
                print(self.trade_pos_list[n+1])
                self.ib_order = OrderIB.create_order('MKT',
                         abs(self.trade_pos_list[n+1]), 'SELL')

            except ValueError:
                 self.ib_order = OrderIB.create_order('MKT', pos_volume, 'SELL')
                 return self.ib_order

    def start(self, sec):
        try:
            self.sec = sec  # интервал запуска скрипта
            self.connect_to_tws()
            tws = self.tws_conn

            # Запрашиваем и выводим информацию о позициях и ордерах перед запуском скрипта

            tws.registerAll(self.server_handler)
            self.register_callback_functions()
            data_loader = histData.Downloader(debug=False)
            self.request_account_updates(self.account_code)
            sleep(1)
            self.monitor_position()
            sleep(1)

            while True:
                tws.registerAll(self.position_handler)
                self.register_callback_functions()
                # Расчитаем количество лотов, как баланс в тысячах (заходим на весь баланс без рычага)
                pos_volume = int(float(self.balance) // 1000 * 100)
                print("\n", "last placed order status:", "\n", self.current_order_status)
                # Алгоритм системы
                self.trade_logic(data_loader, pos_volume)
                try:
                    tws.placeOrder(self.order_ID, self.contract, self.ib_order)
                    self.order_ID += 1
                except AttributeError:
                    print("already placed")
                finally:

                    sleep(self.sec)

        finally:

            # выводим данные при выходе

            print("\n", 'Position:%s Bal:%s  Open orders:%s' % (self.position,
                                                                self.balance, self.OpenOrders))
            print("disconnected")
            self.disconnect_from_tws()


if __name__ == "__main__":
    system = account_ib()
    system.start(20)
