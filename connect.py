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

    def error_handler(self, msg):
        print ("Server Error:", msg)


    def server_handler(self, msg):
        print ("Server Msg:", msg.typeName, "-", msg)


#if __name__ == "__main__":
#    client_id = 100
#    order_id = 1
#    port = 7496
#    tws_conn = None
    
    def connect(self):
        try:
            self.tws_conn = Connection.create(port=self.port,
                                     clientId=self.client_id)
            self.tws_conn.connect()
    # Assign error handling function.
            self.tws_conn.register(self.error_handler, 'Error')
    # Assign server messages handling function.
            self.tws_conn.registerAll(self.server_handler)
         #   print("Connection Ok")
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