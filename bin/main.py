import urlparse
import threading
import time
import Queue
import logging
from ConfigParser import RawConfigParser
from flask import Flask, render_template
from cbapi import CbApi
from syslog_server import SyslogServer
from action import FlushAction, RunLiveResponseScriptAction
from tempfile import NamedTemporaryFile
import sqlite3
import sys

logging.getLogger("requests").setLevel(logging.WARNING)


live_response_results = dict()
live_response_lock = threading.Lock()
live_response_actions = []


def add_response_action(action):
    print ("Adding action: %s" % action.name())
    live_response_actions.append(action)


def get_flask_server():
    flask_server = Flask('liveresponse')

    @flask_server.route('/', methods=['GET', 'POST'])
    def index():
        with live_response_lock:
            return render_template('index.html', sensors=live_response_results.keys())

    @flask_server.route('/sensor_result/<sensor_id>')
    def sensor_result(sensor_id):
        sensor_id = int(sensor_id)
        with live_response_lock:
            results = live_response_results.get(sensor_id, {})
            if 'results' in results:
                return render_template('sensor_result.html', results=results['results'], sensor_id=sensor_id)
            else:
                return render_template('no_such_result.html')

    @flask_server.route('/browser_history/<sensor_id>')
    def browser_history(sensor_id):
        sensor_id = int(sensor_id)
        with live_response_lock:
            results = live_response_results.get(sensor_id, {})
            if 'results' in results and 'browser_history' in results['results']:
                with NamedTemporaryFile(delete=False) as tf:
                    tf.write(results['results']['browser_history'])
                    tf.close()
                    db = sqlite3.connect(tf.name)
                    db.row_factory = sqlite3.Row
                    cur = db.cursor()
                    cur.execute("SELECT url, title, datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), 'unixepoch') as last_visit_time FROM urls ORDER BY last_visit_time DESC")
                    urls = [dict(u) for u in cur.fetchall()]

                    for url in urls:
                        (scheme, netloc, _, _, _) = urlparse.urlsplit(url["url"])
                        url["favicon"] = urlparse.urlunsplit((scheme, netloc, "favicon.ico", "", ""))

                    return render_template('browser_history.html', urls=urls)

            return render_template('no_such_result.html')

    t = threading.Thread(target=flask_server.run, args=['127.0.0.1', 7982])
    t.daemon = True
    return t


class FanOutMessage(threading.Thread):
    def __init__(self, cb, worker_queue, output_queue, logger):
        self.cb = cb
        self.worker_queue = worker_queue
        self.output_queue = output_queue
        self.logger = logger

        threading.Thread.__init__(self)

    def run(self):
        while True:
            sensor_id = self.worker_queue.get()
            with live_response_lock:
                if sensor_id in live_response_results:
                    if live_response_results[sensor_id]['active']:
                        self.worker_queue.task_done()
                        continue

                # otherwise, let's claim this sensor
                live_response_results[sensor_id] = dict()
                live_response_results[sensor_id]['active'] = True

            try:
                for action in live_response_actions:
                    self.logger.warn('Dispatching action %s on sensor id %s' % (action.name(), sensor_id))
                    resp = action.action(sensor_id)
                    if resp:
                        with live_response_lock:
                            live_response_results[sensor_id]['results'] = resp
                        # self.output_queue.put((sensor_id, action.shortname(), resp))
            except Exception as e:
                import traceback
                traceback.print_exc()
            finally:
                with live_response_lock:
                    live_response_results[sensor_id]['active'] = False
                self.worker_queue.task_done()


class LiveResponseOrchestrator(object):
    def __init__(self, cb_server, token):
        self.cb = CbApi(cb_server, token=token, ssl_verify=False)
        self.worker_queue = Queue.Queue(maxsize=10)
        self.output_queue = Queue.Queue()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig()

    def run(self):
        self.logger.info("Cb Live Response Orchestrator starting")

        t = get_flask_server()
        t.start()

        syslog_server = SyslogServer(10240, self.worker_queue, self.logger)
        syslog_server.daemon = True

        for i in range(10):
            message_broker = FanOutMessage(self.cb, self.worker_queue, self.output_queue, self.logger)
            message_broker.daemon = True
            message_broker.start()

        # Note: it is important to keep the relative order stable here.
        # we want to make sure that the Cb sensor flush occurs first, before the feed entry is created
        # and before any other actions are taken (isolation or process termination)

        # We will always flush the sensor that triggered the action, so that we get the most up-to-date
        # information into the Cb console.
        flusher = FlushAction(self.cb, self.logger)
        add_response_action(flusher)

        # isolator = IsolateAction(self.cb, self.logger)
        # message_broker.add_response_action(isolator)

        run_live_response = RunLiveResponseScriptAction(self.cb, self.logger)
        add_response_action(run_live_response)

        # once everything is up & running, start the message broker then the syslog server
        syslog_server.start()

        self.logger.info("Starting event loop")

        try:
            while True:
                sys.stdout.write("Enter sensor ID to test: ")
                sys.stdout.flush()
                sensor_string = sys.stdin.readline()
                try:
                    sensor_string = sensor_string.strip().lower()
                    sensor_id = int(sensor_string)
                except ValueError:
                    if sensor_string == 'quit' or sensor_string == 'exit':
                        return 0
                else:
                    self.worker_queue.put(sensor_id)
        except KeyboardInterrupt:
            self.logger.warn("Stopping Cb Live Response Orchestrator due to Control-C")

        return 0


if __name__ == '__main__':
    config_data = RawConfigParser()
    config_data.read("../connection.ini")

    cb_server = config_data.get('cb_server', 'url')
    token = config_data.get('cb_server', 'token')

    orchestrator = LiveResponseOrchestrator(cb_server, token=token)
    orchestrator.run()
