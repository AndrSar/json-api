import json
import inspect


class Specification:
    def __init__(self):
        self._methods = dict()

    def add_method(self, method):
        if callable(method):
            sig = inspect.signature(method)
            self._methods[method.__name__] = (sig, method)

    def invoke_method_from_json_request(self, json_request) -> Response:
        requested_method = None
        requested_args = None

        try:
            try:
                requested_method = json_request['method']
            except KeyError:
                raise MethodIsNotSpecifiedError()

            try:
                requested_args = json_request['args']
            except KeyError:
                raise MethodArgumentsAreNotSpecifiedError()

            try:
                sig, method = self._methods[requested_method]
            except KeyError:
                raise NoSuchMethodError(requested_method)
        
        except Error as e:
            return e.response


    def check_method_arguments(self, sig, method, args):
        try:
            for param in sig.parameters.values():
                if param.default == param.empty:
                    if (param.name in args)



class Response:
    def __init__(self, status: int, description: str, result=None):
        self._status = status
        self._description = description
        self._result = result

    

    def to_json_str(self):
        return {
            'status': self._status,
            'description': self._description,
            'result': self._result
            }


class Error(RuntimeError):
    def __init__(self, status: int, descr: str):
        self.response = Response(status, descr)


class MethodIsNotSpecifiedError(Error):
    def __init__(self):
        super().__init__(1, 'method is not specified')


class MethodArgumentsAreNotSpecifiedError(Error):
    def __init__(self):
        super().__init__(2, 'method arguments (`args list`) are not specified')


class NoSuchMethodError(Error):
    def __init__(self, input_method_name):
        super().__init__(3, 'no method `%s` exists' % input_method_name)
    