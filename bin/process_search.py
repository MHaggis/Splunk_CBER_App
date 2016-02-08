#!/usr/bin/python
# Parts of this have been copied from Splunks DNSLookup and other examples.
# You can sumbit up to 25 "resources" to VT, however this script does not do that.

import re, collections, json, csv, sys, urllib, urllib2, splunk.Intersplunk, string
from cbapi import CbApi
from ConfigParser import RawConfigParser

def main():
    (isgetinfo, sys.argv) = splunk.Intersplunk.isGetInfo(sys.argv)
    if len(sys.argv) < 2:
        splunk.Intersplunk.parseError("No arguments provided")
        # print "python vt.py MD5 VT"
        sys.exit(0)

    config_data = RawConfigParser()
    my_path = os.path.dirname(os.path.abspath(__file__))
    config_data.read(os.path.join(my_path, "config.ini"))

    self.cb_server = config_data.get('cb_server', 'url')
    self.token = config_data.get('cb_server', 'token')

    self.cb = CbApi(self.cb_server, token=self.token, ssl_verify=False)

    self.logger = logging.getLogger(__name__)

    endpointList = []

    '''
    output = csv.writer(sys.stdout)
    data = [['answer'],[result]]
    output.writerows(data)
    '''

    endpointList.append({'endpoint': [sys.argv[1], sys.argv[1]], 'details': ['more info here', '']})
    splunk.Intersplunk.outputResults(endpointList)

main()
