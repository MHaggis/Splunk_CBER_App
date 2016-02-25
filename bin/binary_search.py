#!/usr/bin/python
# Parts of this have been copied from Splunks DNSLookup and other examples.
# You can sumbit up to 25 "resources" to VT, however this script does not do that.

from cbapi import CbApi
from ConfigParser import RawConfigParser
import os
import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import splunk.clilib.cli_common

@Configuration()
class BinarySearchCommand(GeneratingCommand):
    """Generates a binary search result from Carbon Black from a given MD5 or search query
        | binarysearch ${md5}
    """

    query = Option(name="query", require=True)
    field_names = ['digsig_publisher', 'digsig_result', 'digsig_sign_time', 'host_count', 'is_executable_image',
                   'last_seen', 'original_filename', 'os_type', 'product_name', 'product_version', 'md5']

    def prepare(self):
        configuration_dict = splunk.clilib.cli_common.getConfStanza('carbonblack', 'cbserver')

        cb_server = configuration_dict['cburl']
        token = configuration_dict['cbapikey']

        self.cb = CbApi(cb_server, token=token, ssl_verify=False)

    def generate(self):
        for bindata in self.cb.binary_search_iter(self.query):
            self.logger.info("yielding binary %s" % bindata["md5"])
            yield dict((field_name, bindata.get(field_name, "")) for field_name in self.field_names)


if __name__ == '__main__':
    dispatch(BinarySearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
