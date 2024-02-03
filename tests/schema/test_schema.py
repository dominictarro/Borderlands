import pytest

from borderlands.schema.schema import Field, Filter, Schema


class TestSchema:

    @pytest.mark.parametrize(
        "cls, fields",
        [
            (
                type(
                    "TestSchema",
                    (Schema,),
                    {
                        "id_": Field(int),
                        "name": Field(str),
                        "description": Field(str),
                        "non-field": "non-field",
                    },
                ),
                ["id_", "name", "description"],
            )
        ],
    )
    def test_init_subclass(self, cls: Schema, fields: list[str]):
        """Tests the `__init_subclass__` method."""
        assert list(cls.__fields__) == fields

    def test_iter_no_filter(self):
        cls = type(
            "TestSchema",
            (Schema,),
            {
                "id_": Field(int),
                "name": Field(str),
                "description": Field(str),
                "non-field": "non-field",
            },
        )
        assert list(cls.iter()) == list(cls.__fields__.values())

    def test_iter_include_filter(self):
        cls = type(
            "TestSchema",
            (Schema,),
            {
                "id_": Field(int, tags=["1"]),
                "name": Field(str, tags=["2"]),
                "description": Field(str, tags=["2", "3"]),
                "non-field": "non-field",
            },
        )
        assert list(cls.iter(include=["1"])) == [cls.id_]

    def test_iter_exclude_filter(self):
        cls = type(
            "TestSchema",
            (Schema,),
            {
                "id_": Field(int, tags=["1"]),
                "name": Field(str, tags=["2"]),
                "description": Field(str, tags=["2", "3"]),
                "non-field": "non-field",
            },
        )
        assert list(cls.iter(exclude=["1"])) == [cls.name, cls.description]

    def test_iter_include_and_exclude_filter(self):
        cls = type(
            "TestSchema",
            (Schema,),
            {
                "id_": Field(int, tags=["1", "3"]),
                "name": Field(str, tags=["2"]),
                "description": Field(str, tags=["2", "3"]),
                "non-field": "non-field",
            },
        )
        assert list(cls.iter(include=["3"], exclude=["2"])) == [cls.id_]

    def test_iter_include_and_exclude_filter_with_no_matches(self):
        cls = type(
            "TestSchema",
            (Schema,),
            {
                "id_": Field(int, tags=["1", "3"]),
                "name": Field(str, tags=["2"]),
                "description": Field(str, tags=["2", "3"]),
                "non-field": "non-field",
            },
        )
        assert list(cls.iter(include=["3"], exclude=["1", "2"])) == []


class TestFilter:

    def test_has_tag(self):
        f = Field(int, tags=["1", "2"])
        assert Filter.has_tag(f, "1")
        assert not Filter.has_tag(f, "3")

    def test_is_datatype(self):
        f = Field(int)
        assert Filter.is_datatype(f, int)
        assert not Filter.is_datatype(f, str)

    def test_is_included_tag_only(self):
        f = Field(int, tags=["1", "2"])
        fltr = Filter(include=["1"])
        assert fltr.is_included(f)

    def test_is_included_datatype_only(self):
        f = Field(int)
        fltr = Filter(include=[int])
        assert fltr.is_included(f)

    def test_is_included_tag_and_datatype(self):
        f = Field(int, tags=["1", "2"])
        fltr = Filter(include=["1", int])
        assert fltr.is_included(f)

    def test_is_included_tag_only_with_exclude(self):
        f = Field(int, tags=["1", "2"])
        fltr = Filter(include=["1"], exclude=["2"])
        assert not fltr.is_included(f)
