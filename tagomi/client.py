import json
import base64
import requests
from tagomi.utils import *
import warnings


class InsecureRequestWarning(Warning): pass


warnings.filterwarnings("ignore", message='Unverified HTTPS request is being made. '
                'Adding certificate verification is strongly advised. See: '
                'https://urllib3.readthedocs.io/en/latest/advanced-usage.html'
                '#ssl-warnings')


class TagomiClient:
    def __init__(self, client_id, client_secret):
        self._secret = client_secret
        self._id = client_id
        self._api_url = "https://api.tagomi.com/v1"
        self._access_token = self._get_access_token()
        self._default_account_id = None
        self._update_instruments()

    def _get_access_token(self):
        url = "https://auth.tagomi.com/oauth2/default/v1/token"
        client_info = (self._id + ':' + self._secret).encode("utf-8")
        basic_auth_creds = base64.b64encode(client_info)
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache',
            'Authorization': 'Basic ' + basic_auth_creds.decode("utf-8")
        }

        payload = "grant_type=client_credentials&scope=api&redirect_uri=/"
        response = requests.post(url, data=payload, headers=headers, verify=True).json()
        access_token = response['access_token']

        return access_token

    def _send_request(self, endpoint, account_id=None, params=None, method='GET'):
        acc_id = account_id if account_id is not '' else self._default_account_id
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self._access_token
        }

        params = {} if params is None else params
        if account_id is not None: params['accountId'] = acc_id

        url = "https://api.tagomi.com/v1" + endpoint
        count, resp_code = 0, 401
        while resp_code == 401 and count < 2:
            if method == 'GET':
                response = requests.get(url, data=None, headers=headers, verify=False, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(params))
            elif method == 'DELETE':
                response = requests.delete(url, data=None, headers=headers, verify=False, params=params)
            else:
                raise ValueError("Invalid method")
            count += 1
            resp_code = response.status_code
            if resp_code == 401: self._access_token = self._get_access_token()

        try:
            response = response.json()
        except Exception as e:
            print(response)
            print(response.content)
            raise e
        return response

    def get_instruments(self, account_id='', params=None):
        return self._send_request('/instruments', account_id=account_id, params=params)

    def get_account(self, account_id):
        return self._send_request('/accounts/' + str(account_id))

    def get_accounts(self, params=None):
        return self._send_request('/accounts', params=params)

    def set_default_account_id(self, account_id):
        self._default_account_id = account_id

    def get_balances(self, account_id=None):
        if account_id is None: account_id = self._default_account_id
        if account_id is None: raise ValueError("No accountId specified")
        return self._send_request('/accounts/' + str(account_id) + '/balances')

    def get_order(self, order_id, account_id='', params=None):
        return self._send_request('/orders/' + str(order_id), account_id=account_id, params=params)

    def get_orders(self, account_id='', params=None):
        return self._send_request('/orders', account_id=account_id, params=params)

    def place_order(self, account_id='', params=None):
        if params is None: raise ValueError("Need order info")
        return self._send_request('/orders', account_id=account_id, params=params, method='POST')

    def cancel_order(self, order_id, account_id='', params=None):
        return self._send_request('/orders/' + str(order_id), method='DELETE', account_id=account_id, params=params)

    def get_deposits(self, account_id='', params=None):
        return self._send_request('/deposits', account_id=account_id, params=params)

    def get_withdrawals(self, account_id='', params=None):
        return self._send_request('/withdrawals', account_id=account_id, params=params)

    def get_trade(self, trade_id, account_id='', params=None):
        return self._send_request('/trades/' + str(trade_id), account_id=account_id, params=params)

    def get_trades(self, account_id='', params=None):
        return self._send_request('/trades', account_id=account_id, params=params)

    def get_market_data(self, bookType, instrumentId):
        return self._send_request('/books/' + str(bookType) + '/' + str(instrumentId))

    def _update_instruments(self):
        new_instruments = self.get_instruments()
        for ins in new_instruments:
            instrument_ids[ins['id']] = ins['symbol']

    @staticmethod
    def convert_instrumentId(instrumentId):
        return instrument_ids[instrumentId]
