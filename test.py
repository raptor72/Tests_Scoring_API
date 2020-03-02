import pytest
import api
import hashlib
from collections import namedtuple
from store import Store
import datetime

@pytest.fixture
def load_store():
    s = Store({"46a15aeae88d2123e8ac038602ee248f": 34, "1": 1, "2": "pets", "3": "heavy metall"})
#    s = Store({"": ""})
    return s


@pytest.fixture
def context():
    return {}

def get_response(request, headers, context, store):
    return api.method_handler({"body": request, "headers": headers}, context, store)

def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg).hexdigest()
    return request["token"]

def test_empty_request(load_store):
    _, code = get_response({}, {}, {}, load_store)
    assert api.INVALID_REQUEST == code

@pytest.mark.parametrize("arguments", [{"phone": "79175002040", "email": "stupnikov@otus.ru"},
                                       {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
                                       {"gender": 0, "birthday": "01.01.2000"},
                                       {"gender": 2, "birthday": "01.01.2000"},
                                       {"first_name": "a", "last_name": "b"},
                                       {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
                         "first_name": "a", "last_name": "b"},
                                       {"phone": 79175002040, "email": "stupnikov@otus.ru"},
])
def test_ok_score_request(arguments, load_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_store)
#    print(api.OK) # 200
#    print(arguments) # {'phone': '79175002040', 'email': 'stupnikov@otus.ru'}
#    print("response", response) #('response', {'score': 3.0})
#    print("context", context) # ('context', {'has': ['phone', 'email']})
    assert api.OK == code
    score = response.get("score")
#    print(score) # 3.0
    assert isinstance(score, int) or isinstance(score, float)
    assert score >= 0
    assert sorted(context["has"]) == sorted(arguments.keys())

@pytest.mark.parametrize("request", [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
])
def test_bad_auth(request, load_store):
    _, code = get_response(request, {}, {}, load_store)
    assert api.FORBIDDEN == code

@pytest.mark.parametrize("request", [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
])
def test_invalid_method_request(request, load_store):
    set_valid_auth(request)
    response, code = get_response(request, {}, {}, load_store)
    assert api.INVALID_REQUEST == code
    assert len(response)>0

@pytest.mark.parametrize("arguments", [
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "s", "last_name": 2},
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ])
def test_invalid_score_request(arguments, load_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, {}, load_store)
    assert api.INVALID_REQUEST == code
    assert len(response)>0

def test_ok_score_admin_request(load_store):
    arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
    request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, {}, load_store)
    assert api.OK == code
    score = response.get("score")
    assert score == 42

@pytest.mark.parametrize("arguments", [
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [1]},
    ])
def test_ok_interests_request(arguments, context, load_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_store)
    assert api.OK == code
    assert len(arguments["client_ids"]) == len(response)
    assert (isinstance(i, list) for i in response.values())
    assert ((isinstance(v, basestring) for i in v) for v in response.values())
#    print("response.values(): ", response.values()) #('response.values(): ', [1, 'pets', 'heavy metall'])
    assert context.get("nclients") == len(arguments["client_ids"])

@pytest.mark.parametrize("arguments", [
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ])
def test_invalid_interests_request(arguments, load_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, {}, load_store)
#    print(response)
    assert api.INVALID_REQUEST == code
    assert len(response)>0

@pytest.mark.parametrize("arguments", [
        {"client_ids": [4], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [4], "date": "19.07.2017"},
        {"client_ids": [4]},
    ])
def test_no_data_in_store_interests_request(arguments, context, load_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    with pytest.raises(Exception) as e:
        response, code = get_response(request, {}, context, load_store)
    assert 'is not set!' in str(e)
    assert 'RuntimeError' in str(e)

#@pytest.fixture
#def load_empty_store():
#    s = Store({"": ""})
#    return s

@pytest.fixture
def none_store():
    return None

#score_request working when store burn in atmosphere
@pytest.mark.parametrize("arguments", [{"phone": "79175002040", "email": "stupnikov@otus.ru"},
                                       {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
                                       {"gender": 0, "birthday": "01.01.2000"},
                                       {"gender": 2, "birthday": "01.01.2000"},
                                       {"first_name": "a", "last_name": "b"},
                                       {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
                         "first_name": "a", "last_name": "b"},
                                       {"phone": 79175002040, "email": "stupnikov@otus.ru"},
])
def test_none_store_score_request(arguments, none_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, none_store)
    assert api.OK == code
    score = response.get("score")
    assert isinstance(score, int) or isinstance(score, float)
    assert score >= 0
    assert sorted(context["has"]) == sorted(arguments.keys())

#interests_request not working when store burn
@pytest.mark.parametrize("arguments", [
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [1]},
    ])
def test_none_store_interests_request(arguments, context, none_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    with pytest.raises(Exception) as e:
        response, code = get_response(request, {}, context, none_store)
    assert 'AttributeError' in str(e)
    assert 'object has no attribute' in str(e)


@pytest.fixture
def load_warm_store():
    s = Store({'d41d8cd98f00b204e9800998ecf8427e': 3.0, 'efd4d906526f3a338d9eab83ea4c77e6': 2.0, 'a1301e1514843ca1973b941a88a58092': 0,
               'a1301e1514843ca1973b941a88a58092': 1.5, '187ef4436122d1cc2f40dc2b92f0eba0': 0.5, 'efd4d906526f3a338d9eab83ea4c77e6': 5.0,
               'd41d8cd98f00b204e9800998ecf8427e': 3.0})
    return s

@pytest.mark.parametrize("arguments", [{"phone": "79175002040", "email": "stupnikov@otus.ru"},
                                       {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
                                       {"gender": 0, "birthday": "01.01.2000"},
                                       {"gender": 2, "birthday": "01.01.2000"},
                                       {"first_name": "a", "last_name": "b"},
                                       {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
                         "first_name": "a", "last_name": "b"},
                                       {"phone": 79175002040, "email": "stupnikov@otus.ru"},
])
def test_warm_store_ok_score_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert api.OK == code
    score = response.get("score")
    assert isinstance(score, int) or isinstance(score, float)
    assert score >= 0
    assert sorted(context["has"]) == sorted(arguments.keys())


