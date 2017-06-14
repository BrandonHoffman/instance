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
from instance.types import *
from instance.types import SchemaType
import typing

class TestInteger:
    generic = int
    expected = Integer
    description = "Integer"
    class_description = "<Integer>"
    sucess_cases = [1]
    fail_cases = [1.0, "1", True, None]

    def test_generic(self):
        generic = mapped_type(self.generic)
        expected = mapped_type(self.expected)
        assert(generic.__class__ == self.expected)
        assert(expected.__class__ == self.expected)
        
        expected2 = self.expected()
        assert(len(generic.validators) == len(expected2.validators))
        assert(len(generic.validators) == len(expected2.validators))
        
        assert(repr(self.expected) == self.class_description)

        for idx, validator in enumerate(expected2.validators):
            assert(validator.__class__ == generic.validators[idx].__class__)
            assert(validator.__class__ == expected.validators[idx].__class__)

        assert(repr(expected) == self.description)
       
    def test_validate_success(self):
        num_tested = 0
        generic = mapped_type(self.generic)
        expected = mapped_type(self.expected)
        for case in self.sucess_cases:
            try:
                generic(case)
            except:
                assert(False)
            num_tested += 1
        assert(num_tested == len(self.sucess_cases))

    def test_validate_fail(self):
        generic = mapped_type(self.generic)
        expected = mapped_type(self.expected)
        failed = True
        num_tested = 0
        for case in self.fail_cases:
            try:
                print(generic(case))
                failed = False
            except:
                pass
            num_tested += 1
        assert(failed)
        assert(num_tested == len(self.fail_cases))
        
class TestDouble(TestInteger):
    generic = float
    expected = Double
    description = "Double"
    class_description = "<Double>"
    sucess_cases = [1, 1.0]
    fail_cases = ["1", True, None]

class TestString(TestInteger):
    generic = str
    expected = String
    description = "String"
    class_description = "<String>"
    sucess_cases = ["hello"]
    fail_cases = [1, 1.0, True, None]
        
class TestBoolean(TestInteger):
    generic = bool
    expected = Boolean
    description = "Boolean"
    class_description = "<Boolean>"
    sucess_cases = [True, False]
    fail_cases = [1, 1.0, "True", None]
        
class TestAny(TestInteger):
    generic = typing.Any
    expected = Any
    description = "<Any>"
    class_description = "<Any>"
    sucess_cases = [1, 1.0, "test", True]
    fail_cases = [None]

class TestOptional(TestInteger):
    generic = typing.Optional
    expected = Optional
    description = "Optional<<Any>>"
    class_description = "<Optional>"
    sucess_cases = [1, 1.0, "test", True, None]
    fail_cases = []

class TestOptional2(TestInteger):
    generic = typing.Optional[int]
    expected = Optional[Integer]
    description = "Optional<Integer>"
    class_description = "<Optional[Integer]>"
    sucess_cases = [1, None]
    fail_cases = [1.0, "1", True, [], {}]

class TestOptional3(TestInteger):
    generic = typing.Union[int, None]
    expected = Optional[Integer]
    description = "Optional<Integer>"
    class_description = "<Optional[Integer]>"
    sucess_cases = [1, None]
    fail_cases = [1.0, "1", True, [], {}]

class TestDictionary(TestInteger):
    generic = typing.Dict
    expected = Dictionary
    description = "{<Any>: <Any>}"
    class_description = "<Dictionary>"
    sucess_cases = [{}]
    fail_cases = [1.0, "1", True, [], None]

class TestDictionary2(TestInteger):
    generic = typing.Dict[str, int]
    expected = Dictionary[String, Integer]
    description = "{String: Integer}"
    class_description = "<Dictionary[String, Integer]>"
    sucess_cases = [{}, {"test": 1}]
    fail_cases = [1.0, "1", True,{1: 1}, {"test": 1.0}, [], None]
    
    
class TestList(TestInteger):
    generic = typing.List
    expected = List
    description = "[<Any>]"
    class_description = "<List>"
    sucess_cases = [[]]
    fail_cases = [1.0, "1", True, {}, None]

class TestList2(TestInteger):
    generic = typing.List[int]
    expected = List[Integer]
    description = "[Integer]"
    class_description = "<List[Integer]>"
    sucess_cases = [[], [1,2]]
    fail_cases = [1.0, "1", True, {}, None, ["test"]]

class TestUnion(TestInteger):
    generic = typing.Union
    expected = Union
    description = "Union<<Any>, <Any>>"
    class_description = "<Union>"
    sucess_cases = [1, True, "test"]
    fail_cases = [None]

class TestUnion2(TestInteger):
    generic = typing.Union[int, str]
    expected = Union[Integer, String]
    description = "Union<Integer, String>"
    class_description = "<Union[Integer, String]>"
    sucess_cases = [1, "test"]
    fail_cases = [True, None, 1.0, [], {}]

class TestNewType:
    def test_create_validated_type(self):
        def test_validator(val):
            pass

        test_type = create_validated_type('test_type', typing.List[int], validators=[test_validator])

        new_type = mapped_type(test_type)
        old_type = List[Integer]([test_validator])
        for idx, validator in enumerate(old_type.validators):
            assert(validator.__class__ == new_type.validators[idx].__class__)

        assert(test_validator in new_type.validators)
        assert(repr(new_type) == "<test_type>")

class TestSchema:
    class Car(Schema):
        make: str
        model: str
        year: int

    def test_simple_schema(self):
        assert TestSchema.Car.__annotations__["make"].__class__ == String
        assert TestSchema.Car.__annotations__["model"].__class__ == String
        assert TestSchema.Car.__annotations__["year"].__class__ == Integer

        car = TestSchema.Car.from_json({
                'make': 'test',
                'model': 'test_model',
                'year': 2007,
            })

        assert car.make == 'test'
        assert car.model == 'test_model'
        assert car.year == 2007
        
        assert repr(TestSchema.Car.from_json) == "<SchemaType[<Car>]>"

    def test_defaults(self):
        class ToyotaCar(TestSchema.Car):
            make: str = "Toyota"

        car = ToyotaCar.from_json({
                'model': 'test_model',
                'year': 2007,
            })

        assert car.make == 'Toyota'
        assert car.model == 'test_model'
        assert car.year == 2007

    def test_simple_subclass(self):
        class ElectricCar(TestSchema.Car):
            battery_size: int

        assert ElectricCar.__annotations__["make"].__class__ == String
        assert ElectricCar.__annotations__["model"].__class__ == String
        assert ElectricCar.__annotations__["year"].__class__ == Integer
        assert ElectricCar.__annotations__["battery_size"].__class__ == Integer

        car = ElectricCar.from_json({
                'make': 'test',
                'model': 'test_model',
                'year': 2007,
                'battery_size': 100000
            })
        car.validate()

        assert car.make == 'test'
        assert car.model == 'test_model'
        assert car.year == 2007
        assert car.battery_size == 100000

        car.year = "test"
        failed_validate = True
        try:
            car.validate()
            failed_validate = False
        except:
            pass
        assert(failed_validate)

        failed_validate = True
        try:
            car = ElectricCar.from_json({
                    'make': 'test',
                    'model': 'test_model',
                    'year': '2007',
                    'battery_size': 100000
                })
            failed_validate = False
        except:
            pass
        assert(failed_validate)

    def test_nested_schema(self):
        class Driver(Schema):
            name: str = "Joe"
            car: TestSchema.Car

        assert Driver.__annotations__["name"].__class__ == String
        assert Driver.__annotations__["car"] == TestSchema.Car.from_json
        driver = Driver.from_json({
                'car': {
                    'make': 'test',
                    'model': 'test_model',
                    'year': 2007
                }
            })

        failed = False
        try:
            driver2 = Driver.from_json({
                    'car': {
                        'make': 'test',
                        'model': 'test_model'
                    }
                })
        except:
            failed = True
        assert failed

        assert(driver.name == "Joe")
        assert(driver.car.model == "test_model")
        assert(driver.car.make == "test")
        assert(driver.car.year == 2007)
        driver.validate()

        json = driver.to_json()
        assert(json["name"] == "Joe")
        assert(json["car"]["model"] == "test_model")
        assert(json["car"]["make"] == "test")
        assert(json["car"]["year"] == 2007)

T = typing.TypeVar('T')
class TestGenericSchema:
    class GenericTestSchema(Schema, typing.Generic[T]):
        x: T
        y: List[T]

    def test_simple(self):
        assert TestGenericSchema.GenericTestSchema.__annotations__["x"].__class__ == typing.TypeVar
        assert TestGenericSchema.GenericTestSchema.__annotations__["y"].__class__ == List[T]

        assert TestGenericSchema.GenericTestSchema[int].__annotations__["x"].__class__ == Integer
        assert TestGenericSchema.GenericTestSchema[int].__annotations__["y"].__class__ == List[Integer]

        assert TestGenericSchema.GenericTestSchema[float].__annotations__["x"].__class__ == Double
        assert TestGenericSchema.GenericTestSchema[float].__annotations__["y"].__class__ == List[Double]

        assert TestGenericSchema.GenericTestSchema[int].__annotations__["x"].__class__ == Integer
        assert TestGenericSchema.GenericTestSchema[int].__annotations__["y"].__class__ == List[Integer]

    def test_subclass_generic(self):
        class Gen2(TestGenericSchema.GenericTestSchema[int]):
            pass

        assert Gen2.__annotations__["x"].__class__ == Integer
        assert Gen2.__annotations__["y"].__class__ == List[Integer]


    def test_subclass_generic_2(self):
        class Gen2(TestGenericSchema.GenericTestSchema[int], typing.Generic[T]):
            z: T

        assert Gen2.__annotations__["x"].__class__ == Integer
        assert Gen2.__annotations__["y"].__class__ == List[Integer]
        assert Gen2.__annotations__["z"].__class__ == typing.TypeVar

        assert Gen2[float].__annotations__["x"].__class__ == Integer
        assert Gen2[float].__annotations__["y"].__class__ == List[Integer]
        assert Gen2[float].__annotations__["z"].__class__ == Double
