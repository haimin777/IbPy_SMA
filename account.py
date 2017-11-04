# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 18:16:20 2017

@author: Haimin
"""

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection, message
import datetime


class AccountIB:
    def __init__(self, symbol, port=7496):
        self.client_id = 100
        self.symbol = symbol
        self.port = port
        self.tws_conn = None
        self.account_code = None
        self.position = 0
        self.balance = 10
        
    def server_handler(self, msg):
       #print ("Server Msg:", msg.typeName, "-", msg)
                  
        if msg.typeName == "updatePortfolio":
            self.position = msg.position
        elif msg.typeName == "updateAccountValue" and msg.key == "LookAheadAvailableFunds-S":    
            self.balance = msg.value
            
        elif msg.typeName == "error" and msg.id != -1:
            return
   
    def monitor_position(self):
        print ('Position:%s Bal:%s' % (self.position,
                                               self.balance))

    def connect_to_tws(self):
        self.tws_conn = Connection.create(port=self.port,
                                          clientId=self.client_id)
        self.tws_conn.connect()
        print("Connected")
        
    def error_handler(self, msg):
        if msg.typeName == "error" and msg.id != -1:
            print ("Server Error:", msg)
            
    def request_account_updates(self, account_code):
        self.tws_conn.reqAccountUpdates(True, account_code)
        
    def disconnect_from_tws(self):
        if self.tws_conn is not None:
            self.tws_conn.disconnect()
            
    def register_callback_functions(self):
        # Assign server messages handling function.
        self.tws_conn.registerAll(self.server_handler)

        # Assign error handling function.
        self.tws_conn.register(self.error_handler, 'Error')

               
    def start(self):
        try:
            self.connect_to_tws()
            sleep(1)
            self.register_callback_functions()
            sleep(1)
            self.request_account_updates(self.account_code)
            sleep(1)
            self.monitor_position()
            
           
            
        finally:
            print ("disconnected")
            self.disconnect_from_tws()
        
if __name__ == "__main__":
    system = AccountIB("EUR")
    system.start()
    
