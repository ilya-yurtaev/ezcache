# coding: utf-8

from __future__ import unicode_literals

import pytest

from ezcache import DummyBackend, ezcache, md5_key_builder, mk_cache


def test_md5_key_builder():
    class Wtf(object):
        pass

    args = ("method_name", 1, 2, True, [3, 4, 5], ("a", 1), Wtf())
    kwargs = {"timeout": None, "wtf": Wtf(), "foo": "bar", "x": 1}

    assert md5_key_builder(*args, **kwargs) == md5_key_builder(*args, **kwargs)
    assert md5_key_builder(*args) == md5_key_builder(*args)
    assert md5_key_builder() != md5_key_builder(*args)
    assert md5_key_builder(**kwargs) != md5_key_builder(*args)
    assert md5_key_builder() == md5_key_builder()


def test_cached():
    backend = DummyBackend()
    cached = mk_cache(backend)
    counter = {"value": 0}

    @cached(timeout=60 * 60)
    def func(*args, **kwargs):
        counter["value"] += 1
        return "func value"

    func()

    assert counter["value"] == 1
    assert func.get_cache_key() in backend

    func()

    assert counter["value"] == 1

    func.invalidate()

    assert func.get_cache_key() not in backend

    func()

    assert counter["value"] == 2
    assert backend.get(func.get_cache_key()) == func()
    assert counter["value"] == 2


def test_fully_applied():
    backend = DummyBackend()
    cached60 = ezcache(backend, timeout=60 * 60)

    @cached60
    def func(*args, **kwargs):
        return "hello"

    assert func.get_cache_key() not in backend

    func()

    assert func.get_cache_key() in backend


def test_template():
    def tcached(tmpl, **kwargs):
        return ezcache(
            backend=DummyBackend(),
            key_builder=lambda *a, **k: tmpl.format(*a, **k),
        )

    @tcached("my_template_{1}_{kwarg}", timeout=60 * 60)
    def func(*args, **kwargs):
        return True

    assert func.get_cache_key(None, kwarg=None) == "my_template_None_None"

    with pytest.raises(IndexError):
        func.get_cache_key()

    with pytest.raises(KeyError):
        func.get_cache_key(None)


def test_lambda():
    backend = DummyBackend()

    def lcached(lmbd, **kwargs):
        return ezcache(backend=backend, key_builder=lmbd, **kwargs)

    @lcached(
        lambda *a, **kw: "{}{kwarg}".format(a[1], kwarg=kw.get("kwarg", "")),
        timeout=60 * 60,
    )
    def func(arg0, arg1, kwarg="lol", foo="bar"):
        return 42

    func(1, 2)

    assert "1lol" in backend
