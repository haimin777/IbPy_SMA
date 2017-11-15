# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 18:16:20 2017

@author: Haimin
"""
import time
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

    def server_handler(self, msg):
        #print("Server Msg:", msg.typeName, "-", msg) # Для отладки выводим все сообщения системы

        if msg.typeName == "updatePortfolio":
            self.position = msg.position

        elif msg.typeName == "updateAccountValue" and msg.key == "LookAheadAvailableFunds-S":
            self.balance = msg.value

        elif msg.typeName == "orderStatus":
            self.OpenOrders = msg.remaining

        elif msg.typeName == "nextValidId":
            print("order ir = ", msg.orderId)
            self.order_ID = msg.orderId

        elif msg.typeName == "error" and msg.id != -1:
            return

    def monitor_position(self):
        print('Position:%s Bal:%s  Open orders:%s' % (self.position,
                                                      self.balance, self.OpenOrders))

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

        # Assign error handling function.
        self.tws_conn.register(self.error_handler, 'Error')

    def start(self, sec):
        try:
            self.sec = sec  # интервал запуска скрипта
            self.connect_to_tws()
            tws = self.tws_conn
            tws.registerAll(self.server_handler)  # регистрация всех событий, для получения next valid order id
            OrderIB.__init__(OrderIB)
            time.sleep(1)
            self.register_callback_functions()
            time.sleep(1)
            dataLoader = histData.Downloader(debug=False)
            while True:
                self.request_account_updates(self.account_code)
                #            self.request_orders()
                time.sleep(1)
                self.monitor_position()
                time.sleep(1)
                cur_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + str(
                    " GMT")  # запрашиваем текущее время в нужном формате
                contract = OrderIB.create_contract("EUR", "CASH", "IDEALPRO", "USD")
                data = dataLoader.requestData(contract, cur_time, '1 D',
                                              '5 mins', )  # запрашиваем данные для 5 минутных свеч
                ma_long = talib.SMA(data.close.values, timeperiod=80)[-1]  # вычисляем SMA
                ma_short = talib.SMA(data.close.values, timeperiod=10)[-1]

                allow = ma_short < ma_long  # Проверяем сигнал на вход

                # Расчитаем количество лотов, как баланс в тысячах (заходим на весь баланс без рычага)

                OrderIB.quantyty = int(float(self.balance) // 1000 * 1000)

                # Алгоритм системы

                if allow == True and self.position == 0:  # начальная точка
                    if self.OpenOrders != 0:
                        print("Open order detected")

                        sleep(10)
                        continue
                    ib_order = OrderIB.create_order('MKT', OrderIB.quantyty, 'BUY')
                    tws.placeOrder(self.order_ID, contract, ib_order)

                elif allow == False and self.position == 0:
                    if self.OpenOrders != 0:
                        print("Open order detected")

                        sleep(10)
                        continue
                    ib_order = OrderIB.create_order('MKT', OrderIB.quantyty, 'SELL')
                    tws.placeOrder(self.order_ID, contract, ib_order)

                elif allow == True and self.position < 0:  # разворот
                    if self.OpenOrders != 0:
                        print("Open order detected")

                        sleep(10)
                        continue
                    ib_order = OrderIB.create_order('MKT', OrderIB.quantyty * 2, 'BUY')
                    tws.placeOrder(self.order_ID, contract, ib_order)

                elif allow == False and self.position > 0:
                    if self.OpenOrders != 0:
                        print("Open order detected")

                        sleep(10)
                        continue
                    ib_order = OrderIB.create_order('MKT', OrderIB.quantyty * 2, 'SELL')
                    tws.placeOrder(self.order_ID, contract, ib_order)

                print("ma_short = ", ma_short, "ma_long = ", ma_long)
                sleep(self.sec)
        finally:
            #выводим данные при выходе

            print('Position:%s Bal:%s  Open orders:%s' % (self.position,
                                                          self.balance, self.OpenOrders))
            print("disconnected")
            self.disconnect_from_tws()


if __name__ == "__main__":
    system = account_ib("EUR")
    system.start(10)

