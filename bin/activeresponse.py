from __future__ import absolute_import
from ConfigParser import RawConfigParser
from cbaction import FlushAction, IsolateAction, KillProcessAction
from cbapi import CbApi
import json
import requests
import logging
logging.basicConfig()
import os
import six


class PrerequisiteFailedError(Exception):
    pass


class Device(object):
    path = "carbonblack.endpoint"

    def __init__(self, hosts_mapping):
        #
        # WARNING/TODO:
        # be sure to test the current path we get from splunk so we can read the config file
        #
        config_data = RawConfigParser()
        my_path = os.path.dirname(os.path.abspath(__file__))
        config_data.read(os.path.join(my_path, "config.ini"))

        self.cb_server = config_data.get('cb_server', 'url')
        self.token = config_data.get('cb_server', 'token')

        self.cb = CbApi(self.cb_server, token=self.token, ssl_verify=False)

        self.logger = logging.getLogger(__name__)

        self.hosts_mapping = hosts_mapping

    def ban_hash(self, md5):
        """
        Performs a POST to the Carbon Black Server API for blacklisting an MD5 hash
        :param md5:
        :return:
        """

        print "blacklisting md5:%s" % (md5)

        headers = {'X-AUTH-TOKEN': self.token}

        data = {"md5hash": md5,
                "text": "Blacklist From Splunk",
                "last_ban_time": 0,
                "ban_count": 0,
                "last_ban_host": 0,
                "enabled": True}

        print "connecting to: %s/api/v1/banning/blacklist..." % (self.cb_server)

        r = requests.post("%s/api/v1/banning/blacklist" % (self.cb_server),
                          headers=headers,
                          data=json.dumps(data),
                          verify=False)

        if r.status_code == 409:
            print "This md5 hash is already blacklisted"
        elif r.status_code == 200:
            print "Carbon Black Server API Success"
        else:
            print "CarbonBlack Server API returned an error: %d" % (r.status_code)
            print "Be sure to check the Carbon Black API token"

    def get_sensor_id_from_ip(self, ip):
        filters = {}
        sensors = self.cb.sensors(filters)

        for sensor in sensors:
            src_ip = filter(bool, sensor.get('network_adapters', '').split('|'))
            for ip_address in src_ip:
                if unicode(ip, "utf-8") == ip_address.split(',')[0]:
                    return sensor.get('id', None)
        return None

    def pre_action(self, action_type, data):
        if action_type in ['isolate', 'flush']:
            src_ip = data.get('src_ip', None) or data.get('local_ip', None)
            if not src_ip:
                raise PrerequisiteFailedError("No source IP address provided")
            sensor_id = self.get_sensor_id_from_ip(src_ip)
            if not sensor_id:
                raise PrerequisiteFailedError("Cannot find sensor associated with source IP address %s" % src_ip)

            return sensor_id
        elif action_type in ['killproc']:
            proc_id = data.get('process_guid', None)
            if not proc_id:
                raise PrerequisiteFailedError("No Process GUID provided")
            if not isinstance(proc_id, six.string_types):
                raise PrerequisiteFailedError("Process GUID not valid: must be a string")
            if len(proc_id.split("-")) < 5:
                raise PrerequisiteFailedError("Process GUID not valid: must be a GUID")
            return proc_id
        elif action_type in ['banhash']:
            #
            # Pull out md5 from 'data'
            #
            md5 = data.get('md5', None)
            if not md5:
                #
                # Error out if we can't
                #
                raise PrerequisiteFailedError("Error: Unable to get an MD5 hash from parameters")
            return md5

        return None

    def submit_action(self, settings, data):
        """
        This gets called when the user executes a search
        :param settings:
        :param data:
        :return:
        """

        action_type = settings.get('action_type', '')
        try:
            sensor_id = self.pre_action(action_type, data)
        except PrerequisiteFailedError as e:
            # TODO: how do we signal failure back to ARF ARFARFARF
            self.logger.error(e.message)

        # TODO: return success

    def flush_action(self, sensor_id):
        print "Flushing sensor id: %s" % sensor_id
        #
        # We will always flush the sensor that triggered the action, so that we get the most up-to-date
        # information into the Cb console.
        #
        flusher = FlushAction(self.cb, self.logger)
        flusher.action(sensor_id)

    def isolate_action(self, sensor_id):
        isolator = IsolateAction(self.cb, self.logger)
        isolator.action(sensor_id)

    def kill_action(self, process_id):
        killer = KillProcessAction(self.cb, self.logger)
        killer.action(process_id)

    def run_action(self, settings, data):
        """
        This gets called when the user clicks the validate button
        :param settings:
        :param data:
        :return:
        """
        action_type = settings.get('action_type', '')
        # get sensor ID if required
        try:
            action_argument = self.pre_action(action_type, data)
        except PrerequisiteFailedError as e:
            self.logger.error(e.message)
        else:
            if action_type == 'banhash':
                self.ban_hash(action_argument)
            elif action_type == 'isolate':
                self.isolate_action(action_argument)
            elif action_type == 'flush':
                self.flush_action(action_argument)
            elif action_type == 'killproc':
                self.kill_action(action_argument)
