#!/usr/bin/python3

import redis
import random
import json
import time


import redis
import json

class Store(object):
    _r = None

    def __init__(self):
        if not self._r:
            self._r = redis.Redis()

    def cache_get(self, key):
        val =  self._r.get(key)
        print("key %s get from cache" % key)
        print(self._r.keys())
        return json.loads(val) if val else None

    def cache_set(self, key, value, ttl):
        value = json.dumps(value)
        print("key %s stored in cache" % key)
        self._r.set(key, value, ttl)

    def get(self, key):
        value = self.cache_get(key)
        if value is None:
            raise RuntimeError("Key %s is not set!" % key)
        return value