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

    # Get trades
    print("\nORDERS")
    orders = tc.get_orders(params={'limit': 1000})
    real_orders = []
    for order in orders:
        if order['filledQty'] > 0:  # The fill qty is how much actually traded, this filters to all completed/partial
            real_orders.append(order)
    print(len(orders), orders[:len(orders)//10])
    print(len(real_orders), real_orders, '\n')

    # Get orders
    print("TRADES")
    trades = tc.get_trades(params={'limit': 1000})
    print(len(trades), trades[:len(trades)//10], '\n')

    # Get deposits
    print("DEPOSITS")
    real_deps = []
    deposits = tc.get_deposits(params={'limit': 1000})
    for deposit in deposits:
        if deposit['status'] == 'Completed':  # "Completed" activity are the only ones that should have gone through
            real_deps.append(deposit)
    print(len(deposits), deposits)
    print(len(real_deps), real_deps, '\n')

    # Get withdrawals
    print("WITHDRAWALS")
    real_withs = []
    withdrawals = tc.get_withdrawals(params={'limit': 1000})
    for withdrawal in withdrawals:
        if withdrawal['status'] == 'Completed':  # "Completed" activity are the only ones that should have gone through
            real_withs.append(withdrawal)
    print(len(withdrawals), withdrawals)
    print(len(real_withs), real_withs, '\n')

    w = real_withs[0]
    print(tc.convert_instrumentId(w['instrumentId']), w)
