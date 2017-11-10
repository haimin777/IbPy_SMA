# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 17:34:25 2017

@author: Haimin
"""

from ib.opt import Connection


def error_handler(msg):
    print ("Server Error:", msg)


def server_handler(msg):
    print ("Server Msg:", msg.typeName, "-", msg)


if __name__ == "__main__":
    client_id = 100
    order_id = 1
    port = 7496
    tws_conn = None
    
try:
    # Establish connection to TWS.
    tws_conn = Connection.create(port=port,
                                 clientId=client_id)
    tws_conn.connect()
    # Assign error handling function.
    tws_conn.register(error_handler, 'Error')
    # Assign server messages handling function.
    tws_conn.registerAll(server_handler)
    print("Connection Ok")
finally:
    # Disconnect from TWS
    if tws_conn is not None:
        tws_conn.disconnect()