***************
Instance
***************

instance aims to provide a simple way to create json schemas to be used for validation purposed in python3.

============
How to use
============

To create a new Json Type simple add type annotations to a python class that inherits from Schema like so


    from instance.types import Schema, String, Integer, List
    
    class Car(Schema):
        make: String
        model: String
        year: Integer
        passengers: List[String]



We even support creating a Schema using native python types and types from the python 3's typing module.

    from instance.types import Schema
    from typing import List
    
    class Car(Schema):
        make: str
        model: str
        year: int
        passengers: List[str]

=====================
providing defaults
=====================

instance uses class instance variable values as the default value when a None value is used for a value in json. If for instance we wanted to instantiate passangers as an empty list by default we could do this simply by adding an = [] to its definition like so.

    from instance.types import Schema
    from typing import List
    
    class Car(Schema):
        make: str
        model: str
        year: int
        passengers: List[str] = []

==================
Adding Validation
==================

to add custom validation simple provide a list of validators to the type annotation and let instance take care of the rest


    from instance.types import Schema, String, Integer, List
    from instance.validators import MinValidator, MaxValidator
    
    class Car(Schema):
        make: String
        model: String
        year: Integer(validators=[MinValidator(1950), MaxValidator(2017)])
        passengers: List[String]



Custom validators can be made by creating a function or callable object like so. in the event a validation error occurs Simply throw a ValidationErrorException

    from instance.validators import ValidationError
    
    def starts_capital(val):
        if not val[0].isupper():
            raise ValidationErrorException(431, "Must start with capital letter")

for validators that need parameters create a class and define a __call__ method like so

    from instance.validators import ValidationError
    
    class NumWords:
        def __init__(self, num_words):
            self.num_words = num_words

        
        def __call__(self, val):
            if len(val.split(' ')) != self.num_words:
                raise ValidationErrorException(432, "Must contain at least {num} words".format(num=self.num_words))

to use these new validators simply include them in the list of validators like so

    class Car(Schema):
        make: String
        model: String
        year: Integer(validators=[MinValidator(1950), MaxValidator(2017)])
        passengers: List[String(validators=[starts_capital, NumWords(2)])



==================
Reducing the bloat
==================

you can imagine that for fields with large amounts of validators listing all of them can make it a lot harder to read and update. For this reason instance provides a function to define new types with a set of default validators. This also makes sharing validated types easy across multiple fields on a single Schema and even across multiple Schemas.

    from instance.types import create_validated_type(name, type, validators=[]), Schema, String, Integer, List
    
    name = create_validated_type("name", str, [starts_capital, NumWords(2)])
    year = create_validated_type("year", Integer, [MinValidator(1950), MaxValidator(2017)
    
    class Car(Schema):
        make: String
        model: String
        year: year
        owner: name
        passengers: List[name])

==================
Nested Schema's
==================

Schemas can also be used inside other schema annotations and even as generics parameters like so

    from instance.types import create_validated_type(name, type, validators=[]), Schema, String, Integer, List
    
    name = create_validated_type("name", str, [starts_capital, NumWords(2)])
    class Person(Schema):
        name: name
        age: int
    
    year = create_validated_type("year", Integer, [MinValidator(1950), MaxValidator(2017)
    class Car(Schema):
        make: String
        model: String
        year: year
        owner: Person
        passengers: List[Person])

=====================
subclassing Schema's
=====================

Schemas can be used as subclass in order to create more complex types

    from instance.types import create_validated_type(name, type, validators=[]), Schema, String, Integer, List
    
    name = create_validated_type("name", str, [starts_capital, NumWords(2)])
    class Person(Schema):
        name: name
        age: int
    
    year = create_validated_type("year", Integer, [MinValidator(1950), MaxValidator(2017)
    class Car(Schema):
        make: String
        model: String
        year: year
        owner: Person
        passengers: List[Person])
    
    class ElectricCar(Car):
        battery_capacity: int

