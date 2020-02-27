import pytest
import api
import hashlib
from collections import namedtuple
from store import Store


def get_response(request, headers, context, store):
    return api.method_handler({"body": request, "headers": headers}, context, store)


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg).hexdigest()
    return request["token"]



@pytest.mark.parametrize("arguments", [{"phone": "79175002040", "email": "stupnikov@otus.ru"},
                                       {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
                                       {"gender": 0, "birthday": "01.01.2000"},
                                       {"gender": 2, "birthday": "01.01.2000"},
                                       {"first_name": "a", "last_name": "b"},
                                       {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
                         "first_name": "a", "last_name": "b"},
                                       {"phone": 79175002040, "email": "stupnikov@otus.ru"},
])
def test_ok_score_request(arguments):
    context = {}
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    s = Store({"46a15aeae88d2123e8ac038602ee248f": 34, "1": 1, "2": "pets"})
    response, code = get_response(request, {}, context, s)
#    print(api.OK) # 200
#    print(code) # 200
#    print(arguments) # {'phone': '79175002040', 'email': 'stupnikov@otus.ru'}
#    print("response", response) #('response', {'score': 3.0})
#    print("context", context) # ('context', {'has': ['phone', 'email']})
    assert api.OK == code
    score = response.get("score")
#    print(score) # 3.0
    assert isinstance(score, int) or isinstance(score, float)
    assert score >= 0
    assert sorted(context["has"]) == sorted(arguments.keys())


def test_empty_request():
    s = Store({"46a15aeae88d2123e8ac038602ee248f": 34, "1": 1, "2": "pets"})
    _, code = get_response({}, {}, {}, None)
    assert api.INVALID_REQUEST == code






