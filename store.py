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

    def cache_get(self, key, attempts=1):
        while attempts > 0:
            try:
                val =  self._r.get(key)
                print("key %s get from cache" % key)
                print(self._r.keys())
                return json.loads(val) if val else None
            except TimeoutError:
                attempts -= 1
                continue
        return None

    def cache_set(self, key, value, ttl, attempts=4):
        while attempts > 0:
            try:
                value = json.dumps(value)
                print("key %s stored in cache" % key)
                self._r.set(key, value, ttl)
                return
            except TimeoutError:
                attempts -= 1
                continue
        return None


    def get(self, key, attempts=4):
        value = None
        while attempts > 0:
            try:
                value = self.cache_get(key)
            except TimeoutError:
                attempts -= 1
                continue
            if value is None:
                raise RuntimeError("Key %s is not set!" % key)
            return value
