#!/usr/bin/python
# Parts of this have been copied from Splunks DNSLookup and other examples.
# You can sumbit up to 25 "resources" to VT, however this script does not do that.

from cbapi import CbApi
from ConfigParser import RawConfigParser
import os
import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import time
import dateutil.parser
import json


@Configuration()
class ProcessSearchCommand(GeneratingCommand):
    """Generates a process search result from Carbon Black from a given IP or search query
        | processsearch query=${ip}
    """

    query = Option(name="query", require=True)

    field_names = ['cmdline',
                   'comms_ip',
                   'hostname',
                   'id',
                   'interface_ip',
                   'last_update',
                   'os_type',
                   'parent_md5',
                   'parent_name',
                   'parent_pid',
                   'parent_unique_id',
                   'path',
                   'process_md5',
                   'process_name',
                   'process_pid',
                   'regmod_count',
                   'segment_id',
                   'sensor_id',
                   'start',
                   'unique_id',
                   'username',
                   'childproc_count',
                   'crossproc_count',
                   'modload_count',
                   'netconn_count',
                   'filemod_count',
                   'group',
                   'host_type']

    def prepare(self):
        config_data = RawConfigParser()
        my_path = os.path.dirname(os.path.abspath(__file__))
        config_data.read(os.path.join(my_path, "config.ini"))

        self.cb_server = config_data.get('cb_server', 'url')
        self.token = config_data.get('cb_server', 'token')

        self.cb = CbApi(self.cb_server, token=self.token, ssl_verify=False)

    def generate(self):
        self.logger.info("query %s" % self.query)
        for bindata in self.cb.process_search_iter(self.query):
            temp = dict((field_name, bindata[field_name]) for field_name in self.field_names)
            temp['sourcetype'] = 'bit9:carbonblack:json'

            #
            # Sometimes we have seen 'start' be equal to -1
            #
            try:
                temp['_time'] = int(time.mktime(dateutil.parser.parse(bindata['start']).timetuple()))
            except Exception as e:
                self.logger.exception('parsing bindata["start"] %s' % bindata['start'])
                temp['_time'] = 0

            temp['host'] = self.cb_server + '/#/analyze/' + bindata['id'] + "/1"
            temp['source'] = 'cbapi'
            temp['_raw'] = json.dumps(temp)
            yield temp

if __name__ == '__main__':
    dispatch(ProcessSearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
