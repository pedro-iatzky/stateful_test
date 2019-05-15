"""
    tests.flow

    The flow path functionality

"""

from stateful_test import core


class TestFlowPath(object):

    def __execution_task(self, task_name, text=None):
        for i in range(10**7):
            pass
        print("Task {}: {}".format(task_name, text))

    def __create_task_a(self):
        a = core.Task("task_a")
        a.add_execution_task(self.__execution_task, "task_a")
        return a

    def __create_task_b(self):
        b = core.Task("task_b")
        b.add_execution_task(self.__execution_task, args="task_b",
                             kwargs={"text":"task_a executed, running task_b"})
        return b

    def __create_task_c(self):
        c = core.Task("task_c")
        c.add_execution_task(self.__execution_task, args="task_c",
                             kwargs={"text": "task_b executed, running task_c"})
        return c

    def test_simple_flow_path(self):
        a = self.__create_task_a()
        b = self.__create_task_b()
        c = self.__create_task_c()
        path = core.FlowPath([a, b, c])
        path.run()
        assert True

