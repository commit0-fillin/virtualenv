from __future__ import annotations
import logging
import os
from typing import ClassVar

class TypeData:

    def __init__(self, default_type, as_type) -> None:
        self.default_type = default_type
        self.as_type = as_type

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(base={self.default_type}, as={self.as_type})'

class BoolType(TypeData):
    BOOLEAN_STATES: ClassVar[dict[str, bool]] = {'1': True, 'yes': True, 'true': True, 'on': True, '0': False, 'no': False, 'false': False, 'off': False}

class NoneType(TypeData):
    pass

class ListType(TypeData):

    def _validate(self):
        """no op."""
        if not isinstance(self.as_type, (list, tuple)):
            raise ValueError(f"as_type must be a list or tuple, not {type(self.as_type)}")

    def split_values(self, value):
        """
        Split the provided value into a list.

        First this is done by newlines. If there were no newlines in the text,
        then we next try to split by comma.
        """
        if isinstance(value, (list, tuple)):
            return value
        if not isinstance(value, str):
            raise ValueError(f"Cannot split non-string value: {value}")
        
        # First, try splitting by newlines
        result = [v.strip() for v in value.splitlines() if v.strip()]
        
        # If no newlines were found, try splitting by comma
        if len(result) <= 1:
            result = [v.strip() for v in value.split(',') if v.strip()]
        
        return result

def convert(value, as_type, source):
    """Convert the value as a given type where the value comes from the given source."""
    if as_type is None:
        return value

    if isinstance(as_type, TypeData):
        type_data = as_type
    else:
        type_data = _CONVERT.get(as_type, TypeData)(as_type, as_type)

    if isinstance(value, str):
        value = value.strip()

    if isinstance(type_data, BoolType):
        if isinstance(value, bool):
            return value
        if value.lower() not in BoolType.BOOLEAN_STATES:
            raise ValueError(f"Cannot convert {value} to bool")
        return BoolType.BOOLEAN_STATES[value.lower()]

    if isinstance(type_data, NoneType):
        if value.lower() in ('none', ''):
            return None
        raise ValueError(f"Cannot convert {value} to NoneType")

    if isinstance(type_data, ListType):
        return type_data.split_values(value)

    try:
        return type_data.as_type(value)
    except ValueError as exc:
        raise ValueError(f"Cannot convert {value} to {type_data.as_type.__name__} for {source}: {exc}")
_CONVERT = {bool: BoolType, type(None): NoneType, list: ListType}
__all__ = ['convert', 'get_type']
