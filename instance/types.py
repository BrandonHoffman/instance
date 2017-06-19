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

import typing
from typing import GenericMeta
from instance.validators import NoneTypeValidator, TypesValidator, ValidationException, SchemaValidationException
 
generics_map = {}
 
def map_type(generic):
    def decorator(func, validators=[]):
        inited = func(validators=validators)
        generics_map[generic] = inited
        generics_map[func] = inited
        return func
    return decorator

def new_validators(original_class, new_type):
    return hasattr(original_class, "validators") and original_class.validators or new_type.validators
    
def mapped_type(original):
    if getattr(original, "is_schema", False):
        return original.from_json
    elif hasattr(original, "__args__") and original.__args__:
        original_class = original.__origin__
        new = generics_map.get(original_class, original_class)
        new_validators_list = new_validators(original_class, new)
        new = new.__class__[original.__args__](validators=new_validators_list)
        return new
    else:
        new = generics_map.get(original, original)
        return new
    
def create_type(types, desc):
    standard_validators = [NoneTypeValidator(), TypesValidator(types)]
    class NewType(Type):
        base_validators = list(standard_validators)

        def __init__(self, validators=[]):
            self.validators = list(validators)
            self.all_validators = []
            self.all_validators += self.base_validators
            self.all_validators += self.validators

        def __repr__(self):
            return desc
    NewType.__valid_types__ = types
    NewType.__name__ = desc
    return NewType
 
def create_validated_type(name, type, validators=[]):
    new_type = typing.NewType(name, type)
    old_type = mapped_type(type)
    new_validators = list(old_type.validators)
    new_validators.extend(validators)
    class NewValidatedType(old_type.__class__):
        def __repr__(self):
            return "<{name}>".format(name=name)
    map_type(new_type)(NewValidatedType, validators=new_validators)
    return new_type

T = typing.TypeVar('T')
K = typing.TypeVar('K')
V = typing.TypeVar('V')
 
class TypeMeta(typing.GenericMeta):
    def __new__(cls, name, parents, dct, **kwargs):
        args = kwargs.get("args", [])
        parameters = dct.get("__parameters__", [])
        new_args = []
        types_map = {}
        for idx, arg in enumerate(args):
            new_arg = mapped_type(arg)
            new_args.append(new_arg)
            param = parameters[idx]
            types_map[param] = new_arg 

        for parent in parents:
            types_map.update(getattr(parent, "_variable_map", {}))

        dct["_variable_map"] = types_map


        if new_args:
            kwargs["args"] = new_args
            
        obj = super(TypeMeta, cls).__new__(cls, name, parents, dct, **kwargs)
        return obj

    def __repr__(self):
        if(hasattr(self, "__args__") and self.__args__):
            args = [repr(arg) for arg in self.__args__]
            args = ", ".join(args)
            return "<{name}[{args}]>".format(name=self.__name__, args=args) 
        else:
            return "<{name}>".format(name=self.__name__) 

class UnionMeta(TypeMeta):
    def __new__(cls, name, parents, dct, **kwargs):
        args = kwargs.get("args", [])
        if args and args[1] == None.__class__:
            return Optional[args[0]]
        else:
            return super(UnionMeta, cls).__new__(cls, name, parents, dct, **kwargs)
    
 
class Genericable:
    @classmethod
    def get_actual_type(cls, generic_type):
        actual_type = cls._variable_map.get(generic_type, generic_type)
        if actual_type == generic_type:
            return any
        return actual_type

class Type(Genericable, metaclass = TypeMeta):
    _is_type = True
    base_validators = []
    def __init__(self, validators=[]):
        self.validators = list(validators)
        self.all_validators = []
        self.all_validators += self.base_validators
        self.all_validators += self.validators

    def validate(self, _val):
        for validator in self.all_validators:
            validator(_val)
        return _val

    def __call__(self, _val):
        self.validate(_val)
        return _val


@map_type(typing.Any)
class Any(Type):
    base_validators = [NoneTypeValidator()]

    def __repr__(self):
        return "<Any>"
 
any = Any()

Integer = create_type(types=(int,), desc="Integer")
map_type(int)(Integer)
 
String = create_type(types=(str,), desc="String")
map_type(str)(String)
 
Double = create_type(types=(float, int), desc="Double")
map_type(float)(Double)
 
Boolean = create_type(types=(bool,), desc="Boolean")
map_type(bool)(Boolean)
 
@map_type(typing.Dict)
class Dictionary(Type, typing.Generic[K, V]):
    base_validators = [NoneTypeValidator(), TypesValidator((dict,))]
    def __init__(self, validators=[]):
        self.validators = list(validators)
        self.all_validators = []
        self.all_validators += self.base_validators
        self.all_validators += self.validators

    def validate(self, _val):
        for validator in self.all_validators:
            validator(_val)

        actual_key_type = self.get_actual_type(K)
        actual_val_type = self.get_actual_type(V)
        for (key, value) in _val.items():
            actual_key_type(key)
            actual_val_type(value)

    def __repr__(self):
        return "{{{key}: {val}}}".format(key = self.get_actual_type(K), val = self.get_actual_type(V)) 
 
@map_type(typing.List)
class List(Type, typing.Generic[T]):
    base_validators = [NoneTypeValidator(), TypesValidator((list,))]

    def __init__(self, validators=[]):
        self.validators = validators
        self.all_validators = []
        self.all_validators += self.base_validators
        self.all_validators += self.validators

    def validate(self, _val):
        for validator in self.all_validators:
            validator(_val)

        errors = []
        actual_type = self.get_actual_type(T)
        for (index, value) in enumerate(_val):
            try:
                actual_type.validate(value)
            except ValidationException as e:
                error = e.error()
                error["index"] = index
                errors.append(error)
               
        if errors:
            raise SchemaValidationException(errors)

    def __repr__(self):
        return "[{type}]".format(type = self.get_actual_type(T)) 
 
 
@map_type(typing.Optional)
class Optional(Type, typing.Generic[T]):
    def validate(self, val):
        if val != None:
            actual_type = self.get_actual_type(T)
            actual_type(val)
 
    def __repr__(self):
        return "Optional<{type}>".format(type = self.get_actual_type(T)) 

@map_type(typing.Union)
class Union(Type, typing.Generic[T, K], metaclass=UnionMeta):
    def validate(self, _val):
        errors = []
        for generic in (T, K):
            actual_type = self.get_actual_type(generic)
            try:
                actual_type(_val)
                return _val
            except ValidationException as e:
                error = e.error()
                errors.append(error)
        raise SchemaValidationException(errors)

    def __repr__(self):
        return "Union<{type}, {type2}>".format(type = self.get_actual_type(T), type2 = self.get_actual_type(K)) 
 
class SchemaType(Type):
    def __init__(self, schema, validators=[]):
        self.schema = schema
        self.validators = validators
        self.all_validators = []
        self.all_validators += self.base_validators
        self.all_validators += self.validators

    def __call__(self, _val):
        self.validate(_val)
        obj = self.schema()
        errors = {}
        for (key, type) in self.schema.__annotations__.items():
            if key in _val:
                val = _val.get(key, None)
            else:
                val = getattr(obj, key, None)
            try:
                new_val = type(val)
                setattr(obj, key, new_val)
            except ValidationException as e:
                errors[key] = e.error()
        if errors:
            raise SchemaValidationException(errors)
        return obj

    def __repr__(self):
        return "<SchemaType[{schema}]>".format(schema=self.schema) 

class SchemaMeta(TypeMeta):
    def __new__(cls, name, parents, dct, **kwargs):
        args = kwargs.get("args", [])
        parameters = dct.get("__parameters__", [])
        new_args = []
        types_map = {}

        for idx, arg in enumerate(args):
            new_arg = mapped_type(arg)
            new_args.append(new_arg)
            param = parameters[idx]
            types_map[param] = new_arg 
        dct["_variable_map"] = types_map

        if new_args:
            kwargs["args"] = new_args

        annotations = dict(dct.get("__annotations__", {}))

        for annotation_name, annotation_type in annotations.items():
            if annotation_type.__class__ == typing.TypeVar:
                annotations[annotation_name] = types_map.get(annotation_type, annotation_type)
            else:    
                new_annotation = mapped_type(annotation_type)
                old_annotation_arguments = getattr(new_annotation, "__args__", []) or []
                new_annotation_arguments = []
                for old_annotation_argument in old_annotation_arguments:
                    new_annotation_argument = types_map.get(old_annotation_argument, old_annotation_argument)
                    new_annotation_arguments.append(new_annotation_argument)
                new_annotation_arguments = tuple(new_annotation_arguments)
                if new_annotation_arguments and new_annotation_arguments != old_annotation_arguments:
                    validators = hasattr(annotation_type, "validators") and annotation_type.validators or new_annotation.validators
                    new_annotation = new_annotation.__origin__[new_annotation_arguments](validators=validators)
                
                annotations[annotation_name] = new_annotation

        parents_annotations = {}
        for parent in parents:
            parent_annotations = getattr(parent, "__annotations__", {})
            parents_annotations.update(parent_annotations)

        parents_annotations.update(annotations)

        if parents_annotations:
            dct["__annotations__"] = parents_annotations

        obj = super(SchemaMeta, cls).__new__(cls, name, parents, dct, **kwargs)
        obj.from_json = SchemaType(obj)

        return obj

class Schema(Genericable, metaclass=SchemaMeta):
    is_schema = True

    def validate(self):
        errors = {}
        print(self.__annotations__)
        for (key, type) in self.__annotations__.items():
            val = getattr(self, key, None)
            try:
                if(getattr(val, "is_schema", False)):
                    val.validate()
                else:
                    type(val)
            except ValidationException as e:
                errors[key] = e.error()

        if errors:
            raise SchemaValidationException(errors)

    def to_json(self):
        json = {}
        for (key, type) in self.__annotations__.items():
            val = getattr(self, key, None)
            if getattr(val, "is_schema", False):
                json[key] = val.to_json()
            else:
                json[key] = val
        return json

__all__ = ['Any', 'Optional', 'Integer', 'Double', 'String', 'Boolean', 'List', 'Dictionary', 'Union', 'create_validated_type', 'mapped_type', 'Schema']
