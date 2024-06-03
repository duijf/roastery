from roastery.importer import Cleanable


def test_cleanable() -> None:
    t()

    t(v="3", o="1", c="2", e="3")
    t(v="3", o="1", e="3")
    t(v="3", e="3")

    t(v="2", o="1", c="2")
    t(v="2", c="2")

    t(v="1", o="1")


def t(v=None, o=None, c=None, e=None) -> None:
    c = Cleanable(original=o, cleaned=c, edited=e)
    assert c.value == v
