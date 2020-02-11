#!/usr/bin/python3


import redis
import datetime



r = redis.Redis()
r.mset({"Russia": "Moscow", "Spain": "Madrid"})

print(r)
print(type(r))
print(dir(r))
print(r.ping())
print(r.get("Spain"))
print(r.get("Spain").decode("utf-8"))
print(r.ping())
print(r.info())

today = datetime.date.today().isoformat() # like a str(datetime.date.today())
nodes = {"a", "b", "c"}

r.sadd(today, *nodes)


print(r.keys())


#print(r.get("2020-02-05"))

print(r.smembers(today))

r1 = redis.Redis()
r1.set("Name", "Ivan")

#print(r1)
#if type(r) == type(r1):
#    print(True)

birthday = "01011990"
birthday = "01.01.1990"
#print(datetime(birthday))
current_date = datetime.datetime.strptime(birthday, '%d.%m.%Y').strftime('%Y%m%d')
#current_date = datetime.datetime.strftime('%Y%m%d')
#print(current_date)
r2 = redis.Redis()
dictionary = {"k1":"v1", "k2":"v2"}
r2.hmset("py_dict", dictionary)
#print(r2.hgetall("py_dict"))
#print(dir(r2))


#def get_interests(cid):
#    print("i:%s" % cid)

#get_interests("111")

