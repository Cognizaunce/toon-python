from typing import Optional

from toon_format.pydantic import ToonPydanticModel


class User(ToonPydanticModel):
    name: str
    age: int
    email: Optional[str] = None


def test_schema_to_toon():
    schema = User.schema_to_toon()
    assert "name:" in schema
    assert "age:" in schema
    assert "email:" in schema
    assert "type: object" in schema


def test_model_dump_toon():
    user = User(name="Ansar", age=25)
    toon = user.model_dump_toon()
    assert "name: Ansar" in toon
    assert "age: 25" in toon
