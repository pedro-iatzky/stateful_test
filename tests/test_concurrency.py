from stateful_test import core
import requests


class TestConcurrency(object):

    url = "http://www.example.com/"

    def __request(self):
        response = requests.get(self.url)
        return response

    def __create_request_task(self):
        t = core.Task("example_req", task_function=self.__request)
        return t

    def __create_flow_path(self):
        tasks = [self.__create_request_task(), ]
        return core.FlowPath(tasks)

    def test_concurrent_at_once(self):
        req_no = 5
        flow_dict = {i: self.__create_flow_path() for i in range(req_no)}
        concurrent_flow = core.ConcurrentFlows(flow_dict)
        concurrent_flow.run()
        logs = concurrent_flow.logs
        assert len(logs) == 5
