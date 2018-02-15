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

while True:
    for event in events:
        if matcher.is_a_match(event["type"]):
            exist, summary = jira.check_ticket_existence(event)
            print "exist is %s" % (exist)
            print "summary is %s" % (summary)
            if event["type"] == "issue_resolved" and exist:
                # print "event is %s" % (event)
                # print "summary is %s" % (summary)
                jira.resolved_ticket(summary)
            elif event["type"] == "vulnerable_software_package_found" and not exist:
                jira.create_ticket(event, summary)
