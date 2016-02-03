#
# Just log into /tmp/myactiveresponse.log
#

#
# TODO:
# Ask Kyle how dependencies are handled
#
from __future__ import absolute_import
from ConfigParser import RawConfigParser
from action import FlushAction, IsolateAction
from cbapi import CbApi
import json
import requests

class Device:
    path = "dummy.log"

    def __init__(self, hosts_mapping):
        #
        # WARNING/TODO:
        # be sure to test the current path we get from splunk so we can read the config file
        #
        config_data = RawConfigParser()
        config_data.read("config.ini")

        self.cb_server = config_data.get('cb_server', 'url')
        self.token = config_data.get('cb_server', 'token')

        self.cb = CbApi(self.cb_server, token=self.token, ssl_verify=False)

        self.logger = ""

        self.fp = open("/tmp/arlog1.log", "a")
        self.hosts_mapping = hosts_mapping
        self.fp.write("Initializing with hosts mapping: %s\n" % str(hosts_mapping))
        self.fp.close()

    def blacklist_binary(self, md5):
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

        r = requests.post("https://%s/api/v1/banning/blacklist" % (self.cb_server),
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
                    return sensor.get('id', '')
        return ''

    def submit_action(self, settings, data):
        """
        This gets called when the user executes a search
        :param settings:
        :param data:
        :return:
        """
        self.fp = open("/tmp/arlog1.log", "a")
        self.fp.write("*** Submit action with settings[%s] and data[%s]\n" % (str(settings), str(data)))
        self.fp.close()

    def run_action(self, settings, data):
        """
        This gets called when the user clicks the validate button
        :param settings:
        :param data:
        :return:
        """
        print "run_action ENTER"
        """
        settings:
        [{'action_type': 'banhash', 'flow': 'submit', 'group': 'Z5tLJDgLfSBvItEdSjPK', 'b64records': '', 'path': 'dummy.log',
        'fieldname': 'src_ip', 'fieldvalue': '10.11.6.5'}]
        and
        data :
        [{'dest_ip': '119.147.138.52', 'src_ip': '10.11.6.5'}]
        """
        action_type = settings[0].get('action_type', '')
        if action_type == 'banhash':
            pass
        elif action_type == 'isolate':
            pass
        elif action_type == 'flush':

            sensor_id = self.get_sensor_id_from_ip(data[0].get('src_ip'))
            if not sensor_id:
                return

            print "Flushing sensor id: %s" % sensor_id
            #
            # We will always flush the sensor that triggered the action, so that we get the most up-to-date
            # information into the Cb console.
            #
            flusher = FlushAction(self.cb, self.logger)
            flusher.action(sensor_id)
            pass
        else:
            return
