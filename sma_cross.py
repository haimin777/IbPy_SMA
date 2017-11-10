# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 17:34:25 2017

@author: Haimin
"""

import histData # через него получаем исторические данные ка датафрейм
from histData import Downloader
from order import OrderIB
from account import AccountIB
import talib
from ib.opt import Connection, message, ibConnection
import tradingWithPython as twp
import datetime
from time import sleep

def error_handler(msg):
    print("Server Error:", msg)


def server_handler(msg):
    print("Server Msg:", msg.typeName, "-", msg)
    if msg.typeName == "updatePortfolio":
        AccountIB.position = msg.position

    elif msg.typeName == "updateAccountValue" and msg.key == "LookAheadAvailableFunds-S":
        AccountIB.balance = msg.value

    elif msg.typeName == "nextValidId":
        print("order ir = ", msg.orderId)
        OrderIB.order_ID = msg.orderId

if __name__ == "__main__":
    client_id = 100
    order_id = 1
    port = 7496
    tws = None
    account_code = None
try:
    # Подключаемся к системе
    tws = Connection.create(port=port,
                                 clientId=client_id)


    tws.connect()

    # Осуществляем запись ошибок и ответов сервера
    tws.register(error_handler, 'Error')

    tws.registerAll(server_handler)
    print("Connection Ok")



    # ---check for correct version
    print('twp version', twp.__version__)
    dataLoader = histData.Downloader(debug=False)
    # запускаем цикл каждые 5 минут (300 сек)
    while True:

          # Загружаем исторические данные
        cur_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + str(
            " GMT")  # запрашиваем текущее время в нужном формате
        contract = OrderIB.create_contract("EUR", "CASH", "IDEALPRO", "USD")
        data = dataLoader.requestData(contract, cur_time, '1 D', '5 mins', )  # запрашиваем данные для 5 минутных свеч
        ma_long = talib.SMA(data.close.values, timeperiod=80)[-1]  #вычисляем SMA
        ma_short = talib.SMA(data.close.values, timeperiod=10)[-1]

        allow = ma_short < ma_long
        AccountIB.__init__(AccountIB, symbol="EUR", port=7496)
        AccountIB.tws_conn = tws

        AccountIB.request_account_updates(AccountIB, AccountIB.account_code)
        sleep(1)
#
    # расчитаем количество лотов, как баланс в тысячах (заходим на весь баланс без рычага)

        OrderIB.quantyty = int(float(AccountIB.balance)//1000*1000)
# Алгоритм системы
        if allow == True and AccountIB.position == 0: # начальная точка

            ib_order = OrderIB.create_order('MKT',OrderIB.quantyty, 'BUY')
            tws.placeOrder(OrderIB.order_ID, contract, ib_order)
        elif allow == False and AccountIB.position == 0:

            ib_order = OrderIB.create_order('MKT',OrderIB.quantyty, 'SELL')
            tws.placeOrder(OrderIB.order_ID, contract, ib_order)
        elif allow == True and AccountIB.position < 0:  # разворот

            ib_order = OrderIB.create_order('MKT', OrderIB.quantyty*2, 'BUY')
            tws.placeOrder(OrderIB.order_ID, contract, ib_order)
        elif allow == False and AccountIB.position > 0:

            ib_order = OrderIB.create_order('MKT', OrderIB.quantyty * 2, 'SELL')
            tws.placeOrder(OrderIB.order_ID, contract, ib_order)

        print("sma long = ", ma_long, "sma short = ", ma_short)
        print(AccountIB.balance, AccountIB.position, "OrderId = ", OrderIB.order_ID)
        sleep(10)
finally:
    # Disconnect from TWS
    if tws is not None:
        tws.disconnect()
        print("tws disconnected")


