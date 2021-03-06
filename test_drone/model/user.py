"""用户自定义的orm映射.

注意使用装饰器register将要创建的表注册到Tables.
"""
from peewee import (
    CharField,
    IntegerField
)
from ._base import (
    BaseModel,
    register
)


@register
class User(BaseModel):
    age = IntegerField()
    name = CharField()

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age
        }


__all__ = ["User"]
