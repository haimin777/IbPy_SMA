# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 17:34:25 2017

@author: Haimin
"""

from ib.opt import Connection
from time import sleep

class connect_ib:
    def __init__(self):
        self.client_id = 100
        self.port = 7496
        self.tws_conn = None

    def connect(self):
        try:
            self.__init__(self)
            self.tws_conn = Connection.create(port=self.port,
                                     clientId=self.client_id)
            self.tws_conn.connect()

        finally:
            print("Connection Ok")

    def disconnect(self):
        if self.tws_conn is not None:
            self.tws_conn.disconnect()
            print("Disconnect OK")

if __name__ == "__main__":
    system = connect_ib()
    system.connect()
    sleep(1)
    system.disconnect()