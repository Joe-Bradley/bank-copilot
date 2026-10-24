from pydantic import BaseModel


class Lili(BaseModel):
    name: str
    age: int


def test_basemodel_creates_object_and_dumps_dict():
    person = Lili(name="lili", age=18)

    assert person.name == "lili"
    assert person.age == 18
    assert person.model_dump() == {
        "name": "lili",
        "age": 18,
    }
