# -*- coding: utf-8 -*-

# import re

from Framework.Exception import ATException


def validate(**params):
    """Validate function's parameters

    Example：
            @funValidate(a=str, b=int)
            def func(a, b):
                pass
    """

    def validateTypes(function):

        argCount = function.func_code.co_argcount

        for varName in function.func_code.co_varnames:
            if varName == 'self':
                argCount -= 1

        if len(params) != argCount:
            raise ATException('Method: %s access params number invalid' % function.func_name)

        def tempFunction(*args, **kargs):

            for index, var in enumerate(args):
                if function.func_code.co_varnames[index] in params \
                        and not isinstance(var, params[function.func_code.co_varnames[index]]):
                    raise ATException('Method[%s] param[%s] type invalid'
                                      % (function.func_name, function.func_code.co_varnames[index]))
            for key, var in kargs.iteritems():
                if key in params and not isinstance(var, params[key]):
                    raise ATException('Method[%s] param[%s] type invalid' % (function.func_name, params[key]))
            return function(*args, **kargs)

        tempFunction.func_name = function.func_name
        return tempFunction

    return validateTypes
