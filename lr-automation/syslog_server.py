__author__ = 'cb'

import threading
import socket
import re

class SyslogServer(threading.Thread):
    def __init__(self, syslog_port, worker_queue, logger):
        self.syslog_port = syslog_port
        self.worker_queue = worker_queue
        self.logger = logger
        self.format_string = \
            re.compile('reason=watchlist\.hit.*sensor_id=(\d+)')
        threading.Thread.__init__(self)

    def run(self):
        try:
            syslog_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            listen_addr = ("", self.syslog_port)
            syslog_socket.bind(listen_addr)

            while True:
                data, addr = syslog_socket.recvfrom(2048)
                data = data.strip()
                self.logger.info("Got packet: %s" % data)
                hit = self.format_string.search(data)
                if hit:
                    self.worker_queue.put(int(hit.group(1)))
        except:
            import traceback
            self.logger.error('%s' % traceback.format_exc())

