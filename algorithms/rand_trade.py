# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 18:16:20 2017

@author: Haimin
"""
import sys

sys.path.append('/home/haimin777/Quantum/IbPy_SMA/api')

import random


def logic_random(positions, pos_volume):
    if random.randint(0, 1):
        # let's trade
        pair = random.choice(['EUR', 'CHF', 'GBP'])

        if positions[pair] == 0:
            # позиция отсутствует, будем торговать в одном из направлений
            if random.randint(0, 1):
                print('open long from zero for ', pair)
                # buy
                order_info = ['MKT', pos_volume, 'BUY']

                return pair, order_info
            else:
                # sell
                print('open short from zero for ', pair)
                order_info = ['MKT', pos_volume, 'SELL']

                return pair, order_info
        elif positions[pair] > 0:
            # у нас лонг, будем закрывать
            print('close long for ', pair)
            order_info = ['MKT', positions[pair], 'SELL']

            return pair, order_info
        elif positions[pair] < 0:
            # у нас шорт, будем крыть
            print('close short for ', pair)
            order_info = ['MKT', abs(positions[pair]), 'BUY']

            return pair, order_info
    else:
        print('No signal')

        # return pair, order_info
