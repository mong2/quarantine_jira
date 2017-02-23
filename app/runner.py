import quarantine
import lib

# Build config
config = quarantine.ConfigHelper()

# Halo object
halo = quarantine.HaloGeneral(config)

# Halo events
events = quarantine.HaloEvents(config)

# Matcher object
matcher = quarantine.Matcher(config.match_list)

jira = lib.JiraController()

# Iterate over events, quarantine targeted workloads
count = 0
while count < 6:
    for event in events:
        if matcher.is_a_match(event["type"]):
            # print event
            print "Quarantining workload: %s" % event["server_id"]
            jira.check_ticket_existence(event)
            count += 1
#             # halo.quarantine_workload(event["server_id"])
