import re
import json


class JiraForm(object):
    def __init__(self, config):
        self.config = config
        self.sva_severity = self.config['sva_severity']
        self.event_severity = self.config['event_severity']

    def form_summary(self, event):
        if event['type'] == 'issue_resolved':
            if 'SVA' in event['message']:
                m = re.search("Vulnerable package: (.*)\.", event["message"])
                if m:
                    issue_name = m.group(1)
            if 'CSM' in event['message']:
                m = re.search("Test: (.*)\.", event["message"])
                if m:
                    issue_name = m.group(1)

        elif event["type"] == "sca_rule_failed":
            issue_name = event["rule_name"]
        else:
            issue_name = event["package_name"]
        try:
            summary = "Halo Alert: %s on %s" % (issue_name, event['server_hostname'])
            return summary
        except:
            return None


    def form_ticket(self, event, summary):
        priority = self.set_priority(event)
        if priority:
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
                        "name": priority
                    }
                }
            }
            return json.dumps(data, indent=2)
        return None

    def form_transition(self, comment=False):
        if comment:
            data = self.config['resolution_workflow']['comment']
        else:
            data = {k:v for k,v in self.config['resolution_workflow'].items() if k in 'transition'}
        return json.dumps(data, indent=2)

    def set_priority(self, event):
        if event["type"] == "vulnerable_software_package_found":
            return self.priority_for_sva(event["cves"])
        else:
            if event["critical"]:
                return self.event_severity["critical"]
            return self.event_severity["non_critical"]
        return None


    def priority_for_sva(self, cves):
        max_cvss = max(cves, key=lambda d: d['CVSS'])['CVSS']
        try:
            max_severity = max(filter(lambda x: x <= max_cvss, self.sva_severity.values()))
        except:
            max_severity = min(self.sva_severity.values())

        if not self.is_surpressed(max_severity):
            criticality = [k for (k,v) in self.sva_severity.items() if v == max_severity]
            return criticality[0]
        return None

    def is_surpressed(self, max_cve):
        if max_cve <= self.config["supress_threshold"]:
            return True
        return False