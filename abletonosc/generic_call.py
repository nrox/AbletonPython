import inspect
from typing import Tuple

import Live  # type: ignore

from .handler import AbletonOSCHandler


def parse_code(args):
    """
    Return the code to execute and a flag for inspection.
    """
    code = str(args[0])
    debug_flag = (len(args) > 1) and (args[1] == "debug")
    return code, debug_flag


class GenericCallHandler(AbletonOSCHandler):
    def init_api(self):
        """This code is not safe: usage of eval and exec."""

        def post_eval(args) -> Tuple:
            code, debug = parse_code(args)
            result = eval(code)
            if debug:
                output = OutputLogger()
                introspect_module(result, output)
                return str(result), str(output),
            return str(result),

        def post_exec(args) -> Tuple:
            code, debug = parse_code(args)
            result = []
            exec(code)
            if debug:
                output = OutputLogger()
                introspect_module(result, output)
                return str(result), str(output),
            return str(result),

        self.osc_server.add_handler("/live/eval", post_eval)
        self.osc_server.add_handler("/live/exec", post_exec)


class OutputLogger:
    def __init__(self):
        self.logs: list[str] = []

    def info(self, msg: str):
        self.logs.append(msg)

    def __str__(self):
        return "\n".join(self.logs)


def introspect_module(module, logger: OutputLogger):
    logger.info("Introspect: %s" % module)
    for name in dir(module):
        obj = getattr(module, name)
        if inspect.ismodule(obj):
            introspect_module(obj, logger)
        elif inspect.isclass(obj):
            logger.info("Class: %s" % name)
            members = inspect.getmembers(obj)

            logger.info("Builtins")
            for name, member in members:
                if inspect.isbuiltin(member):
                    logger.info(" - %s" % (name))

            logger.info("Functions")
            for name, member in members:
                if inspect.isfunction(member):
                    logger.info(" - %s" % (name))

            logger.info("Properties")
            for name, member in members:
                if str(type(member)) == "<type 'property'>":
                    logger.info(" - %s" % (name))

            logger.info("----------")

    for name in dir(module):
        obj = getattr(module, name)
        if inspect.ismethod(obj) or inspect.isfunction(obj):
            logger.info("Method %s" % obj)
