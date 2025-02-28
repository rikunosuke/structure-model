from datetime import datetime
from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any, Type

from fastructure.exceptions import ConvertError

if TYPE_CHECKING:
    from fastructure.base import BaseModel


class Converter[ToType]:
    def __init__(self, value: Any, to_type: Type[ToType]):
        self._value = value
        self._to_type = to_type

    def _execute(self) -> ToType:
        from fastructure.base import BaseModel

        if self._to_type is str:
            return self.to_str(self._value)
        elif self._to_type is int:
            return self.to_int(self._value)
        elif self._to_type is float:
            return self.to_float(self._value)
        elif self._to_type is bool:
            return self.to_bool(self._value)
        elif self._to_type is datetime:
            return self.to_datetime(self._value)
        elif self._to_type is list:
            return self.to_list(self._value)
        elif self._to_type is tuple:
            return self.to_tuple(self._value)
        elif issubclass(self._to_type, BaseModel):
            return self.to_base_model(self._value)
        return self._value

    def execute(self) -> ToType:
        try:
            return self._execute()
        except ValueError as e:
            raise ConvertError(str(e))

    def to_base_model(self, value: Any) -> "BaseModel":
        if isinstance(value, self._to_type):
            # converter may run several times.
            # So check if may already values are converted.
            return value
        return (
            self._to_type.from_dict(value)
            if isinstance(value, dict)
            else self._to_type.from_list(value)
        )

    @singledispatchmethod
    def to_str(self, value) -> str:
        return str(value)

    @to_str.register
    def _(self, value: datetime) -> str:
        return value.isoformat()

    @to_str.register
    def _(self, value: bool) -> str:
        return "yes" if value else "no"

    @to_str.register
    def _(self, _: None) -> str:
        return ""

    @singledispatchmethod
    def to_int(self, value: int) -> int:
        return int(value)

    @to_int.register
    def _(self, value: datetime) -> int:
        return int(value.timestamp())

    @singledispatchmethod
    def to_float(self, value) -> float:
        return float(value)

    @to_float.register
    def _(self, value: datetime) -> float:
        return value.timestamp()

    @singledispatchmethod
    def to_bool(self, _) -> bool:
        return bool(self._value)

    @to_bool.register(str)
    def _(self, value: str) -> bool:
        return value.lower() == "yes"

    @singledispatchmethod
    def to_datetime(self, value) -> datetime:
        raise NotImplementedError(f"Cannot convert {type(value)} to datetime")

    @to_datetime.register(int)
    @to_datetime.register(float)
    def _(self, value: int | float) -> datetime:
        return datetime.fromtimestamp(value)

    @to_datetime.register(str)
    def _(self, value: str) -> datetime:
        return datetime.fromisoformat(value)

    @to_datetime.register(datetime)
    def _(self, value: datetime) -> datetime:
        return value

    def to_list(self, value) -> list:
        return list(value)

    def to_tuple(self, value) -> tuple:
        return tuple(value)

    def to_set(self, value) -> set:
        return set(value)
