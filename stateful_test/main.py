"""
    Main functionality to be used with command line.
    * Acknowledgments for the locust library team, from which I have
    borrowed many functions and code structure
"""
import importlib
import logging
import json
import os
import sys
from optparse import OptionParser

from .core import FlowPath


def parse_options():
    parser = OptionParser(usage="stateful_test [options]")

    parser.add_option(
        '-f', '--flowfile',
        dest='flowfile',
        default='flowfile',
        help='Python file with the flow path, e.g. "../api_test.py. Default: flowfile"'
    )

    parser.add_option(
        '-o', '--outputfile',
        action='store',
        type='str',
        dest='outputfile',
        default=None,
        help="Path to log file. If not set, log will go to stdout/stderr",
    )

    opts, args = parser.parse_args()
    return parser, opts, args


def _is_package(path):
    """
    Is the given path a Python package?
    """
    return (
        os.path.isdir(path)
        and os.path.exists(os.path.join(path, '__init__.py'))
    )


def find_flowfile(flowfile):
    """
    Attempt to locate a flowfile, either explicitly or by searching parent dirs.
    """
    # Obtain env value
    names = [flowfile]
    # Create .py version if necessary
    if not names[0].endswith('.py'):
        names += [names[0] + '.py']
    # Does the name contain path elements?
    if os.path.dirname(names[0]):
        # If so, expand home-directory markers and test for existence
        for name in names:
            expanded = os.path.expanduser(name)
            if os.path.exists(expanded):
                if name.endswith('.py') or _is_package(expanded):
                    return os.path.abspath(expanded)
    else:
        # Otherwise, start in cwd and work downwards towards filesystem root
        path = os.path.abspath('.')
        while True:
            for name in names:
                joined = os.path.join(path, name)
                if os.path.exists(joined):
                    if name.endswith('.py') or _is_package(joined):
                        return os.path.abspath(joined)
            parent_path = os.path.dirname(path)
            if parent_path == path:
                # we've reached the root path which has been checked this iteration
                break
            path = parent_path
    return None


def is_flowpath(tup):
    """
    Takes (name, object) tuple, returns True if it's a public Locust subclass.
    """
    name, item = tup
    return bool(
        isinstance(item, FlowPath)
        and not name.startswith('_')
    )


def load_flowfile(path):
    """
    Import given flowfile path and return (docstring, callables).
    Specifically, the flowfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is_flowpath" test.
    """

    def __import_flowfile__(filename, path):
        """
        Loads the flowfile as a module, similar to performing `import`
        """
        source = (importlib.machinery.
                  SourceFileLoader(os.path.splitext(flowfile)[0], path))
        imported = source.load_module()
        return imported

    # Get directory and flowfile name
    directory, flowfile = os.path.split(path)
    # If the directory isn't in the PYTHONPATH, add it so our import will work
    added_to_path = False
    index = None
    if directory not in sys.path:
        sys.path.insert(0, directory)
        added_to_path = True
    # If the directory IS in the PYTHONPATH, move it to the front temporarily,
    # otherwise other flowfiles -- like flowfile's own -- may scoop the intended
    # one.
    else:
        i = sys.path.index(directory)
        if i != 0:
            # Store index for later restoration
            index = i
            # Add to front, then remove from original position
            sys.path.insert(0, directory)
            del sys.path[i + 1]
    # Perform the import
    imported = __import_flowfile__(flowfile, path)
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]
    # Return our two-tuple
    flowpaths = dict(filter(is_flowpath, vars(imported).items()))
    return imported.__doc__, flowpaths


def write_log(out_dict, output_file=None):
    if output_file:
        with open(output_file, 'w') as log_file:
            json.dump(out_dict, log_file, indent=4)
    else:
        print(json.dumps(out_dict, indent=4))


def main():
    parser, options, arguments = parse_options()

    flowfile = find_flowfile(options.flowfile)
    logger = logging.getLogger(__name__)

    if not flowfile:
        logger.error(
            "Could not find any flowfile! Ensure file ends in '.py'"
            " and see --help for available options.")
        sys.exit(1)

    docstring, flowpaths = load_flowfile(flowfile)

    if not flowpaths:
        logger.error("No FlowPath instances found!")
        sys.exit(1)

    out_dict = {}
    for path_name, obj in flowpaths.items():
        logger.info("Starting execution of Flow Path {}".format(path_name))
        out_dict[path_name] = obj.run()

    write_log(out_dict, output_file=options.outputfile)
    if options.outputfile:
        logger.info("You can review the execution results in {}"
                    .format(options.outputfile))
