import cPickle as pickle
import datetime
import dbm
import os


class LocalCache(object):

    def __init__(self):
        self._now = datetime.datetime.now()
        self._db = dbm.open(self._get_db_path(), "c")

    def __contains__(self, key):
        return key in self._db

    def __getitem__(self, key):
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

    @staticmethod
    def _get_db_path():
        if "HOME" in os.environ:
            return os.path.join(
                os.environ["HOME"], "config", "ripe-atlas-tools", "cache.db")
        return os.path.join("/", "tmp", "cache.db")

cache = LocalCache()
