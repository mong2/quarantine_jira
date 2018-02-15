from jira_lib import JiraApi
from config import CONFIG
import re
import json

class JiraController(object):
    def __init__(self):
        self.config = CONFIG['jira']
        self.existing_tickets = {}
        self.summary = ""
        self.severity = self.config['severity_criteria']

    def show_ticket(self, ticket_id):
        return JiraApi().get("/rest/api/2/issue/%s" % (ticket_id))

    def form_key(self, event):
        if event['type'] == 'issue_resolved':
            if 'SVA' in event['message']:
                m = re.search("Vulnerable package: <strong>(.*)</strong>", event["message"])
                if m:
                    package_name = m.group(1)
        else:
            package_name = event["package_name"]

        summary = "Halo Alert -- Vulnerable package:%s on %s" % (package_name, event['server_hostname'])
        return summary

    def form_ticket(self, event, summary):
        data = {
            "fields":{
                "project":
                {
                    "key": self.config['project_key']
                },
                "summary": summary,
                "description": "Creating this issue based on a triggered event in Halo\n {code}%s{code}" % (json.dumps(event, indent=2)),
                "issuetype": {
                    "name": self.config['issue_name']
                },
                "priority": {
                    "name": self.set_priority(event["cves"])
                }
            }
        }
        return json.dumps(data, indent=2)

    def updated_form(self):
        data = {
            "update": self.config["resolution_workflow"]
        }
        return json.dumps(data, indent=2)

    def exist_in_jira(self, summary):
        endpoint = "/rest/api/2/search?jql=summary~%s" % summary
        return JiraApi().get(endpoint)

    def set_priority(self, cves):
        max_cvss = max(cves, key=lambda d: d['CVSS'])['CVSS']
        criticality = [k for (k,v) in self.severity.items() if v >= max_cvss]
        return criticality[0]

    def check_ticket_existence(self, event):
        summary = self.form_key(event)
        if summary not in self.existing_tickets.keys():
            if exist_in_jira(summary):
                self.existing_tickets[summary] = resp["issues"]["key"]
            else:
                return False, summary
        return True, self.existing_tickets[summary]

    def create_ticket(self, event, summary):
        resp = JiraApi().post("/rest/api/2/issue/", self.form_ticket(event, summary))
        self.existing_tickets[summary] = resp["key"]
        return None

    def resolved_ticket(self, issuekey):
        endpoint = "/rest/api/2/issue/%s" % issuekey
        return JiraApi().post(endpoint, self.updated_form())