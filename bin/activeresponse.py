#
# Just log into /tmp/myactiveresponse.log
#
from __future__ import absolute_import
import time


class Device:
    path = "dummy.log"

    def __log(self, msg):
        self.fp.write("[%s] %s\n" % (time.ctime(), msg))
        pass

    def __init__(self, hosts_mapping):
        print("The device is being initialized")
        self.hosts_mapping = hosts_mapping

    def submit_action(self, settings, results):
        log_file = settings["log_file"]
        log_fp = open(log_file, "a")
        log_fp.write("[SUBMIT] AR_Log settings=\"%s\" and results:[[%s]]\n" % (str(settings), str(results)))
        log_fp.close() 

    def run_action(self, settings, results):
        log_file = settings["log_file"]
        log_fp = open(log_file, "a")
        log_fp.write("Running the action with data:%s\n" % str(results))
        log_fp.close()

    def undo_action(self):
        self.__log("I am undoing the action")
        pass

    def fetch_feedback(self):
        self.__log("I am fetching the feedback")
        pass

    def expiration(self):
        self.__log("I am running the expiration")
        pass

