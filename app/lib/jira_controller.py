from jira_lib import JiraApi
from config import CONFIG
import json

class JiraController(object):
    def __init__(self):
        self.config = CONFIG['jira']
        self.existing_tickets = {}

    def show_ticket(self, ticket_id):
        return JiraApi().get("/rest/api/2/issue/%s" % (ticket_id))

    def form_ticket(self, event):
    	data = {
    		"fields":{
    			"project":
    			{
    				"key": self.config['project_key']
    			},
    			"summary": "Halo Alert -- %s" % (event['name']),
    			"description": "Creating this issue based on a triggered event in Halo\n Effected servers:\n%s" %(event['server_hostname']),
    			"issuetype": {
    				"name": self.config['issue_name']
    			}
    		}
    	}
    	return json.dumps(data,indent=2)

    def form_description(self,event):
        result = self.show_ticket(self.existing_tickets[event['type']])
        update = "%s\n%s" % (result["fields"]["description"], event['server_hostname'])
        words = update.split()
        return " ".join(sorted(set(words), key=words.index))

    def create_ticket(self, event):
    	return JiraApi().post("/rest/api/2/issue/", self.form_ticket(event))

    def update_ticket(self, event):
        endpoint = "/rest/api/2/issue/%s" % self.existing_tickets[event['type']]
        data = { "update":{ "description": [{"set":self.form_description(event)}]}}
        return JiraApi().put(endpoint, json.dumps(data, indent=2))

    def check_ticket_existence(self, event):
        if event['type'] in self.existing_tickets.keys():
            self.update_ticket(event)
        else:
            resp = self.create_ticket(event)
            self.existing_tickets[event['type']] = resp["key"]
            print self.existing_tickets
