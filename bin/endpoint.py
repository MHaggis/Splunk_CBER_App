#!/usr/bin/python 
# Parts of this have been copied from Splunks DNSLookup and other examples.
# You can sumbit up to 25 "resources" to VT, however this script does not do that.

import re, collections, json, csv, sys, urllib, urllib2, splunk.Intersplunk, string


def main():
    (isgetinfo, sys.argv) = splunk.Intersplunk.isGetInfo(sys.argv)
    if len(sys.argv) < 2:
        splunk.Intersplunk.parseError("No arguments provided")
        # print "python vt.py MD5 VT"
        sys.exit(0)

    endpointList = []

    '''
    output = csv.writer(sys.stdout)
    data = [['answer'],[result]]
    output.writerows(data)
    '''

    endpointList.append({'endpoint': [sys.argv[1], sys.argv[1]], 'details': ['more info here', '']})
    splunk.Intersplunk.outputResults(endpointList)

main()
