import inspect


class Specification:
    def __init__(self):
        self._methods = dict()

    def add_method(self, method, validation_predicates=dict()):
        if callable(method):
            sig = inspect.signature(method)
            self._methods[method.__name__] = (sig, method, validation_predicates)

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
                sig, method, predicates = self._methods[requested_method]
                self._check_method_arguments(sig, requested_args, predicates)
                result = method(**requested_args)
                return Result('OK', result)

            except KeyError:
                raise NoSuchMethodError(requested_method)

        except Error as error:
            return error.response


    def _check_method_arguments(self, sig, args, predicates):
        if len(sig.parameters) != len(args):
            raise WrongArgumentsNumberError(len(args), len(sig.parameters))

        for param in sig.parameters.values():
            try:
                param_name = param.name
                arg = args[param_name]
                if param.annotation != param.empty:
                    if param.annotation is not type(arg):
                        received_type = type(arg).__name__
                        expected_type = param.annotation.__name__
                        raise InvalidArgumentTypeError(param_name, received_type, expected_type)

                if param_name in predicates:
                    if not predicates[param_name](arg):
                        raise InvalidArgumentValueError(param_name)

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
        super().__init__(descr)
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


class WrongArgumentsNumberError(Error):
    def __init__(self, received: int, expected: int):
        super().__init__(type(self), 'wrong arguments number, expected %u, but got %u' % (expected, received))


class InvalidArgumentTypeError(Error):
    def __init__(self, name: str, received: str, expected: str):
        super().__init__(type(self), 'argument `%s` has invalid type `%s`, `%s` expected' % (name, received, expected))


class InvalidArgumentValueError(Error):
    def __init__(self, name: str):
        super().__init__(type(self), 'value of argument `%s` does not pass predicate condition' % name)
