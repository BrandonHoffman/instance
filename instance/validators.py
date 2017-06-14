"""
MIT License

Copyright (c) 2017 Brandon Hoffman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

class ValidationException(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def error(self):
        return {
            "code": self.code,
            "message": self.msg
        }

class SchemaValidationException(ValidationException):
    def __init__(self, errors):
        self.errors = errors

    def error(self):
        return self.errors

class Validator:
    def __call__(self, val):
        raise Exception("Uniplemented Validator")

class NoneTypeValidator(Validator):
    def __init__(self):
        self.none_type_exception = ValidationException(1, "None type not permitted")

    def __call__(self, val):
        if val == None:
            raise self.none_type_exception

class TypesValidator(Validator):
    def __init__(self, types):
        self.types = types
        self.none_type_exception = ValidationException(2, "unexpected type")

    def __call__(self, val):
        if type(val) not in self.types:
            raise self.none_type_exception

class MaxValidator(Validator):
    def __init__(self, max, inclusive=True):
        self.max = max
        self.inclusive = inclusive
        operator = inclusive and ">=" or ">"
        self.max_exceeded_exception = ValidationException(3, "value must be {operator} {max}".format(operator=operator, max=max))

    def __call__(self, val):
        if val > self.max or val == self.max and not self.inclusive:
            raise self.max_exceeded_exception

class MinValidator(Validator):
    def __init__(self, min, inclusive=True):
        self.min = min
        self.inclusive = inclusive
        operator = inclusive and "<=" or "<"
        self.min_exceeded_exception = ValidationException(4, "value must be {operator} {min}".format(operator=operator, min=min))

    def __call__(self, val):
        if val < self.min or val == self.min and not self.inclusive:
            raise self.min_exceeded_exception

class MaxLengthValidator(Validator):
    def __init__(self, max, inclusive=True):
        self.max = max
        self.inclusive = inclusive
        operator = inclusive and ">=" or ">"
        self.max_exceeded_exception = ValidationException(5, "value must have length {operator} {max}".format(operator=operator, max=max))

    def __call__(self, val):
        if len(val) > self.max or len(val) == self.max and not self.inclusive:
            raise self.max_exceeded_exception

class MinLengthValidator(Validator):
    def __init__(self, min, inclusive=True):
        self.min = min
        self.inclusive = inclusive
        operator = inclusive and "<=" or "<"
        self.min_exceeded_exception = ValidationException(6, "value must have length {operator} {min}".format(operator=operator, min=min))

    def __call__(self, val):
        if len(val) < self.min or len(val) == self.min and not self.inclusive:
            raise self.min_exceeded_exception
