#!/usr/bin/python
# Parts of this have been copied from Splunks DNSLookup and other examples.
# You can sumbit up to 25 "resources" to VT, however this script does not do that.

from cbapi import CbApi
from ConfigParser import RawConfigParser
import os
import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option


@Configuration()
class ProcessSearchCommand(GeneratingCommand):
    """Generates a process search result from Carbon Black from a given IP or search query
        | processsearch ${ip}
    """

    query = Option(name="query", require=True)

    field_names = ['childproc_count',
                   'cmdline',
                   'comms_ip',
                   'crossproc_count',
                   'filemod_count',
                   'group',
                   'host_type',
                   'hostname',
                   'id',
                   'interface_ip',
                   'last_update',
                   'modload_count',
                   'netconn_count',
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
                   'username']

    def prepare(self):
        config_data = RawConfigParser()
        my_path = os.path.dirname(os.path.abspath(__file__))
        config_data.read(os.path.join(my_path, "config.ini"))

        cb_server = config_data.get('cb_server', 'url')
        token = config_data.get('cb_server', 'token')

        self.cb = CbApi(cb_server, token=token, ssl_verify=False)

    def generate(self):
        for bindata in self.cb.process_search_iter(self.query):
            yield dict((field_name, bindata[field_name]) for field_name in self.field_names)

if __name__ == '__main__':
    dispatch(ProcessSearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)