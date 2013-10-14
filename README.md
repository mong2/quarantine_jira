#Quarantine script

Version: *1.0*
<br />
Author: *Apurv Singh* - *apurva@cloudpassage.com*

The purpose of the quarantine script is to place a server instance(s) into an isolated firewall group if/when specified Halo events occur. This script can also be used to move a server instance into a 'remote analysis' group (for Forensics-Response investigation) or to a data capture group.
You can use the script to manually quarantine servers or trigger server quarantines automatically, based on different criteria*. In either case, the script does the following:

* It creates a Halo Server Group called “Quarantine”
* It creates a Linux firewall policy called “quarantine-linux”
* It creates a Windows firewall policy called “quarantine-windows”
* It applies the two firewall policies to the Quarantine server group
* It moves the server in question to the Quarantine server group

Note: The firewall policies allow the server to communicate only to the Halo grid.


##List of Files

* name of script file
* README.md -- This ReadMe file.
* cputils.py
* cpapi.py
* cpfwpolicies.py
* quarantine.auth
* quarantine_filter.txt
* quarantine-ng.py


##Requirements and Dependencies

To get started, you must have the following privileges and software resources:
* An active CloudPassage Halo subscription. If you don't have one, Register for CloudPassage to receive your credentials and further instructions by email.
* Access to your CloudPassage API key. Create a new key, with write privileges, specifically for use with this script.
* Python 2.6 or later. You can download Python from here.



##Installation 

Once you have downloaded the script, make sure you make it executable by typing the following on the command line: chmod +x quarantine-ng.py

##Usage
To see detailed script usage, type the following on the command line:
```
$ ./quarantine-ng.py -?
Usage: quarantine-ng.py [<flag>]... --stdin|--portal|<server>
```
Where <server> is the ID of a server to quarantine, and <flag> is one of:
```
-?                              This message
-v                             	Make program verbose
--auth=<file>              	    Specify a file containing ID/secret pairs (up to 5)
--stdin                        	Read events from stdin
--portal                      	Read events from CP portal
```

If no server ID supplied on command line, script will accept events in JSON format, which are assumed to be events containing servers which should be quarantined. You must specify the source of the events, either --stdin or --portal.



If you want to manually quarantine a Halo managed cloud server, you can specify the server’s Halo server ID as a parameter to the script.  

To automatically quarantine servers based on certain security events on that server, do the following:

In the quarantine_filter.txt file, specify the name of events on which to trigger a server quarantine. Say for example, you wanted to automatically trigger a quarantine for a cloud server whose firewall had been modified locally, outside of Halo. In the quarantine_filter.txt file, you would specify an entry like this on it’s own line:
```
name=Server firewall modified
```

where “Server firewall modified” is the name of the Halo event that is generated and logged in the event of a host firewall being modified locally, outside of Halo.

Then, run the script by typing the following command:
```
./quarantine-ng.py --auth=/etc/quarantine.auth --portal
```

Note: The quarantine script doesn’t yet support the --starting option, so if you want to pull events from point in time of your choosing, use the following command to quarantine:
```
./haloEvents.py --starting=<datetime> --kv | ./quarantine-ng.py --stdin -v 
```
--auth specifies the file where the Halo API keys are specified<br />
--portal tells the script to read events from the Halo account specified in the file specified in the --auth option

The script will starting reading events from the Halo account and matching each event against the events specified in the quarantine_filter.txt file. As soon as a match is found, the server in question will be quarantined. 

*In the current version of the script, only Halo event names can be used to trigger automatic server quarantines. 

