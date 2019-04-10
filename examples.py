import time, os
from tagomi import *


if __name__ == "__main__":

    API_ID = os.environ['tagomi_api_id']
    API_SECRET = os.environ['tagomi_api_secret']

    tc = TagomiClient(client_id=API_ID, client_secret=API_SECRET)
    r = tc.get_accounts()
    print(r)
    api_acc = r[0]['id']
    print(api_acc)
    time.sleep(2)
    tc.set_default_account_id(api_acc)

    r2 = tc.get_orders()
    print(len(r2), r2)
    for item in r2: print(item)
    print()

    # r2 = tc.get_order(order_id='05W9DZFC08EB4C5LH0ET')
    # print(5, len(r2), r2)

    # r2 = tc.get_order(order_id='05W9DZFC08EB4C5LH0ET')
    # print(5, len(r2), r2)
    #
    # r2 = tc.cancel_order(order_id='05W9DZFC08EB4C5LH0ET')
    # print(5, len(r2), r2)

    # r2 = tc.get_instruments()
    # print(r2)

    # r2 = tc.get_account(account_id=api_acc)
    # print(r2)
    #
    # r2 = tc.get_balances(account_id=api_acc)
    # print(r2)
    #
    # r2 = tc.get_deposits(account_id=api_acc)
    # print(r2)
    #
    # r2 = tc.get_withdrawals(account_id=api_acc)
    # print(r2)
    #
    # r2 = tc.get_trades(account_id=api_acc)
    # print(r2)

    # r2 = tc.get_orders(params={"orderId": '05W9DZFC08EB4C5LH0ET'})
    # print(1, r2)

    order_info = {
      # "clOrdId": "string",
      # "accountId": 0,
      "instrument": "ETH/USD",
      "orderType": "StopLimit",
      # "timeInForce": "Day",
      "stopPrice": 200,
      "price": 200.1,
      "side": "B",
      # "stopPrice": 0,
      "size": 0.1,
      # "createUser": "string",
      "strategy": "Stop",
      # "destination": "string",
      # "startTime": "2019-02-26T21:53:55Z",
      # "endTime": "2019-02-26T21:53:55Z"
    }

    r2 = tc.place_order(account_id=api_acc, params=order_info)
    print(r2)
    # for order in r2: print(order)
    # r = tc.get_open_orders()
    # print(r)



