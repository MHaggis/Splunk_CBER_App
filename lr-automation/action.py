import time
from live_response import LiveResponseThread


class Action(object):
    def __init__(self, cb, logger):
        self.cb = cb
        self.logger = logger

    def name(self):
        return self.__class__.__name__


class FlushAction(Action):
    def __init__(self, cb, logger):
        Action.__init__(self, cb, logger)

    def action(self, sensor_id):
        flush_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time() + 86400))
        self.cb.sensor_flush(sensor_id, flush_time)

    def name(self):
        return 'Flush sensor information'


class IsolateAction(Action):
    def __init__(self, cb, logger):
        Action.__init__(self, cb, logger)

    def action(self, sensor_id):
        self.cb.sensor_toggle_isolation(sensor_id, True)

    def name(self):
        return 'Isolate affected sensor'


class RunLiveResponseScript(LiveResponseThread):
    def run(self):
        self.success = False

        try:
            self.establish_session()
            self.logger.info("Gathering running services")
            self.running_services = self.create_process("c:\\windows\\system32\\net.exe start")
            self.logger.info("Gathering running processes")
            self.running_processes = self.get_processes()

            # get the current user
            users = set([proc['username'].split('\\')[-1]
                         for proc in self.running_processes if proc['path'].find('explorer.exe') != -1])

            for user in users:
                self.logger.info("Gathering Chrome browser history for %s" % user)
                self.browser_history = \
                    self.get_file("c:\\users\\%s\\appdata\\local\\google\\chrome\\user data\\default\\history" % user)

            self.logger.info("LR done")
        except Exception as e:
            import traceback
            traceback.print_exc()
        else:
            self.success = True

    def get_results(self):
        if self.success:
            return {'running_services': self.running_services.decode('latin-1'),
                    'running_processes': self.running_processes,
                    'browser_history': self.browser_history}
        else:
            return None


class RunLiveResponseScriptAction(Action):
    def __init__(self, cb, logger):
        Action.__init__(self, cb, logger)

    def action(self, sensor_id):
        print "Starting live response against sensor %d" % sensor_id
        lr_thread = RunLiveResponseScript(self.cb, self.logger, sensor_id)
        lr_thread.start()
        lr_thread.join()
        return lr_thread.get_results()

    def name(self):
        return 'Run live response script'

    def shortname(self):
        return 'liveresponse'
