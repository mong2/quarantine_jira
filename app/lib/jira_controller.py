from jira_lib import JiraApi
from config import CONFIG
from jira_form import JiraForm

class JiraController(object):
    def __init__(self):
        self.config = CONFIG['jira']
        self.existing_tickets = {}
        self.summary = ""
        self.fmt = JiraForm(self.config)

    def check_ticket_existence(self, event):
        summary = self.fmt.form_summary(event)
        if summary not in self.existing_tickets.keys():
            resp = self.exist_in_jira(summary)
            if resp['issues']:
                self.existing_tickets[summary] = resp["issues"][0]["key"]
            else:
                return False, summary
        return True, self.existing_tickets[summary]

    def create_ticket(self, event, summary):
        ticket = self.fmt.form_ticket(event, summary)
        if ticket:
            resp = JiraApi().post("/rest/api/2/issue/", ticket)
            try:
                self.existing_tickets[summary] = resp["key"]
            except:
                return None

    def transition_ticket(self, issuekey):
        if not self.config["auto_resolved"]:
            return None
        trans_endpoint = "/rest/api/2/issue/%s/transitions?expand=transitions.fields" % issuekey
        comment_endpoint = "/rest/api/2/issue/%s/comment" % issuekey
        JiraApi().post(comment_endpoint, self.fmt.form_transition(comment=True))
        JiraApi().post(trans_endpoint, self.fmt.form_transition())
        return None


    def exist_in_jira(self, summary):
        endpoint = "/rest/api/2/search?jql=summary~'%s'" % (summary)
        return JiraApi().get(endpoint)

