#!/usr/bin/env python
import sys
import platform
import os
import atexit

import cputils
import cpapi
import json

cputils.checkPythonVersion()

import os.path

# Here, we check for which OS (all non-Windows OSs are treated equally) we have.
isWindows = True
if (platform.system() != "Windows"):
    isWindows = False

# global vars
verbose = False
authFilenameDefault = "quarantine.auth"
authFilenameList = []
if isWindows:
    pidFilename = "/quarantine.lock"
else:
    pidFilename = "/tmp/quarantine.lock"
hostToQuarantine = None
quarantineGroupName = "Quarantine"
linuxFirewallPolicyName = "quarantine-linux"
windowsFirewallPolicyName = "quarantine-windows"
matchFileName = "quarantine_filter.txt"
events_per_page = 100
readEvents = False
readStdin = False
readMode = None

def processCmdLineArgs(argv):
    global verbose, key_id, secret, hostToQuarantine, readMode
    for arg in argv[1:]:
        if ((arg == '-?') or (arg == "-h")):
            printUsage(os.path.basename(argv[0]))
            return True
        elif (arg == '-v'):
            verbose = True
        elif (arg.startswith('--stdin')):
            readMode = "stdin"
        elif (arg.startswith('--portal')):
            readMode = "portal"
        elif (arg.startswith('--auth=')):
            filename = arg[7:]
            if len(authFilenameList) > 0:
                print >> sys.stderr, "Error: Only one auth filename allowed"
                return True
            else:
                authFilenameList.append(filename)
        elif (not arg.startswith('-')):
            hostToQuarantine = arg
            readMode = "cmdline"
        elif (arg != argv[0]):
            print >> sys.stderr, "Unrecognized argument: %s" % arg
            return False
    if readMode == None:
        printUsage(os.path.basename(argv[0]))
        return True
    return False


# Any code that needs to be executed, no matter how we exit,
#   should be added to this function.
def processExit():
    global pidFilename, syslogOpen
    try:
        os.remove(pidFilename)
    except:
        if (os.path.exists(pidFilename)):
            print >> sys.stderr, "Unable to clean up lock file %s, clean up manually" % pidFilename


def printUsage(progName):
    print >> sys.stderr, "Usage: %s [<flag>]... --stdin|--portal|<server>" % progName
    print >> sys.stderr, "Where <server> is the ID of a server to quarantine,"
    print >> sys.stderr, "and <flag> is one of:"
    print >> sys.stderr, "-?\t\t\tThis message"
    print >> sys.stderr, "-v\t\t\tMake program verbose"
    print >> sys.stderr, "--auth=<file>\t\tSpecify a file containing ID/secret pairs (up to 5)"
    print >> sys.stderr, "--stdin\t\t\tRead events from stdin"
    print >> sys.stderr, "--portal\t\tRead events from CP portal"
    print >> sys.stderr, "If no server ID supplied on command line, script will accept events in"
    print >> sys.stderr, "JSON format, which are assumed to be events containing servers which"
    print >> sys.stderr, "should be quarantined. You must specify the source of the events:"
    print >> sys.stderr, "either --stdin or --portal."


def addToServerList(list, id):
    if (id) and (not (id in list)):
        list.append(id)
        if verbose:
            print >> sys.stderr, "Adding server ID '%s' to quarantine list" % id


def extractNextLink(obj):
    paginationKey = 'pagination'
    nextKey = 'next'
    nextLink = None
    lastTimestamp = None
    if (paginationKey in obj):
        pagination = obj[paginationKey]
        if ((pagination) and (nextKey in pagination)):
            nextLink = pagination[nextKey]
    return nextLink


def processStdin(criteria):
    serverList = []
    lines = sys.stdin.readlines()
    for line in lines:
        str = line.strip()
        evObj = json.loads(str)
        if not matchEvent(evObj, criteria):
            continue
        if 'server_id' in evObj:
            addToServerList(serverList, evObj['server_id'])
    return serverList


def getFieldWithDefault(obj,key,defaultValue):
    if key in obj:
        return obj[key]
    else:
        return defaultValue


def processEventsFromPortal(apiCon, criteria, startingDate, connLastTimestamp = None):
    eventsKey = 'events'
    serverList = []
    nextLink = apiCon.getInitialLink(connLastTimestamp, events_per_page)
    while (nextLink):
        (batchStr, authError) = apiCon.getEventBatch(nextLink)
        if authError:
             resp = apiCon.authenticateClient()
             if (not resp):
                 print >> sys.stderr, "Failed to retrieve authentication token. Exiting...."
                 sys.exit(1)
        else:
            batchObj = json.loads(batchStr)
            nextLink = extractNextLink(batchObj)
            if (eventsKey in batchObj):
                eventList = batchObj[eventsKey]
                numEvents = len(eventList)
                if (numEvents > 0):
                    for evObj in eventList:
                        if not matchEvent(evObj, criteria):
                            continue
                        if ('server_id' in evObj) and (evObj['server_id']):
                            addToServerList(serverList, evObj['server_id'])
                        else:
                            timestamp = getFieldWithDefault(evObj,'created_at',"Unknown")
                            message = getFieldWithDefault(evObj,'message',"Unknown")
                            print >> sys.stderr, "Event found with no server_id value at %s" % timestamp
                            print >> sys.stderr, "    Event msg: %s" % message
    return serverList


def processMatchFile(filename):
    criteria = []
    if not os.path.exists(filename):
        print >> sys.stderr, "Match file (%s) not found" % filename
        return criteria
    lines = open(filename,"r").readlines()
    for line in lines:
        str = line.strip()
        if not str.startswith("#"):
            fields = str.split("=")
            if (len(fields) == 2):
                criterion = { "field": fields[0], "value": fields[1] }
                criteria.append(criterion)
            else:
                print >> sys.stderr, "Illegal line: %s" % str
    return criteria


def matchEvent(event, criteria):
    if event == None:
        return False
    if (criteria == None) or (len(criteria) < 1):
        return True
    for criterion in criteria:
        if (criterion["field"] in event) and (event[criterion["field"]] == criterion["value"]):
            if verbose:
                print "Event: %s=%s - matched!" % (criterion["field"], criterion["value"])
            return True
    return False


# end of function definitions, begin inline code

atexit.register(processExit)
progDir = os.path.dirname(sys.argv[0])

if (processCmdLineArgs(sys.argv)):
    sys.exit(0)

cputils.checkLockFile(pidFilename)

if (len(authFilenameList) == 0):
    authFilenameList = [authFilenameDefault]

# was a for/loop in haloEvents.py, but we'll never need that here
authFilename = authFilenameList[0]
(credentialList, errMsg) = cputils.processAuthFile(authFilename,progDir)
credential = credentialList[0]

apiCon = cpapi.CPAPI()
(apiCon.key_id, apiCon.secret) = (credential['id'], credential['secret'])

if ((not apiCon.key_id) or (not apiCon.secret)):
    print >> sys.stderr, "Unable to read auth file %s. Exiting..." % authFilename
    print >> sys.stderr, "Requires lines of the form \"<API-id>|<secret>\""
    sys.exit(1)

resp = apiCon.authenticateClient()
if (not resp):
    print >> sys.stderr, "Failed to retrieve authentication token. Exiting..."
    sys.exit(1)

criteria = processMatchFile(matchFileName)

if (readMode == "stdin") or (readMode == "portal"):
    if (readMode == "stdin"):
        if verbose:
            print >> sys.stderr, "Reading events from stdin..."
        desiredServerList = processStdin(criteria)
    else:
        if verbose:
            print >> sys.stderr, "Reading events from portal..."
        desiredServerList = processEventsFromPortal(apiCon, criteria, None)
    if verbose:
        print >> sys.stderr, "Identified %d servers to be quarantined." % len(desiredServerList)
    if (len(desiredServerList) < 1) or (desiredServerList[0] == None):
        print >> sys.stderr, "No server IDs found in events, no servers to quarantine"
        sys.exit(2)
else:
    desiredServerList = [cputils.findHostByID(apiCon, hostToQuarantine)]
    if (len(desiredServerList) < 1) or (desiredServerList[0] == None):
        print >> sys.stderr, "No such server found: %s" % hostToQuarantine
        for server in cputils.findHostByNameOrAddress(apiCon, hostToQuarantine):
            print >> sys.stderr, "Found server by name: %s" % server
        sys.exit(2)

desiredGroup = cputils.findGroupByName(apiCon, quarantineGroupName)
if not (desiredGroup):
    print "No quarantine group found, attempting to create: %s" % quarantineGroupName
    desiredLinuxFirewallPolicy = cputils.findOrCreateFirewallPolicy(apiCon, linuxFirewallPolicyName, "linux")
    if not (desiredLinuxFirewallPolicy):
        print >> sys.stderr, "No such firewall policy found: %s" % linuxFirewallPolicyName
        sys.exit(2)
    desiredWindowsFirewallPolicy = cputils.findOrCreateFirewallPolicy(apiCon, windowsFirewallPolicyName, "windows")
    if not (desiredWindowsFirewallPolicy):
        print >> sys.stderr, "No such firewall policy found: %s" % windowsFirewallPolicyName
        sys.exit(2)
    apiCon.createServerGroup(quarantineGroupName, desiredLinuxFirewallPolicy, desiredWindowsFirewallPolicy)

desiredGroup = cputils.findGroupByName(apiCon, quarantineGroupName)
if not (desiredGroup):
    print >> sys.stderr, "Failed to create group: %s" % quarantineGroupName
    sys.exit(2)

availableServerList = cputils.getHostList(apiCon)

for desiredServerID in desiredServerList:
    if desiredServerID:
        desiredServer = cputils.findHostInList(availableServerList,desiredServerID)
    else:
        desiredServer = None
    if ((desiredServer) and (desiredGroup)):
        (response, authError) = apiCon.moveServerToGroup(desiredServer['id'], desiredGroup['id'])
        if (response):
            print >> sys.stderr, "error: %s" % response
        else:
            print "Successfully quarantined server: %s (id=%s)" % (desiredServer['hostname'], desiredServer['id'])
            print "   moved to group %s" % quarantineGroupName
    else:
        print >> sys.stderr, "error: Server %s, Group %s" % (cputils.isNullOrNot(desiredServer), cputils.isNullOrNot(desiredGroup))
