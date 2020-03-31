#!/usr/bin/python3

import redis
import random
import json
import time
import logging
import redis
import json
import functools

logging.basicConfig(format=u'[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S',
                    level=logging.INFO
                    )


def retry(max_tries, error='TimeoutError'):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for n in range(1, max_tries + 1):
                try:
                    return func(*args, **kwargs)
                except error:
                    print(n)
                    if n == max_tries:
                        raise
        return wrapper
    return decorator


def load_redis(host='localhost', port=6379, db=0, socket_timeout=5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _r = redis.Redis(host=host, port=port, db=db, socket_timeout=socket_timeout)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class Store(object):
    # _r = None

    def __init__(self):
        # if not self._r:
        self._r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)



    @load_redis
    @retry(1)
    def cache_get(self, key):
        # while attempts > 0:
        #     try:
        val =  self._r.get(key)
        logging.info("key %s get from cache" % key)
        logging.info(self._r.keys())
        return json.loads(val) if val else None
            # except TimeoutError:
        #         attempts -= 1
        #         continue
        # return None

    @retry(4)
    def cache_set(self, key, value, ttl):
        # while attempts > 0:
        #     try:
        value = json.dumps(value)
        logging.info("key %s stored in cache" % key)
        self._r.set(key, value, ttl)
        return
        #     except TimeoutError:
        #         attempts -= 1
        #         continue
        # return None

    @retry(4)
    def get(self, key):
        # value = None
        # while attempts > 0:
        #     try:
        value = self.cache_get(key)
            # except TimeoutError:
            #     attempts -= 1
            #     continue
        if value is None:
            raise RuntimeError("Key %s is not set!" % key)
        return value

