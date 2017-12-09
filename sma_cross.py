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


class account_ib:
    def __init__(self, symbol, port=7496):
        self.client_id = 100
        self.symbol = symbol
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

    def cross_signal(self, data_loader):  # функция для определения пересечения
        self.cur_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + str(
            " GMT")  # запрашиваем текущее время в нужном формате
        self.contract = OrderIB.create_contract("EUR", "CASH", "IDEALPRO", "USD")
        data = data_loader.requestData(self.contract, self.cur_time, '1 D',
                                       '5 mins', )  # запрашиваем данные для 5 минутных свеч
        ma_long = talib.SMA(data.close.values, timeperiod=80)[-1]  # вычисляем SMA
        ma_short = talib.SMA(data.close.values, timeperiod=10)[-1]

        allow = ma_short > ma_long
        return allow

    def trade_logic(self, data_loader, pos_volume):

        allow = self.cross_signal(data_loader)  # Проверяем сигнал на вход

        if allow:  # проверка пересечения

            print("\n", "signal to open long position", "\n")

            if self.position == 0:
                self.ib_order = OrderIB.create_order('MKT', pos_volume, 'BUY')

            elif self.position < 0:  # выставляем ордер с учетом перекрытия текущей позиции

                self.ib_order = OrderIB.create_order("MKT", abs(self.position) + pos_volume, "BUY")

            return self.ib_order

        elif not allow:
            print("\n", "signal to open short position", "\n")

            if self.position == 0:
                self.ib_order = OrderIB.create_order('MKT', pos_volume, 'SELL')
            elif self.position > 0:
                # перворачиваем текущую длинную позицию
                self.ib_order = OrderIB.create_order("MKT", abs(self.position) + pos_volume, "SELL")
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
                pos_volume = int(float(self.balance) // 1000 * 1000)
                print("\n", "last placed order status:", "\n", self.current_order_status)
                # Алгоритм системы
                self.trade_logic(data_loader, pos_volume)
                tws.placeOrder(self.order_ID, self.contract, self.ib_order)

                sleep(self.sec)

        finally:

            # выводим данные при выходе

            print("\n", 'Position:%s Bal:%s  Open orders:%s' % (self.position,
                                                                self.balance, self.OpenOrders))
            print("disconnected")
            self.disconnect_from_tws()


if __name__ == "__main__":
    system = account_ib("EUR")
    system.start(10)
