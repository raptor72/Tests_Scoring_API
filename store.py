#!/usr/bin/python2.7

#import redis

import random

#def get(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None): # get_score()

class Store:
    def __init__(self, volume):
        self.volume = volume

#    def cache_get(self, key):
#        hash = key.split("uid:")[1]
#        if hash == "46a15aeae88d2123e8ac038602ee248f":
#            return 34

    def cache_get(self, key):
        hash = key.split("uid:")[1]
        if volume[hash]:
            return volume[hash]
        return None

    def cache_get(self, key):
#        volume = {"46a15aeae88d2123e8ac038602ee248f": 34}
        hash = key.split("uid:")[1]
        try:
            if self.volume[hash]:
                print("get from cashe")
                return self.volume[hash]
        except KeyError:
            return None

    def cache_set(self, key, score, seconds):
#        self.volume.update({key:score})
        self.__dict__['volume'].update({key:score})
        print("stored in cache")
        print(self.__dict__)
        print(self.volume)

    def get(self, key):
        pass


# function based store

#volume = {"46a15aeae88d2123e8ac038602ee248f": 34}
#def cache_get(key):
#    hash = key.split("uid:")[1]
#    if hash == "46a15aeae88d2123e8ac038602ee248f":
#        return 34

def cache_get(key):
    volume = {"46a15aeae88d2123e8ac038602ee248f": 34}
    hash = key.split("uid:")[1]
    try:
        if volume[hash]:
           print("get from cashe")
           return volume[hash]
    except KeyError:
        return None

#store.cache_set(key, score, 60 * 60)
def cache_set(key, score, seconds):
    volume.update({key: score})
    print("stored in cache")
    print(volume)

def get(key):
    pass


