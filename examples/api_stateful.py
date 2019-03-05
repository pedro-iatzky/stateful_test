def function_a(foo):
    print(foo)
    return foo


def use_task_result(func):
    def result_exec(*args, **kwargs):
        print(self.foo)
        return func(result_var, *args, **kwargs)
    return result_exec


@use_task_result
def function_b(task_result, foo):
    print(task_result, foo)



def result_function(arg_a, TaskResult):
    pass


for a in args:
    if isinstance(a, TaskResult):
        a = self.result




task_a = Task("task_a", function=function_a, function_args=None)
task_a.add_result_function(function_b, baz, TaskResult)


PathFlow[task_a, task_b, task_c]
