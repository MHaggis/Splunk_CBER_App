# Carbon Black Enterprise Response Splunk App

Current Version: ***Beta***

**NOTE: This Splunk app is in Beta, proof of concept state.**

The Carbon Black App for Splunk allows administrators to leverage the industry's leading EDR solution to see, detect and take action upon endpoint activity from directly within Splunk. Once installed, the App will allow administrators to access many of the powerful features of Carbon Black, such as process and binary searches from within and in conjunction with Splunk.

This initial version of the Integration App provides the user the capability to search the Carbon Black server fromSplunk. Future versions will integrate additional features to allow you to direct Carbon Black detection, response and remediation actions via the Splunk interface.

## Requirements

This app requires a functional Carbon Black server, version 5.1 or above, and Splunk version 6.3 or above.
No additional hardware requirements are necessary for running this app above the standard requirements for both
Carbon Black and Splunk.

## Getting Started

Once the integration is installed, you must configure it to connect to your Carbon Black server. The Integration requires a Carbon Black API token from a user with Search privileges to enable all current features.

To retrieve the Carbon Black API Token:

1.  Log into your Carbon Black server, click your user profile on the top right banner and select "Profile Info".
2.  On this page, click "API Token" on the left hand side and copy  the API token

To setup the Splunk App:

1. Navigate to the Apps Manager page.
2. Look for the Carbon Black Enterprise Response App
3. Click 'Set up'
4. Enter your server URL in the 'CB server URL' text box. (example: https://cbserver.mycompany.com)
5. Paste the Carbon Black API Token into the text box labelled 'API Key'.
6. Click 'Save'

## Usage

The Carbon Black QRadar Application contains two major components. These components are process/binary search within
the app and workflow actions that enable pivoting from standardized fields into Carbon Black searches.

### Process/Binary Searches

The main tab within the Carbon Black Enterprise Response Splunk App allows users to perform either a process or binary search
within Carbon Black.  The results will be displayed within the same screen.  Users can also use Carbon Black search features
using the following custom search commands.

*   processsearch

        Example: processsearch query="process_name:cmd.exe"
*   binarysearch

        Example: binarysearch query="md5=fd3cee0bbc4e55838e65911ff19ef6f5"

### Workflow Actions

Workflow Actions allow users to pivot into Carbon Black searches from standardized fields.  To Perform a workflow action, drilldown into an event and click the 'Event Actions' button.  From this menu the available workflow actions from this app will be displayed.  A User can pivot directly from a field given that a workflow action is available for that field.  Current supported workflow actions:

| Workflow Action | Supported Fields |
|-----------------|------------------|
| CB Binary Search by MD5 | md5, file_hash, process_md5 |
| CB Process Search by IP | src_ip, dest_ip, local_ip, remote_ip, ipv4 |
| CB Process Search by MD5 | md5, file_hash |
| CB Process Search by FileName | file_name, file_path |
| CB Process Search by Domain | domain |


## Contacting Carbon Black Support

E-mail: support@carbonblack.com

### Reporting Problems

When you contact Carbon Black Support with an issue, please provide the following:

* Your name, company name, telephone number, and e-mail address
* Product name/version, CB Server version, CB Sensor version
* QRadar version
* Hardware configuration of the Carbon Black Server or computer (processor, memory, and RAM)
* For documentation issues, specify the version of the manual you are using.
* Action causing the problem, error message returned, and event log output (as appropriate)
* Problem severity
