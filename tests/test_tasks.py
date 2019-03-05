"""
    tests.tasks

    The Tasks functionality

"""

from stateful_test import core


class TestTaskPlaceHolder(object):

    VAR = "hello, world!"

    def __simple_task(self, str_var):
        return str_var

    def __result_with_place_holder(self, task_result):
        print("task_result", task_result)
        return task_result == self.VAR

    def test_task_placeholder_1(self):
        t = core.Task('test_placeholder', task_function=self.__simple_task,
                      task_args=self.VAR)
        t.add_result_function(self.__result_with_place_holder, t.result)
        t.run()
        check_result = t.check_result()
        assert check_result

    def test_task_placeholder_2(self):
        t = core.Task('test_placeholder', task_function=self.__simple_task,
                      task_args=self.VAR)
        t.add_result_function(self.__result_with_place_holder, core.TaskResult())
        t.run()
        check_result = t.check_result()
        assert check_result

    def test_task_placeholder_wrong(self):
        t = core.Task('test_placeholder', task_function=self.__simple_task,
                      task_args=self.VAR)
        t.add_result_function(self.__result_with_place_holder, "foo_bar")
        t.run()
        check_result = t.check_result()
        assert check_result is False
