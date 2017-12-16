# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 18:16:20 2017

@author: Haimin
"""
import sys

sys.path.append('/home/haimin777/Quantum/IbPy_SMA/api')
# sys.path.append('/home/haimin777/Quantum/IbPy_SMA/algorithms')
import histData  # через него получаем исторические данные как датафрейм

from order import OrderIB
# from account import AccountIB
import talib
from ib.opt import Connection, message, ibConnection

import datetime
from time import sleep
from connect import ConnectIB
from account import AccountInfo


class AccountIB:
    def __init__(self):
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

    def trade_logic(self, position, data_loader, pos_volume):
        allow = self.cross_signal(data_loader)  # Проверяем сигнал на вход
        print("allow: ", allow)
        # Обновляем дынные по позициям

        if allow:  # проверка пересечения
            print("\n", "signal to open long position", "\n")
            if position == 0:
                self.ib_order = OrderIB.create_order('MKT', pos_volume, 'BUY')
            elif position < 0:  # выставляем ордер с учетом перекрытия текущей позиции
                self.ib_order = OrderIB.create_order("MKT", abs(self.position) + pos_volume, "BUY")
            return self.ib_order
        elif not allow:
            print("\n", "signal to open short position", "\n")
            if position == 0:
                self.ib_order = OrderIB.create_order('MKT', pos_volume, 'SELL')
            elif position > 0:
                # перворачиваем текущую длинную позицию
                self.ib_order = OrderIB.create_order("MKT", abs(self.position) + pos_volume, "SELL")
            return self.ib_order

    def start(self, sec, ConnectIB, AccountInfo):
        try:
            # Запрашиваем и выводим информацию о позициях и ордерах перед запуском скрипта
            acc_inf = AccountInfo()
            acc_inf.start_info(ConnectIB)
            sleep(1)
            tws = ConnectIB.tws_conn
            data_loader = histData.Downloader(debug=False)

            while True:
                position = acc_inf.position
                pos_volume = int(float(acc_inf.balance) // 1000 * 100)
                print("\n", "last placed order status:", "\n", self.current_order_status)
                # Алгоритм системы

                tws.reqPositions()
                self.trade_logic(position, data_loader, pos_volume)

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
                   acc_inf.open_orders))
            ConnectIB.disconnect(ConnectIB)


if __name__ == "__main__":
    #  system = AccountInfo()
    #  system.start_info(ConnectIB)
    #  ConnectIB.disconnect(ConnectIB)

    system = AccountIB()
    system.start(20, ConnectIB, AccountInfo)
