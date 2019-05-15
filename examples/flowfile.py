"""
    Perform simple requests concurrently using the ConcurrencyFlows class. Check
    the task returns a 200 response code
"""

from stateful_test import core
import requests

req_no = 10
url = "http://www.example.com/"


def request():
    response = requests.get(url)
    return response


def create_task():
    def result_test(code_response):
        if code_response.status_code == 200:
            return True
        else:
            return False

    task = core.Task("example_request", request)
    task.add_result_function(result_test, task.result)
    return task


flow_dict = {i: core.FlowPath(create_task()) for i in range(req_no)}
cflows = core.ConcurrentFlows(flow_dict)
