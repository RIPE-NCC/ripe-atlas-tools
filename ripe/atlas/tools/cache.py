import cPickle as pickle
import datetime
import dbm
import functools
import os


class LocalCache(object):

    def __init__(self):
        self._now = datetime.datetime.now()
        self._db = dbm.open(self._get_db_path(), "c")

    def __contains__(self, key):
        return key in self._db

    def __getitem__(self, key):
        if key in self._db:
            expires, value = pickle.loads(self._db[key])
            if not expires or expires > self._now:
                return value
        return None

    def __setitem__(self, key, value, expires=None):
        self._db[key] = pickle.dumps((expires, value))

    def __delitem__(self, key):
        if key not in self._db:
            raise KeyError
        del self._db[key]

    def keys(self):
        return self._db.keys()

    def get(self, key):
        return self.__getitem__(key)

    def set(self, key, value, expires=None):
        return self.__setitem__(
            key, value, self._now + datetime.timedelta(seconds=expires))

    def clear(self, key=None):
        if key:
            if key in self._db:
                del(self._db[key])
        else:
            for key in self._db.keys():
                del(self._db[key])

    @staticmethod
    def _get_db_path():
        if "HOME" in os.environ:
            return os.path.join(
                os.environ["HOME"], ".config", "ripe-atlas-tools", "cache.db")
        return os.path.join("/", "tmp", "cache.db")

cache = LocalCache()


class Memoiser(object):

    def __init__(self, function, cache_time):
        self._function = function
        self._cache_time = cache_time

    def __call__(self, *args, **kwargs):

        key = pickle.dumps([args, kwargs])
        value = cache[key]

        if value:
            return value

        value = self._function(*args, **kwargs)
        cache.set(key, value, self._cache_time)

        return value

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


def memoised(cache_time):
    def _wrap(function):
        return Memoiser(function, cache_time=cache_time)
    return _wrap
