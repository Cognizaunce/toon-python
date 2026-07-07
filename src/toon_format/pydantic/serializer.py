from __future__ import annotations

from pydantic import BaseModel

from toon_format import encode


class ToonPydanticModel(BaseModel):
    """
    Pydantic mixin that adds TOON superpowers.

    • schema_to_toon()        → TOON schema string (for LLM few-shot / system prompts)
    • model_dump_toon()       → Serialize this model instance to a TOON string
    """

    @classmethod
    def schema_to_toon(cls) -> str:
        """
        Convert the model's JSON schema into compact TOON format.
        Use this in your LLM prompt to save 40–60% tokens vs JSON schema.
        """
        schema = cls.model_json_schema()
        # Pydantic gives us full JSON schema
        return encode(schema)

    def model_dump_toon(self, **kwargs) -> str:
        """
        Serialize this model instance into a compact TOON string.

        Mirrors pydantic's ``model_dump_json()``. Extra keyword arguments are
        forwarded to ``model_dump()`` (e.g. ``exclude_none=True``).
        """
        data = self.model_dump(mode="json", **kwargs)
        return encode(data)
