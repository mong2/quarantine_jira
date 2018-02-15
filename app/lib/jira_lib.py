from config import CONFIG
import requests

class JiraApi(object):
    def __init__(self):
        self.config = CONFIG['jira']
        self.auth = (self.config['user'], self.config['passwd'])
        self.headers = {'Content-Type' : 'application/json'}

    def url(self, endpoint):
        return self.config['url'] + endpoint

    def get(self, endpoint):
        print 'querying endpoint: %s' % (endpoint)
    	resp = requests.get(self.url(endpoint), auth=(self.auth), headers=self.headers)
        if resp.status_code != 200:
            print('resp.text is %s' % (resp.text))
            print('Status:', resp.status_code, 'Problem with the request. Exiting.')
            exit()
        return resp.json()

    def post(self, endpoint, data):
        resp = requests.post(self.url(endpoint), auth=(self.auth), headers=self.headers, data=data)
        if resp.status_code != 201 and resp.status_code != 204:
            print('Status:', resp.status_code, 'Problem with the post request. Exiting', resp.text)
            exit()
        return resp.json()

    def put(self, endpoint, data):
        resp = requests.put(self.url(endpoint), auth=(self.auth), headers=self.headers, data=data)
        if resp.status_code != 201 and resp.status_code != 204:
            print('Status:', resp.status_code, 'Problem with the post request. Exiting', resp.text)
            exit()
        return resp.json()