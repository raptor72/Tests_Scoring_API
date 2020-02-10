#!/usr/bin/python3

import redis
import random

class Store:
    def __init__(self, volume):
        self.volume = volume
        self.r = redis.Redis()
        self.r.hmset("volume", volume)

    def cache_get(self, key):
        volume = self.r.hgetall("volume")
        hash = key.split("uid:")[1]
        try:
            if self.volume[hash]:
                print("get from cashe")
                return self.volume[hash]
        except KeyError:
            return None

    def cache_set(self, key, score, seconds):
        self.volume.update({key.split("uid:")[1]:score})
        print("stored in cache 2")
        print(self.volume)

    def get(self, key):
        pass



