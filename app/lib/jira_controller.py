from jira_lib import JiraApi
from config import CONFIG
import json

class JiraController(object):
    def __init__(self):
        self.config = CONFIG['jira']

    def show_ticket(self, ticket_id):
        return JiraApi().get("/rest/api/2/issue/%s" % (ticket_id))

    def form_ticket(self, event):
    	data = {
    		"fields":{
    			"project":
    			{
    				"key": self.config['project_key']
    			},
    			"summary": "%s on %s" % (event['name'], event['server_hostname']),
    			"description": "Creating this issue based on a triggered event in Halo\n %s" % (json.dumps(event, indent=2)),
    			"issuetype": {
    				"name": self.config['issue_name']
    			}
    		}
    	}
    	return json.dumps(data,indent=2)

    def create_ticket(self, event):
    	return JiraApi().post("/rest/api/2/issue/", self.form_ticket(event))