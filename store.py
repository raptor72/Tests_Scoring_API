#!/usr/bin/python3

import redis
import random
import json
import time

class Store:
    def __init__(self, volume):
        self.volume = volume
        self.r = redis.Redis()
        self.r.hmset("volume", volume)

    def cache_get(self, key):
        volume = self.r.hgetall("volume")
        hash = key.split(":")[1]
        try:
            if self.volume[hash]:
                print("get from cashe")
                return self.volume[hash]
        except KeyError:
            return None

    def cache_set(self, key, score, seconds):
        self.volume.update({key.split(":")[1]:score})
        print("Key %s stored in cache" % key.split(":")[1])
        print(self.volume)

    def get(self, cid):
        time.sleep(0.1)
        value = self.cache_get(cid)
        if value is None:
            raise RuntimeError("Key %s is not set!" % cid.split(":")[1])
        return value


def get_interests(store, cid):
    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
    return str({cid: random.sample(interests, 2)})

def get_interests2(store, cid):
    r = """
    {
    "REPORT_SIZE": 25
    }
    """
    r = "{'key0': {'key1': 40}}"
    r = """{
    "1":{"1":1}
    }"""
#    r = store.get("i:%s" % cid)
    r = '{"i":["cars", "music"]}'
    return json.loads(r) if r else []


#print(get_interests2("", "")) # {'i': ['cars', 'music']}
