# coding=utf-8
from __future__ import division
import logging
import requests
import sys
import getopt
from credentials import SLACK_BOT_TOKEN,\
    JIRA_AUTHORIZATION,\
    JIRA_API_URL,\
    SLACK_CHANNEL_ID,\
    SLACK_TEST_CHANNEL_ID,\
    SLACK_BOT_NAME

class TimetrackingController():
    def getAverageFromTickets(self, data):
        accuracies = []

        for issue in data['issues']:
            timetracking = issue['fields']['timetracking']
            timespent = 0
            estimated = 0

            if 'timeSpentSeconds' in timetracking.keys():
                timespent = timetracking['timeSpentSeconds']
                #print timespent

            if 'originalEstimateSeconds' in timetracking.keys():
                estimated = timetracking['originalEstimateSeconds']
                #print estimated
            
            if (timespent and estimated):
                accuracy = timespent * 100 / estimated
                # print "accuracy: "
                # print accuracy
                accuracies.append(abs(100 - accuracy))

        self.computeAverageFromVariations(accuracies)

    def computeAverageFromVariations(self, variations):
        variations.sort(reverse=True)

        # floor round number of elements that count into average
        probe = int(len(variations) * 0.75)
        sum = 0

        for acc in variations[:probe]:
            print acc
            sum+=acc

        print "result: "
        print sum/probe


class JiraController():
    def __init__(self):
        logging.basicConfig(level = logging.INFO)

    def get_tickets(self):
        """
        Gets the finished tickets statistics
        """
        response = []
        params = self.get_params()

        finished_tickets = self.make_jira_request(params)

        return finished_tickets

    def make_jira_request(self, params):
        headers = {
            'contentType': 'application/json',
            'Authorization': JIRA_AUTHORIZATION
        }

        jql = 'assignee was diana.falkowska AND status in (Closed, Solved, Done) AND project = "West Wing" AND updated >= 2016-05-01 AND updated <= 2016-06-30'

        response = requests.get(
                JIRA_API_URL,
                params = {
                    'jql': jql,
                    'fields': 'timetracking,timespent,summary,self'
                },
                headers = headers
            ).json()

        return response

    def get_params(self):
        project_name = 'West Wing'
        params = {
            'project_name': project_name,
        }

        optlist, args = getopt.getopt(sys.argv[1:], "p:d:", ["project=", "test"])

        for option, arg in optlist:
            if option in ("-p", "--project"):
                params['project_name'] = arg

        return params

if __name__ == "__main__":
    jiraConnector = JiraController()
    tracker = TimetrackingController()

    tickets = jiraConnector.get_tickets()
    tracker.getAverageFromTickets(tickets)
