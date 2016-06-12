# coding=utf-8
from __future__ import division
import logging
import requests
import sys
import getopt
from credentials import JIRA_AUTHORIZATION,\
    JIRA_API_URL

class TimetrackingController:
    def __init__(self, params):
        self.data_width = params['data_width']

    def getAverageFromTickets(self, tickets):
        """
        Given array of ticket, checks if one have proper estimation
        and tracking data and compute average error of estimation(abs)
        """
        accuracies = []

        for ticket in tickets:
            timetracking = ticket['fields']['timetracking']
            timespent = 0
            estimated = 0

            if 'timeSpentSeconds' in timetracking.keys():
                timespent = timetracking['timeSpentSeconds']

            if 'originalEstimateSeconds' in timetracking.keys():
                estimated = timetracking['originalEstimateSeconds']
            
            if (timespent and estimated):
                accuracy = timespent * 100 / estimated
                accuracies.append(abs(100 - accuracy))

        return self.computeAverageFromVariations(accuracies)

    def computeAverageFromVariations(self, variations):
        variations.sort(reverse = True)

        # floor round number of elements that count into average
        probe = int(len(variations) * self.data_width / 100)
        sum = 0

        if (probe < 1):
            return 0

        for acc in variations[:probe]:
            print acc
            sum += acc

        averageAccuracy = sum / probe

        return averageAccuracy


class JiraController():
    def get_tickets(self, params):
        """
        Gets the finished tickets data
        """
        jira_response = self.make_jira_request(params)

        return jira_response['issues']

    def make_jira_request(self, params):
        headers = {
            'contentType': 'application/json',
            'Authorization': JIRA_AUTHORIZATION
        }

        jql = ('assignee was ' + params['user'] + ' AND '
            'status in (Closed, Solved, Done) AND '
            'project = "' + params['project_name'] + '" AND '
            'updated >= 2016-04-01 AND '
            'updated <= 2016-06-30')

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
        user = 'diana.falkowska'
        data_width = 75
        params = {
            'project_name': project_name,
            'user': user,
            'data_width': data_width
        }

        optlist, args = getopt.getopt(sys.argv[1:], "p:u:w:", ["project=", "user=", "width="])

        for option, arg in optlist:
            if option in ("-p", "--project"):
                params['project_name'] = arg

            if option in ("-u", "--user"):
                user = arg
                params['user'] = arg

            if option in ("-w", "--width"):
                user = arg
                params['data_width'] = int(arg)

        return params

if __name__ == "__main__":
    jiraConnector = JiraController()
    params = jiraConnector.get_params()
    tickets = jiraConnector.get_tickets(params)

    tracker = TimetrackingController(params)
    averageAccuracy = tracker.getAverageFromTickets(tickets)

    print ("{} is accurate +/- {:.2f}% in {}% of cases.". format(params['user'], 100 - averageAccuracy, params['data_width']))
    print ("That is, in {}% of cases {}'s estimation is good in {:.2f}%.". format(params['data_width'], params['user'], averageAccuracy))
