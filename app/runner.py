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
            issue_key = jira.check_ticket_existence(event)
            if event["type"] == "issue_resolved" and issue_key:
                jira.issue_resolved(issue_id)
            elif event["type"] == "vulnerable_software_package_found" and not issue_key:
                jira.create_ticket(event)