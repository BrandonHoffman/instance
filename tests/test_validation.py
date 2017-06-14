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
from instance.validators import *

class TestValidator:
    validator = Validator()
    success_cases = []
    failure_cases = [None]

    def test_validate_success(self):
        count = 0
        for success in self.success_cases:
            self.validator(success)
            count += 1
        assert(count == len(self.success_cases))
    
    def test_validate_failure(self):
        count = 0
        for failure in self.failure_cases:
            try:
                self.validator(failure)
            except:
                count += 1
        assert(count == len(self.failure_cases))
    
class TestNoneTypeValidator(TestValidator):
    validator = NoneTypeValidator()
    success_cases = [1, "test", [], {}]
    failure_cases = [None]
    
class TestNoneTypesValidator(TestValidator):
    validator = TypesValidator((str, int))
    success_cases = [1, "test"]
    failure_cases = [None, 1.0]
    
class TestMaxValidator(TestValidator):
    validator = MaxValidator(10, inclusive=False)
    success_cases = [5]
    failure_cases = [10, 11]
    
class TestMaxValidator2(TestValidator):
    validator = MaxValidator(10)
    success_cases = [5, 10]
    failure_cases = [11]

class TestMinValidator(TestValidator):
    validator = MinValidator(10, inclusive=False)
    success_cases = [11]
    failure_cases = [10, 5]
    
class TestMinValidator2(TestValidator):
    validator = MinValidator(10)
    success_cases = [11, 10]
    failure_cases = [5]

class TestMaxLengthValidator(TestValidator):
    validator = MaxLengthValidator(1, inclusive=False)
    success_cases = [[]]
    failure_cases = [[1], [1,2]]
    
class TestMaxLengthValidator2(TestValidator):
    validator = MaxLengthValidator(1)
    success_cases = [[], [1]]
    failure_cases = [[1,2]]

class TestMinLengthValidator(TestValidator):
    validator = MinLengthValidator(1, inclusive=False)
    success_cases = [[1, 2]]
    failure_cases = [[1], []]
    
class TestMinLengthValidator2(TestValidator):
    validator = MinLengthValidator(1)
    success_cases = [[1, 2], [1]]
    failure_cases = [[]]
