import os
import sys
import time
import redis
import pytest
import logging
import hashlib
import datetime

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(PROJECT_ROOT)

import api
from store import Store
from scoring  import get_score, get_interests

@pytest.fixture
def load_store():
    s = Store()
    return s


@pytest.fixture
def context():
    return {}


@pytest.fixture
def none_store():
    return None


@pytest.fixture
def load_warm_store():
    s = Store()
    ttl = 20
    for k, v in (('d41d8cd98f00b204e9800998ecf8427e', 3.0), ('efd4d906526f3a338d9eab83ea4c77e6', 2.0), ('a1301e1514843ca1973b941a88a58092', 0), ('a1301e1514843ca1973b941a88a58092', 1.5),
                ('187ef4436122d1cc2f40dc2b92f0eba0', 0.5), ('efd4d906526f3a338d9eab83ea4c77e6', 5.0), ('d41d8cd98f00b204e9800998ecf8427e', 3.0), ("1", 1), ("2", "2"), ("3", "3"), ("-1", "-1")):
        s.cache_set(k, v, ttl)
    return s


@pytest.fixture
def storage_redis_offline_mock(monkeypatch):
    def mock_get_and_set_to_redis(*args, **kwargs):
        raise redis.exceptions.ConnectionError
    monkeypatch.setattr(redis.Redis, 'get', mock_get_and_set_to_redis)


@pytest.fixture
def mock_set_with_success_reconnect(monkeypatch):
    ones_raise_completed = False
    global ones_raise_completed
    def mock_set_to_redis(*args, **kwargs):
        global ones_raise_completed
        if ones_raise_completed:
            monkeypatch.undo()
            return redis.Redis.set(*args, **kwargs)
        ones_raise_completed = True
        raise redis.exceptions.ConnectionError
    monkeypatch.setattr(redis.Redis, 'set', mock_set_to_redis)


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


@pytest.mark.parametrize(
    "arguments",
    [{"phone": "79175002040", "email": "stupnikov@otus.ru"},
    {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
    {"gender": 0, "birthday": "01.01.2000"},
    {"gender": 2, "birthday": "01.01.2000"},
    {"first_name": "a", "last_name": "b"},
    {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
    "first_name": "a", "last_name": "b"},
    {"phone": 79175002040, "email": "stupnikov@otus.ru"}]
)
def test_ok_score_request(arguments, load_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_store)
    assert api.OK == code
    score = response.get("score")
    assert isinstance(score, int) or isinstance(score, float)
    assert score >= 0
    assert sorted(context["has"]) == sorted(arguments.keys())


@pytest.mark.parametrize(
    "request",
    [{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
    {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
    {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},]
)
def test_bad_auth(request, load_store):
    _, code = get_response(request, {}, {}, load_store)
    assert api.FORBIDDEN == code


@pytest.mark.parametrize(
    "request",
    [{"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
    {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
    {"account": "horns&hoofs", "method": "online_score", "arguments": {}}]
)
def test_invalid_method_request(request, load_store):
    set_valid_auth(request)
    response, code = get_response(request, {}, {}, load_store)
    assert api.INVALID_REQUEST == code
    assert len(response)>0


@pytest.mark.parametrize(
    "arguments",
    [{},
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
    {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2}]
)
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


@pytest.mark.parametrize(
    "arguments",
    [{},
    {"date": "20.07.2017"},
    {"client_ids": [], "date": "20.07.2017"},
    {"client_ids": {1: 2}, "date": "20.07.2017"},
    {"client_ids": ["1", "2"], "date": "20.07.2017"},
    {"client_ids": [1, 2], "date": "XXX"}]
)
def test_invalid_interests_request(arguments, load_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, {}, load_store)
    assert api.INVALID_REQUEST == code
    assert len(response)>0


@pytest.mark.parametrize(
    "arguments",
    [{"client_ids": [4], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
    {"client_ids": [4], "date": "19.07.2017"},
    {"client_ids": [4]}]
)
def test_no_data_in_store_interests_request(arguments, context, load_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    with pytest.raises(Exception) as e:
        response, code = get_response(request, {}, context, load_store)
    assert 'is not set!' in str(e)
    assert 'RuntimeError' in str(e)


#score_request working when store burn in atmosphere
@pytest.mark.parametrize(
    "arguments",
    [{"phone": "79175002040", "email": "stupnikov@otus.ru"},
    {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
    {"gender": 0, "birthday": "01.01.2000"},
    {"gender": 2, "birthday": "01.01.2000"},
    {"first_name": "a", "last_name": "b"},
    {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
    "first_name": "a", "last_name": "b"},
    {"phone": 79175002040, "email": "stupnikov@otus.ru"}]
)
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
@pytest.mark.parametrize(
    "arguments",
    [{"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
    {"client_ids": [1, 2], "date": "19.07.2017"},
    {"client_ids": [1]}]
)
def test_none_store_interests_request(arguments, context, none_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    with pytest.raises(Exception) as e:
        response, code = get_response(request, {}, context, none_store)
    assert 'AttributeError' in str(e)
    assert 'object has no attribute' in str(e)


@pytest.mark.parametrize(
    "arguments",
    [{"phone": "79175002040", "email": "stupnikov@otus.ru"},
    {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
    {"gender": 0, "birthday": "01.01.2000"},
    {"gender": 2, "birthday": "01.01.2000"},
    {"first_name": "a", "last_name": "b"},
    {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
    "first_name": "a", "last_name": "b"},
    {"phone": 79175002040, "email": "stupnikov@otus.ru"}]
)
def test_warm_store_ok_score_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert api.OK == code
    score = response.get("score")
    assert isinstance(score, int) or isinstance(score, float)
    assert score >= 0
    assert sorted(context["has"]) == sorted(arguments.keys())


@pytest.mark.parametrize(
    "arguments",
    [{"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
    {"client_ids": [1, 2], "date": "19.07.2017"},
    {"client_ids": [1]}]
)
def test_ok_interests_request(arguments, context, load_warm_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert api.OK == code
    assert len(arguments["client_ids"]) == len(response)
    assert (isinstance(i, list) for i in response.values())
    assert ((isinstance(v, basestring) for i in v) for v in response.values())
    assert context.get("nclients") == len(arguments["client_ids"])


@pytest.mark.parametrize(
    "arguments",
    [[3.0, {"phone": 79175002040, "email": "ivanov@mail.com"}],
    [2.0, {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"}],
    [1.5, {"gender": 0, "birthday": "01.01.2000"}],
    [1.5, {"gender": 2, "birthday": "01.01.2000"}],
    [0.5, {"first_name": "a", "last_name": "b"}],
    [2.0, {"phone": 79175002040, "email": "ivanov@mail.com", "gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"}],
    [3.0, {"phone": 79175002040, "email": "ivanov@mail.com"}]]
)
def test_scoring_request(arguments, load_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments[1]}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_store)
    assert api.OK == code
    score = response.get("score")
    assert score >= 0
    assert arguments[0] == score


@pytest.mark.parametrize(
    "arguments",
    [{"email": 1, "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"email": ["stupnikov@otus.ru"], "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"email": "stupnikovotus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"email": {"stupnikov": "otus.ru"}, "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"email": 1.0, "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"email": None, "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"email": ("stupnikov", "@otus.ru"), "gender": 1, "birthday": "01.01.2000", "first_name": "a"}]
)
def test_invalid_email_field_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field email (type EmailField) invalid' in response


@pytest.mark.parametrize(
    "arguments",
    [{"phone": "7917500204", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": "89175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": "+79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": "791750020400", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"}]
)
def test_invalid_phone_number_field_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field phone (type PhoneField) invalid: Phone number should be 7**********' in response


@pytest.mark.parametrize(
    "arguments",
    [{"phone": 79175002040.0, "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": [79175002040], "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": 0+79175002040j, "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": {"number": "79175002040"}, "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": None, "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"}]
)
def test_invalid_phone_type_field_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field phone (type PhoneField) invalid: Phone number must be number or string' in response


@pytest.mark.parametrize(
    "arguments",
    [{"birthday": "01-01-2000", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"},
    {"birthday": "2000.01.01", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"},
    {"birthday": "01012000", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"},
    {"birthday": "01.13.2000", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"},
    {"birthday": "31.02.2000", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"}]
)
def test_invalid_birthday_type_field_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field birthday (type BirthDayField) invalid: Incorect date format, should be DD.MM.YYYY' in response


@pytest.mark.parametrize(
    "arguments",
    [{"gender": -1, "phone": 79175002040, "email": "stupnikov@otus.ru", "birthday": "01.01.2000", "first_name": "a"},
    {"gender": 3, "phone": 79175002040, "email": "stupnikov@otus.ru", "birthday": "01.01.2000", "first_name": "a"},
    {"gender": "1", "phone": 79175002040, "email": "stupnikov@otus.ru", "birthday": "01.01.2000", "first_name": "a"}]
)
def test_invalid_gender_type_field_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field gender (type GenderField) invalid: Gender must be equal to 0, 1 or 2' in response


@pytest.mark.parametrize(
    "arguments",
    [{"client_ids": [1, "2", 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
    {"client_ids": [1, -1], "date": "19.07.2017"}]
)
def test_invalid_clients_ids_field_request(arguments, context, load_warm_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Client IDs should be list or positive integers' in response


@pytest.mark.parametrize("arguments", [[], 1, 1.0, "string"])
def test_invalid_arguments_field_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field arguments (type ArgumentsField) invalid: This field must be a dict' in response


@pytest.mark.parametrize(
    "arguments",
    [{"first_name": ["a"], "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "last_name": "b"},
    {"first_name": 1, "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "last_name": "b"},
    {"first_name": 1.0, "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "last_name": "b"},
    {"first_name": {"k":"v"}, "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "last_name": "b"}]
)
def test_invalid_char_field_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert '(type CharField) invalid: This field must be a string' in response


@pytest.mark.parametrize(
    "arguments",
    [{"phone": 79175002040, "gender": 1, "first_name": "a"},
    {"email": "stupnikov@otus.ru", "birthday": "01.01.2000", "first_name": "a"},
    {"phone": 79175002040,},
    {"gender": 1, "first_name": "a"},
    {"email": "stupnikov@otus.ru", "last_name": "b"},
    {"phone": 79175002040, "birthday": "01.01.2000", "last_name": "b"},
    {"email": "stupnikov@otus.ru", "gender": 1}]
)
def test_invalid_required_pairs_field_request(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'At least one of the pairs should be defined: first/last name, email/phone, birthday/gender' in response


@pytest.mark.parametrize(
    "full_dict",
    [{"account": "horns&hoofs", "login": "h&f", "arguments": {"phone": 79175002040, "gender": 1, "first_name": "a"}},
    {"account": "horns&hoofs", "method": "online_score", "arguments": {"phone": 79175002040, "gender": 1, "first_name": "a"}},
    {"account": "horns&hoofs", "login": "h&f", "method": "online_score"}]
)
def test_invalid_required_field_types_request(full_dict, load_warm_store, context):
    request = full_dict
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Required field' in response
    assert 'is not defined!' in response


def test_set_key(load_store):
    load_store.cache_set('key1', 'value1', 1)
    assert load_store.get('key1')


def test_cleanup_cache(load_store):
    load_store.cache_set('key3', 'value3', 1)
    time.sleep(2)
    assert load_store.cache_get('key3') is None


def test_get_command_reconnect_if_connection_lost(load_store, storage_redis_offline_mock):
    with pytest.raises(redis.exceptions.ConnectionError):
        load_store.get("123")


def test_cached_get_reconnect_if_connection_lost(load_store, storage_redis_offline_mock):
    assert load_store.cache_set("123", "123", 30) is None


def test_get_score_if_redis_offline(load_store, storage_redis_offline_mock):
    score = get_score(load_store, phone="79175002040", email="stupnikov@otus.ru")
    assert score == 3.0


def test_get_interests_if_redis_offline(load_store, storage_redis_offline_mock):
    with pytest.raises(redis.exceptions.ConnectionError):
        get_interests(load_store, 1)


def test_cached_get_reconnect_if_reconnection_success(load_store, mock_set_with_success_reconnect, caplog):
    caplog.set_level(logging.INFO)
    load_store.cache_set("123", "123", 30)
    assert any("connection lost" in record.message for record in caplog.records)
    assert load_store.get("123") == "123"
