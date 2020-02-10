#!/usr/bin/python

import hashlib
import json
#from store import Store # oop
#from store import * # func
import datetime



def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):

    key_parts = [
        first_name or "",
        last_name or "",
        phone or "",
#        birthday.strftime("%Y%m%d") if birthday is not None else "",
        datetime.datetime.strptime(birthday, '%d.%m.%Y').strftime('%Y%m%d') if birthday is not None else "",
]
    key = "uid:" + hashlib.md5("".join(key_parts)).hexdigest()
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
#    print(key_parts)
#    return key

#    store = Store({"46a15aeae88d2123e8ac038602ee248f": 34}) # oop
    score = store.cache_get(key) or 0 # oop
#    score = cache_get(key) or 0 # func

    if score:
        return score
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
#    cache_set(key, score, 60 * 60)
    return score

"""
def get_interests(store, cid):
    r = store.get("i:%s" % cid)
    return json.loads(r) if r else []
"""

#get_score(None, "79177002040", "ipetrov@gmail.com", "19900101", 1, "Ivan", "Petrov")



