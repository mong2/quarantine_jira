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
            if event["type"] == "issue_resolved" and exist:
                jira.transition_ticket(summary)
            elif event["type"] == "vulnerable_software_package_found" and not exist:
                jira.create_ticket(event, summary)
