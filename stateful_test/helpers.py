import time


def cast_to_args(arg_values):
    if not arg_values:
        return []
    elif isinstance(arg_values, list):
        return arg_values
    elif isinstance(arg_values, tuple):
        return arg_values
    else:
        return [arg_values]


def cast_to_kwargs(kwarg_values):
    if not kwarg_values:
        return {}
    elif isinstance(kwarg_values, dict):
        return kwarg_values
    else:
        raise ValueError("{} is not a dictionary type".format(str(kwarg_values)))


def format_time(t_last):
    return round((time.time() - t_last) * 1000)
