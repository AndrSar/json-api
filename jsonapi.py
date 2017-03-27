import json
import inspect


class Specification:
    def __init__(self):
        self._methods = dict()

    def add_method(self, method):
        if callable(method):
            sig = inspect.signature(method)
            self._methods[method.__name__] = (sig, method)

    def invoke_method_from_json_request(self, json_request):
        if 'method' not in json_request:
            raise MethodIsNotSpecifiedError()

        if 'args' not in json_request:
            raise MethodArgumentsAreNotSpecifiedError()

        requested_method = json_request['method']
        if requested_method not in self._methods:
            raise NoSuchMethodError(requested_method)

        sig, method = self._methods[requested_method]

    def check_method_arguments(self, sig, method, args):
        #for param in sig.parameters.values():
        #    if param.default == param.empty:
        pass


class Error(RuntimeError):
    def __init__(self, descr: str):
        self.code = 1
        self.descr = descr


class MethodIsNotSpecifiedError(Error):
    def __init__(self):
        super().__init__('method is not specified')


class MethodArgumentsAreNotSpecifiedError(Error):
    def __init__(self):
        super().__init__('method arguments (`args list`) are not specified')


class NoSuchMethodError(Error):
    def __init__(self, input_method_name):
        super().__init__('no method `%s` exists' % input_method_name)
    