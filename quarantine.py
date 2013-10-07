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

def processCmdLineArgs(argv):
    global verbose, key_id, secret, hostToQuarantine
    for arg in argv[1:]:
        if ((arg == '-?') or (arg == "-h")):
            printUsage(os.path.basename(argv[0]))
            return True
        elif (arg == '-v'):
            verbose = True
        elif (arg.startswith('--auth=')):
            filename = arg[7:]
            if len(authFilenameList) > 0:
                print >> sys.stderr, "Error: Only one auth filename allowed"
                return True
            else:
                authFilenameList.append(filename)
        elif (not arg.startswith('-')):
            hostToQuarantine = arg
        elif (arg != argv[0]):
            print >> sys.stderr, "Unrecognized argument: %s" % arg
            return False
    if hostToQuarantine == None:
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
    print >> sys.stderr, "Usage: %s [<flag>]... <server>" % progName
    print >> sys.stderr, "Where <server> is the ID of a server to quarantine,"
    print >> sys.stderr, "and <flag> is one of:"
    print >> sys.stderr, "-?\t\t\tThis message"
    print >> sys.stderr, "-v\t\t\tMake program verbose"
    print >> sys.stderr, "--auth=<file>\t\tSpecify a file containing ID/secret pairs (up to 5)"


# end of function definitions, begin inline code

atexit.register(processExit)
progDir = os.path.dirname(sys.argv[0])

if (processCmdLineArgs(sys.argv)):
    sys.exit(0)

cputils.verbose = verbose
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
        sys.exit(2) # findOrCreateFirewallPolicy should print relevant error message
    desiredWindowsFirewallPolicy = cputils.findOrCreateFirewallPolicy(apiCon, windowsFirewallPolicyName, "windows")
    if not (desiredWindowsFirewallPolicy):
        sys.exit(2) # findOrCreateFirewallPolicy should print relevant error message
    (response, authError) = apiCon.createServerGroup(quarantineGroupName, desiredLinuxFirewallPolicy, desiredWindowsFirewallPolicy)
    if authError:
        print >> sys.stderr, "Creating Quarantine Group FAILED: check that your Halo API key has write priviledges on your account"
        sys.exit(2)
else:
    # Server Group exists, but we didn't create it... check firewall policies:
    cputils.checkGroupFirewallPolicies(desiredGroup,apiCon,linuxFirewallPolicyName,windowsFirewallPolicyName)

desiredGroup = cputils.findGroupByName(apiCon, quarantineGroupName)
if not (desiredGroup):
    print >> sys.stderr, "Failed to create group: %s" % quarantineGroupName
    sys.exit(2)

for desiredServer in desiredServerList:
    if ((desiredServer) and (desiredGroup)):
        (response, authError) = apiCon.moveServerToGroup(desiredServer['id'], desiredGroup['id'])
        if (response):
            print >> sys.stderr, "error: %s" % response
        elif authError:
            print >> sys.stderr, "Quarantine FAILED: check that your Halo API key has write priviledges on your account"
        else:
            print "Successfully quarantined server: %s (id=%s)" % (desiredServer['hostname'], desiredServer['id'])
            print "   moved to group %s" % quarantineGroupName
    else:
        print >> sys.stderr, "error: Server %s, Group %s" % (cputils.isNullOrNot(desiredServer), cputils.isNullOrNot(desiredGroup))
