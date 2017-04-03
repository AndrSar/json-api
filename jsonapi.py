import json
import inspect


class Specification:
    def __init__(self):
        self._methods = dict()

    def add_method(self, method):
        if callable(method):
            sig = inspect.signature(method)
            self._methods[method.__name__] = (sig, method)

    def invoke_method(self, dictionary):
        requested_method = None
        requested_args = None

        try:
            try:
                requested_method = dictionary['method']
            except KeyError:
                raise MethodIsNotSpecifiedError()

            try:
                requested_args = dictionary['args']
            except KeyError:
                raise MethodArgumentsAreNotSpecifiedError()

            try:
                sig, method = self._methods[requested_method]
                self.check_method_arguments(sig, requested_args)
                result = method(**requested_args)
                return Result('OK', result)

            except KeyError:
                raise NoSuchMethodError(requested_method)

        except Error as e:
            return e.response


    def check_method_arguments(self, sig, args):
        for param in sig.parameters.values():
            try:
                arg = args[param.name]
                if param.annotation != param.empty:
                    if param.annotation is not type(arg):
                        received_type = type(arg).__name__
                        expected_type = param.annotation.__name__
                        raise InvalidArgumentTypeError(param.name, received_type, expected_type)
            except KeyError:
                raise RequiredArgumentIsMissedError(param.name)



class Result:
    def __init__(self, description: str, result=None, exception_type=None):
        self._description = description
        self._result = result
        self._exception_type = exception_type

    def to_dict(self):
        return {
            'result': self._result,
            'description': self._description,
            'exception': self._exception_type.__name__
            }

    def get_result(self):
        return self._result

    def is_exception(self, exception_type):
        return self._exception_type is exception_type


class Error(RuntimeError):
    def __init__(self, type, descr: str):
        self.response = Result(descr, None, type)


class MethodIsNotSpecifiedError(Error):
    def __init__(self):
        super().__init__(type(self), 'method is not specified')


class MethodArgumentsAreNotSpecifiedError(Error):
    def __init__(self):
        super().__init__(type(self), 'method arguments (`args list`) are not specified')


class NoSuchMethodError(Error):
    def __init__(self, input_method_name):
        super().__init__(type(self), 'no method `%s` exists' % input_method_name)


class RequiredArgumentIsMissedError(Error):
    def __init__(self, arg_name: str):
        super().__init__(type(self), 'required argument `%s` is missed' % arg_name)


class InvalidArgumentTypeError(Error):
    def __init__(self, name: str, received: str, expected: str):
        super().__init__(type(self), 'argument `%s` has invalid type `%s`, `%s` expected' % (name, received, expected))
