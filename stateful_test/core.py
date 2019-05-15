from gevent import monkey; monkey.patch_all()
import gevent
import copy
import contextlib
import time
from .helpers import cast_to_args, cast_to_kwargs, format_time
from .log_config import LOG_DICT, TASK_DICT
import traceback


class TaskNotDefined(Exception):
    def __init__(self, task_name):
        super().__init__("Task {}: execution task not defined!!".format(task_name))


class TaskError(Exception):
    def __init__(self, task_name):
        super().__init__("Task {} failed when executing!!".format(task_name))


class TaskNotRunError(Exception):
    def __init__(self, task_name):
        super().__init__("Task {} run method must be called before running "
                         "the check_result method!!".format(task_name))


class TaskAlreadyRunException(Exception):
    def __init__(self, task_name):
        super().__init__("Task {} has already run. If you want to run the task twice,"
                         "create another one with the same characteristics!!"
                         .format(task_name))


class ResultFunctionError(Exception):
    def __init__(self, task_name):
        super().__init__("Result function for task {} failed"
                         " when executing!!".format(task_name))


class RunFailException(Exception):
    def __init__(self, task_name):
        super().__init__("The task {} result was unexpected!!".format(task_name))


@contextlib.contextmanager
def task_trace(log_dict, task_name):
    # What would be best than creating non idempotent functions in order to
    # build a library aimed to testing stateful systems
    t = time.time()
    task_dict = copy.deepcopy(TASK_DICT)
    log_dict["tasks"][task_name] = task_dict
    task_dict["status"]["task"] = "SUCCESS"
    try:
        yield
    except Exception as e:
        task_dict["status"]["task"] = "ERROR"
        raise e
    finally:
        task_dict["execution_time"] = format_time(t)


@contextlib.contextmanager
def verification_trace(log_dict, task_name):
    t = time.time()
    # I have the dict already saved in the log dictionary
    task_dict = log_dict["tasks"][task_name]
    task_dict["status"]["verification"] = "SUCCESS"
    try:
        yield
    except RunFailException as e:
        task_dict["status"]["verification"] = "FAILED"
        raise e
    except Exception as e:
        task_dict["status"]["verification"] = "ERROR"
        raise e
    finally:
        task_dict["verification_time"] = format_time(t)


@contextlib.contextmanager
def flow_trace(log_dict):
    t = time.time()
    log_dict["status"] = "SUCCESS"
    try:
        yield
    except RunFailException as e:
        log_dict["status"] = "FAILED"
    except Exception:
        log_dict["status"] = "ERROR"
        traceback.print_exc()
    finally:
        log_dict["total_elapsed_time"] = format_time(t)


class TaskResult(object):
    # This class is just a place holder to be used when specifying the
    # check_result functions for a Task class. If you want to use the task result
    # as a variable input, you can set this place holder
    pass


class Task(object):

    def __init__(self, name, task_function=None, task_args=None, task_kwargs=None,
                 result_function=None, result_args=None, result_kwargs=None):
        """
        Define a task to be executed. You must define a task_function when
        instantiating or using the add_execution_task function. Further,
        a checking function can be defined to be executed after the task has finished
        :param name: <str> The task name
        :param task_function: <function> The task execution main function
        :param task_args: <list> If your task uses positional arguments, pass them
            here as a list
        :param task_kwargs: <dict> If your task uses keyword arguments, pass them
            here as a dictionary
        :param result_function: <function> The result function. You can set a function
            to be executed after the task runs. You can use this function to check
            if the task did what it was supposed to do. Must return a boolean value
        :param result_args: <dict> If your result_function uses positional arguments,
            pass them here as a dictionary
        :param result_kwargs: <dict> If your result_function uses keyword arguments,
            pass them here as a dictionary
        """
        self.name = name

        self.__task_function = task_function
        self.__task_args = cast_to_args(task_args)
        self.__task_kwargs = cast_to_kwargs(task_kwargs)

        self.__result_function = result_function
        self.__result_args = cast_to_args(result_args)
        self.__result_kwargs = cast_to_kwargs(result_kwargs)

        self.__result = None
        self.__task_run = None

    @property
    def result(self):
        if self.__result is None:
            return TaskResult()
        else:
            return self.__result

    @result.setter
    def result(self, function_result):
        self.__result = function_result

    def run(self):
        """
        Run the main task
        :return:
        """
        if not self.__task_function:
            raise TaskNotDefined(self.name)
        if self.__task_run:
            raise TaskAlreadyRunException(self.name)
        try:
            self.__result = self.__task_function(*self.__task_args,
                                                 **self.__task_kwargs)
            self.__task_run = True
        except Exception:
            raise TaskError(self.name)

    def check_result(self):
        """
        If a verification result function was given. Execute it and success
        if this one return a positive boolean value
        :return:
        """
        if not self.__result_function:
            # If there is not a defined a result function. It is assumed the task
            # has completed successfully
            return True
        if self.__result is None:
            # If there isn't a result, the task was not run, and the result verification
            # cannot be called yet
            raise TaskNotRunError(self.name)
        try:
            mutated_args = [self.__result if isinstance(a, TaskResult) else a
                            for a in self.__result_args]
            fail_or_success = self.__result_function(*mutated_args,
                                                     **self.__result_kwargs)
        except Exception:
            raise ResultFunctionError(self.name)

        if not isinstance(fail_or_success, bool):
            raise TypeError("The expected Type for the task {} result function"
                            " must be boolean".format(self.name))
        return fail_or_success

    def add_execution_task(self, task_function, args=None, kwargs=None):
        """
        Add a execution task
        :param task_function: <function>
        :param args: The positional arguments of the function
        :param kwargs: The keyword arguments of the function
        :return:
        """
        self.__task_function = task_function
        self.__task_args = cast_to_args(args)
        self.__task_kwargs = cast_to_kwargs(kwargs)

    def add_result_function(self, result_function, args=None, kwargs=None):
        """
        Add a result function to be exectude after the task. The return value
        must be a boolean
        :param result_function: <function>
        :param args: The positional arguments of the function
        :param kwargs: The keyword arguments of the function
        :return: <bool>
        """
        self.__result_function = result_function
        self.__result_args = cast_to_args(args)
        self.__result_kwargs = cast_to_kwargs(kwargs)

    def copy(self):
        return Task(
            self.name, task_function=self.__task_function, task_args=self.__task_args,
            task_kwargs=self.__task_kwargs, result_function=self.__result_function,
            result_args=self.__result_args, result_kwargs=self.__result_kwargs
        )


class FlowPath(object):

    def __init__(self, task_path):
        """
        This is the flow the tasks will follow. A logging will be collected when
        calling the run function
        :param task_path: <list>.<Task>
        """
        self.path = cast_to_args(task_path)

        self.log = copy.deepcopy(LOG_DICT)

    def add_task(self, task):
        """
        Add a task to the task list. The task will be appended at the bottom of the
        execution path
        :param task: <Task>
        :return:
        """
        self.path.append(task)

    def __check_result(self, task):
        try:
            fail_or_success = task.check_result()
        except Exception as e:
            raise e

        if not isinstance(fail_or_success, bool):
            raise TypeError("The expected Type for the task {} result function"
                            " must be boolean".format(task.name))
        return fail_or_success

    def __run_task(self, task):
        # First, run the task
        with task_trace(self.log, task.name):
            try:
                task.run()
            except Exception:
                raise TaskError(task.name)
        # Then, check the result function returns a True value
        with verification_trace(self.log, task.name):
            expected_result = self.__check_result(task)
            if expected_result:
                return
            else:
                raise RunFailException(task.name)

    def __compute_log_aggregations(self):
        total_exec_time = total_verif_time = 0
        for t, values in self.log.get("tasks").items():
            task_exec_time = values.get("execution_time")
            if task_exec_time:
                total_exec_time += task_exec_time
            task_verif_time = values.get("task_verif_time")
            if task_verif_time:
                total_verif_time += task_verif_time
        self.log["total_execution_time"] = total_exec_time
        self.log["total_verification_time"] = total_verif_time

    def run(self):
        """
        Run the Flow Path following the order given in the path list
        :return: <dict> Returns the execution log
        """
        self.log["path"] = [t.name for t in self.path]
        with flow_trace(self.log):
            for task in self.path:
                self.__run_task(task)
                self.log["executed_path"].append(task.name)

        self.__compute_log_aggregations()
        return self.log

    def copy(self):
        tasks_copy = [t.copy() for t in self.path]
        return FlowPath(tasks_copy)


class ConcurrentFlows(object):
    """
    If you want to run concurrent flows, you can instantiate this class
    with a dictionary of FlowPath instances
    """
    def __init__(self, flow_dict=None):
        self.flow_list = {} if flow_dict is None else flow_dict

        self.__logs = None

    @property
    def logs(self):
        return self.__logs

    @logs.setter
    def logs(self, log_list):
        self.__logs = {ld[0]: ld[1].value for ld in log_list}

    def add_flow(self, flow_id, flow):
        """
        Add a flow path, or a list of flow paths
        :param flow_id: <str>. A flow path identifier
        :param flow: <list>.<FlowPath> or <FlowPath>
        :return:
        """
        if isinstance(flow, list):
            self.flow_list.extend(flow)
        else:
            self.flow_list.append(flow)

    def __run_flows_at_once(self):
        """
        Run all the flow path at the same time.
        :return:
        """
        id_list, path_jobs = [], []
        for fid, flow_path in self.flow_list.items():
            id_list.append(fid)
            path_jobs.append(gevent.spawn(flow_path.run))
        gevent.joinall(path_jobs)
        self.logs = zip(id_list, path_jobs)

    def run(self, options=None):
        """
        Run all the specified flows according to the passed options. The default
        running behaviour is to run all the flow Paths at once.
        :param options:
        :return:
        """
        if not options:
            self.__run_flows_at_once()
        return self.logs
