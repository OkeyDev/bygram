import json

import pytest

from bygram.core import serializer
from bygram.core.types import DeserializedObject
from bygram.types import raw
from bygram.types.base import ObjectBase, TlObject


@pytest.mark.parametrize(
    "obj,result",
    [
        (raw.TestCallEmpty(), {"@type": "testCallEmpty"}),
        (raw.TestSquareInt(1), {"x": 1, "@type": "testSquareInt"}),
    ],
)
def test_serialize(obj: ObjectBase, result: dict):
    assert serializer.serialize_object(obj) == json.dumps(result).encode()


@pytest.mark.parametrize(
    "obj,result",
    [
        (b'{"@type": "testCallEmpty"}', DeserializedObject(raw.TestCallEmpty())),
        (
            b'{"@type": "testCallEmpty", "@client_id": 1, "@extra": 1}',
            DeserializedObject(raw.TestCallEmpty(), 1, 1),
        ),
    ],
)
def test_deserialize(obj: bytes, result: TlObject):
    assert serializer.deserialize_object(obj) == result
