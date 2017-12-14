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
from connect import connect_ib
from account import account_info

class account_ib:
    def __init__(self, port=7496):
        self.client_id = 100
        self.port = port
        self.tws_conn = None
        #self.account_code = None
        self.position = 0
        self.OpenOrders = 0
        self.statusOrder = None
        self.list1_orders = []  # Открытые ордера: Тикер и цена
        self.pos_list = []  # Активные позиции: тикер, размер позиции, рыночная стоимость, цена
        self.list2_orders = list()  # Открытые ордера: Объем и статус
        self.current_order_status = None



    def cross_signal(self, data_loader):  # функция для определения пересечения
        # запрашиваем текущее время в нужном формате
        self.cur_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + \
                        str(" GMT")

        self.contract = OrderIB.create_contract("EUR",
                                                "CASH",
                                                "IDEALPRO",
                                                "USD")
        data = data_loader.requestData(self.contract,
                                       self.cur_time,
                                       '1 D',
                                       '5 mins', )  # запрашиваем данные для 5 минутных свеч
        ma_long = talib.SMA(data.close.values, timeperiod=80)[-1]  # вычисляем SMA
        ma_short = talib.SMA(data.close.values, timeperiod=10)[-1]
        allow = ma_short > ma_long
        return allow

    def trade_logic(self, data_loader, pos_volume):
        allow = self.cross_signal(data_loader)  # Проверяем сигнал на вход
        print("allow: ", allow)
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

    def start(self, sec, connect_ib, account_info):
        try:
            # Запрашиваем и выводим информацию о позициях и ордерах перед запуском скрипта
            acc_inf = account_info()
            acc_inf.start_info(connect_ib)
            sleep(1)
            tws = connect_ib.tws_conn
            data_loader = histData.Downloader(debug=False)

            while True:
               # tws.registerAll(account_info.position_handler)
               # self.register_callback_functions()
                # Расчитаем количество лотов, как баланс в тысячах (заходим на весь баланс без рычага)
                #pos_volume = 1000
                pos_volume = int(float(acc_inf.balance) // 1000 * 100)
                print("\n", "last placed order status:", "\n", self.current_order_status)
                # Алгоритм системы

                tws.reqPositions()
                self.trade_logic(data_loader, pos_volume)

                try:
                    tws.placeOrder(acc_inf.order_ID,
                                   self.contract,
                                   self.ib_order)
                    acc_inf.order_ID += 1
                except AttributeError:
                    print("already placed")
                finally:
                    sleep(sec)

        finally:
            # выводим данные при выходе
            print("\n",
                  'Position:%s Bal:%s  '
                  'Open orders:%s' %
                  (acc_inf.position,
                   acc_inf.balance,
                   acc_inf.OpenOrders))
            connect_ib.disconnect(connect_ib)


if __name__ == "__main__":
  #  system = account_info()
  #  system.start_info(connect_ib)
  #  connect_ib.disconnect(connect_ib)

   system = account_ib()
   system.start(20, connect_ib, account_info)
