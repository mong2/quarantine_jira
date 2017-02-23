from jira_lib import JiraApi
from config import CONFIG
import json

class JiraController(object):
    def __init__(self):
        self.config = CONFIG['jira']
        self.existing_tickets = {}
        self.summary = ""

    def show_ticket(self, ticket_id):
        return JiraApi().get("/rest/api/2/issue/%s" % (ticket_id))

    def form_key(self, event):
        if event['type'] == 'vulnerable_software_package_found':
            summary = "Halo Alert -- Vulnerable package:%s on %s" % (event['package_name'], event['server_hostname'])
        else:
            summary = "Halo Alert -- %s on %s" % (event['name'],event['server_hostname'])
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
    			}
    		}
    	}
    	return json.dumps(data,indent=2)

    def create_ticket(self, event, summary):
    	return JiraApi().post("/rest/api/2/issue/", self.form_ticket(event, summary))

    def check_ticket_existence(self, event):
        summary = self.form_key(event)
        if summary not in self.existing_tickets.keys():
            resp = self.create_ticket(event,summary)
            self.existing_tickets[summary] = resp["key"]
            print self.existing_tickets
