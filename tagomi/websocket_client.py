import time, json, warnings, copy, requests, base64
from websocket import WebSocketApp
import asyncio, websockets
from threading import Thread
from tagomi.utils import *
import websocket
from websocket import WebSocketApp, create_connection, WebSocketConnectionClosedException
from urllib.parse import urlencode
websocket.enableTrace(True)

class InsecureRequestWarning(Warning): pass
# warnings.filterwarnings("ignore", message='Unverified HTTPS request is being made. '
#                 'Adding certificate verification is strongly advised. See: '
#                 'https://urllib3.readthedocs.io/en/latest/advanced-usage.html'
#                 '#ssl-warnings')


class TagomiWebsocket:
    def __init__(self, client_id, client_secret, endpoint, params, ws_link='wss://api.tagomi.com/ws/v1/',
                 run_forever=False, verbose=True, debug=False):
        """
        :param client_id: str Tagomi provided api client id
        :param client_secret: str Tagomi provided api client id
        :param endpoint: "book" or "order"
        :param params: dict of epoint params
        :param ws_link: (optional) ws endpoint to connect to
        :param run_forever: (optional) if True listen to all incoming messages
        :param verbose: (optional) print out relevant information
        """

        self._secret = client_secret
        self._id = client_id
        self._access_token = self._get_access_token()
        self._default_account_id = None

        self.verbose = verbose
        self._debug = debug
        self._ws_link = ws_link
        self.run_forever = run_forever
        self.stop = True
        self.error = None
        self._params = params
        self._endpoint = endpoint
        self.last_message = None

        self.ws = None

        self.keepalive = None
        self._thread = None

        if run_forever:
            self.start()
        else:
            self._connect()
            for i in range(4): self.recv()

    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.on_open()
        self._thread = Thread(target=_go)
        self.keepalive = Thread(target=self._keepalive)
        self._thread.start()

    def _connect(self):
        headers = {
            'Authorization': 'Bearer ' + self._access_token
        }
        params = urlencode(self._params)
        self.ws = create_connection(self._ws_link + self._endpoint + '/?' + params, header=headers)

    def _keepalive(self, interval=30):
        while self.ws.connected:
            self.ws.ping("keepalive")
            time.sleep(interval)

    def _listen(self):
        self.keepalive.start()
        while not self.stop:
            try:
                data = self.ws.recv()
                msg = json.loads(data)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(msg)

    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass
        finally:
            self.keepalive.join()

        self.on_close()

    def close(self):
        self.stop = True
        self._disconnect()
        self._thread.join()

    def on_open(self):
        if self.verbose:
            print("-- Subscribed! --\n")

    def on_close(self):
        if self.verbose:
            print("\n-- Socket Closed --")

    def on_message(self, msg):
        self.last_message = msg
        if self.verbose:
            print(msg)

    def get_last_msg(self):
        return copy.deepcopy(self.last_message)

    def on_error(self, e, data=None):
        self.error = e
        self.stop = True
        print('{} - data: {}'.format(e, data))

    def recv(self):
        r = self.ws.recv()
        r = json.loads(r)
        if self.verbose:
            print(r)
        return r

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

    @staticmethod
    def convert_instrumentId(instrumentId):
        return instrument_ids[instrumentId]


if __name__ == "__main__":
    pass
