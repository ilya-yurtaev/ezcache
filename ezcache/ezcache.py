# coding: utf-8

from __future__ import unicode_literals

import inspect

from hashlib import md5

try:
    from typing import *
except ImportError:
    pass

from functools import wraps, partial


class DummyBackend(dict):
    # type: Dict[Hashable, Any]
    """
    Backend instance must have implemented following methods:
    `get`, `set`, `clear`, `delete`, `delete_pattern` (optional)
    """

    def set(self, key, value, *args, **kwargs):
        super(DummyBackend, self).setdefault(key, value)

    def delete(self, key):
        if key in self:
            del self[key]


DEFAULT_BACKEND = DummyBackend()


def get_func_defaults(f):
    # type: (Callable[[Any], Any]) -> Dict[str, Any]
    try:
        # py3
        return {
            k: v.default
            for k, v in inspect.signature(f).parameters.items()
            if v.default is not inspect._empty
        }
    except AttributeError:
        # py2
        sp = inspect.getargspec(f)
        return dict(zip(reversed(sp.args or []), reversed(sp.defaults or [])))


def md5_key_builder(*args, **kwargs):
    # type: (*Any, **Dict[Hashable, Any]) -> str
    return md5(
        "".join(
            list(map(str, args))
            + [
                "{}{}".format(k, v)
                for k, v in sorted(kwargs.items(), key=lambda x: x[0])
            ]
        ).encode("utf-8")
    ).hexdigest()


def qualname(f):
    # type: (Callable[[Any], Any]) -> str
    return ".".join(
        [
            f.__module__,
            getattr(f, "__qualname__", None)
            or ".".join(
                [
                    x
                    for x in [
                        getattr(getattr(f, "im_class", None), "__name__", None),
                        f.__name__,
                    ]
                    if x
                ]
            ),
        ]
    )


def ezcache(backend=DEFAULT_BACKEND, key_builder=md5_key_builder, timeout=None):
    # type: (Type, Callable[[Any], str], int) -> Any

    def decorator(f):
        # type: (Callable[[Any], Any]) -> Callable[[Any], Any]
        defaults = get_func_defaults(f)
        _qualname = qualname(f)

        def _key_builder(*args, **kwargs):
            _dflts = defaults.copy()
            _dflts.update(kwargs)
            return key_builder(_qualname, *args, **_dflts)

        @wraps(f)
        def wrapper(*args, **kwargs):
            # type: (*Any, **Any) -> Any
            key = _key_builder(*args, **kwargs)
            res = backend.get(key)

            if not res:
                res = f(*args, **kwargs)
                backend.set(key, res, timeout=timeout)

            return res

        def invalidate(*args, **kwargs):
            # type: (*Any, **Any) -> None
            backend.delete(_key_builder(*args, **kwargs))

        setattr(wrapper, "get_cache_key", _key_builder)
        setattr(wrapper, "invalidate", invalidate)

        return wrapper

    return decorator


def mk_cache(*args, **kwargs):
    # just not to make `import partial`
    return partial(ezcache, *args, **kwargs)
