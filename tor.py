import os
import socket
import requests
import time

import socks
import stem.process
from stem import Signal
from stem.control import Controller
from user_agent import generate_user_agent


class Network:

    def switch_ip(self):
        self.controller.signal(Signal.NEWNYM)
        time.sleep(self.controller.get_newnym_wait())

    def print_bootstrap_lines(self, line):
        print(line)

    def init_tor(self, password='supersafe', log_handler=None):
        self.tor_process = None
        self.controller = None

        try:
            self.tor_process = stem.process.launch_tor_with_config(
                tor_cmd=self.tor_path,
                config=self.tor_config,
                init_msg_handler=log_handler
            )

            self.controller = Controller.from_port(port=self.SOCKS_PORT + 1)
            self.controller.authenticate(password)

        except:
            if self.tor_process is not None:
                self.tor_process.terminate()
            if self.controller is not None:
                self.controller.close()

            raise RuntimeError('Failed to initialize Tor')

        socket.socket = self.proxySocket

    def kill_tor(self):
        print('Killing Tor process')
        if self.tor_process is not None:
            self.tor_process.kill()

        if self.controller is not None:
            self.controller.close()

    def __init__(self):

        TOR_DIR = '/Applications/TorBrowser.app/Contents/Resources/TorBrowser/Tor/'
        PASS_HASH = '16:DEBBA657C88BA8D060A5FDD014BD42DB7B5B736C0C248422F37C46B930'
        IP_ADDRESS = '127.0.0.1'
        self.SOCKS_PORT = 9050

        self.tor_config = {
            'SocksPort': str(self.SOCKS_PORT),
            'ControlPort': str(self.SOCKS_PORT + 1),
            'HashedControlPassword': PASS_HASH,
            'GeoIPFile': os.path.join(TOR_DIR, 'geoip'),
            'GeoIPv6File': os.path.join(TOR_DIR, 'geoip6')
        }

        self.tor_path = os.path.join(TOR_DIR, 'tor')
        # Setup proxy
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, IP_ADDRESS, self.SOCKS_PORT)

        self.nonProxySocket = socket.socket
        self.proxySocket = socks.socksocket


def main():

    try:
        network = Network()
        network.init_tor('supersafe', network.print_bootstrap_lines)

        url = 'http://checkip.amazonaws.com/'
        headers = {'User-Agent': generate_user_agent()}

        req = requests.get(url, headers=headers)
        print(req.content)
        network.switch_ip()
        req = requests.get(url, headers=headers)
        print(req.content)
    finally:
        network.kill_tor()

if __name__ == "__main__":
    main()