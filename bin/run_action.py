#!/Users/stricaud/splunk_sandbox/splunkmodalerts/bin/splunk cmd python
# Please change the line above to match where your Splunk resides

# Do not change this
ACTIVERESPONSE_SCRIPT = "activeresponse.py"

import imp
import os
import sys

# this is the configuration from default/_alert_actions.conf
# settings = {u'log_file': u'/tmp/active_response.log', u'device_path': u'dummy', u'action_type': u'block'}
# [{'action_type': 'banhash', 'flow': 'submit', 'group': 'Z5tLJDgLfSBvItEdSjPK', 'b64records': '', 'path': 'dummy.log',
# 'fieldname': 'src_ip', 'fieldvalue': '10.11.6.5'}]

#
# This was taken from an example /tmp/arlog1.log
#
settings = [{'action_type': 'banhash', 'flow': 'submit', 'group': 'Z5tLJDgLfSBvItEdSjPK', 'b64records': '', 'path': 'dummy.log',
             'fieldname': 'src_ip', 'fieldvalue': '10.11.6.5'}]
# This is one event being sent from Splunk, you can add more key/values here to match your needs
results = [{'__mv__serial': '', 'eventtype': '', '_kv': '1', '__mv__indextime': '', '__mv_eventtype': '',
           '__mv__time': '', '__mv_sourcetype': '', 'splunk_server': 'stricaud-mbpr15.splunk.local',
           '__mv__confstr': '', '__mv__sourcetype': '', 'index': 'main',
           '_raw': 'This is the log that I sent which triggered the active response', '__mv__raw': '',
           '__mv_splunk_server': '', '__mv_index': '', '__mv_linecount': '', '_time': '1429133464',
           'source': '/Users/stricaud/foobar.txt', '__mv__kv': '', '_serial': '0', '_sourcetype': 'foobar',
           '_indextime': '1429133464', '__mv_host': '', 'timestamp': 'none', 'host': 'stricaud-mbpr15.splunk.local',
           '_confstr': 'source::/Users/stricaud/foobar.txt|host::stricaud-mbpr15.splunk.local|foobar',
           'sourcetype': 'foobar', '__mv_timestamp': '', '__mv_source': '', 'linecount': '1'}]

#
# sample data
# This was taken from an example /tmp/arlog1.log
#
results[0]['dest_ip'] = '111.111.111.111'
results[0]['source_ip'] = '111.111.111.111'

# This is what Splunk gives, which was configured in our KV store
hosts_mapping = {'network.firewall.vendor': '192.168.0.23 fw2 fw-zone3 192.168.123.8'}
hosts_mapping['endpoint.carblack.response'] = 'localhost'

devices = {}
'''
splunk_apps_path = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps')
devices_list = [f for f in os.listdir(splunk_apps_path) if
                os.path.isfile(os.path.join(splunk_apps_path, f, "bin", ACTIVERESPONSE_SCRIPT))]
for m in devices_list:
    if m != "arf":  # Obviously we do not want to load the framework itself
        device_path = os.path.join(splunk_apps_path, m, "bin")
        device_arfile = ACTIVERESPONSE_SCRIPT
        module_to_load = os.path.join(device_path, device_arfile)
        armodule = imp.load_source(device_arfile, module_to_load).Device(hosts_mapping)
        devices[armodule.path] = armodule
'''
armodule = imp.load_source("activeresponse.py", "./activeresponse.py").Device(hosts_mapping)
devices[armodule.path] = armodule

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Syntax: %s <action>" % (sys.argv[0]))
        print("Where <action> is either one of:")
        print("\tsubmit_action\n\trun_action\n\tundo_action\n\tfetch_feedback\n\texpiration\n")
        sys.exit(1)
    else:
        if sys.argv[1] == "submit_action":
            print("Testing submit_action")
            for device_path, device in devices.items():
                print("running on device path: %s" % (device_path))
                device.submit_action(settings, results)
        elif sys.argv[1] == "run_action":
            print("Testing run_action")
            for device_path, device in devices.items():
                print("running on device path: %s" % (device_path))
                device.run_action(settings, results)
        elif sys.argv[1] == "undo_action":
            print("Testing undo_action")
            for device_path, device in devices.items():
                print("running on device path: %s" % (device_path))
                device.undo_action()
        elif sys.argv[1] == "fetch_feedback":
            print("Testing fetch_feedback")
            for device_path, device in devices.items():
                print("running on device path: %s" % (device_path))
                device.fetch_feedback()
        elif sys.argv[1] == "expiration":
            print("Testing expiration")
            for device_path, device in devices.items():
                print("running on device path: %s" % (device_path))
                device.expiration()
        else:
            print("Error: no such token %s" % sys.argv[1])
            sys.exit(1)
