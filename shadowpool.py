# -*- coding: utf-8 -*-
import argparse
from io import BytesIO
import logging
import os
import json
import signal
import socket
import subprocess
import time
import random


CHECK_INTERVAL = 3 * 60

logger = logging.getLogger(__name__)

def setup_log():
    consoleHandler = logging.StreamHandler()
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)


class ServerPool(object):
    def __init__(self, conf_path):
        self.conf_path = conf_path
        with open(conf_path) as conf_file:
            self.configs = json.loads(conf_file.read())
        self.current_server = "{}:{}".format(self.configs['server'], self.configs['server_port'])

    def switch(self):
        for server in self.configs['pool']:
            if can_connect(server):
                break
        self.current_server = server
        host, port = server.split(':')
        port = int(port)
        self.configs['server'] = host
        self.configs['server_port'] = port

        logger.warning('Switching to {}.'.format(server))

        with open(self.conf_path, 'w') as conf_file:
            conf_file.write(json.dumps(self.configs, indent=4))


def can_connect(server):
    try:
        host, port = server.split(':')
        port = int(port)
        conn = socket.create_connection((host, port), timeout=5)
        conn.close()
        return True
    except socket.error:
        return False


def main():
    setup_log()

    parser = argparse.ArgumentParser(description='Shadowsocks Pooling')
    parser.add_argument('-c', dest="config", default="/opt/shadowsocks/config.json", help='path to the shadowsocks file')
    args = parser.parse_args()

    pool = ServerPool(args.config)

    ss_process = None
    try:
        while True:
            if ss_process and can_connect(pool.current_server):
                time.sleep(CHECK_INTERVAL)
            else:
                if ss_process:
                    os.killpg(ss_process.pid, signal.SIGTERM)
                pool.switch()
                ss_process = subprocess.Popen(["sslocal", '-c', pool.conf_path], stdout=subprocess.PIPE,
                                preexec_fn=os.setsid)
                time.sleep(60)
    except KeyboardInterrupt:
        if ss_process:
            os.killpg(ss_process.pid, signal.SIGTERM)
        return

if __name__ == '__main__':
    main()
