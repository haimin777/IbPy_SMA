from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection

class OrderIB:
    def __init__(self):
        self.quantyty = 0
        self.order_ID = 1

    def error_handler(msg):
        print("Server Error:", msg)

    def error_handler(msg):
        print("Server Error:", msg)


    def server_handler(msg):
        print("Server Msg:", msg.typeName, "-", msg)


    def create_contract(symbol, sec_type, exch, curr):
        contract = Contract()
        contract.m_symbol = symbol
        contract.m_secType = sec_type
        contract.m_exchange = exch
        contract.m_currency = curr
        return contract


    def create_order(order_type, quantity, action):
        order = Order()
        order.m_orderType = order_type
        order.m_totalQuantity = quantity
        order.m_action = action

        return order

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
        tws_conn.register(OrderIB.error_handler, 'Error')

        # Assign server messages handling function.
        tws_conn.registerAll(OrderIB.server_handler)

        # Create AAPL contract and send order
        aapl_contract = OrderIB.create_contract('EUR', 'CASH','IDEALPRO','USD')

        # Go long 100 shares of AAPL
        aapl_order = OrderIB.create_order('MKT', 1001, 'SELL')

        # Place order on IB TWS.
        tws_conn.placeOrder(order_id, aapl_contract, aapl_order)
        print("Order placed", order_id)
    finally:
        # Disconnect from TWS
        if tws_conn is not None:
            tws_conn.disconnect()