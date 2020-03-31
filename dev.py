#!/usr/bin/python3

from time import sleep
import functools

def attemper(attempts, timeout):
#    print(attempts)
    def decorator(func):
#        print(attempts)
        def wrapper(*args, **kwargs):
            print(attempts)
#            while attempts > 0:
#                try:
            if attempts > 0:
                try:
                    return func(*args, **kwargs)

                except PermissionError:
                    print(attempts)
                    sleep(timeout)
                    attempts = attempts - 1
                    #continue
#                    pass
            else:
#            attempts -= 1
#                    pass
#                    print(attempts)
#                    pass
                return None
        return wrapper
    return decorator


def retry(max_tries, error=PermissionError):
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


#@decorator_maker("Tesla", "SpaceX")
#@attemper(5, 1)
@retry(5)
def opener(file):
    f = open(file, 'r')
    for line in f:
        print(line)

opener('1.txt')
