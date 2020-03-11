import os
import sys
import pytest
import hashlib
import datetime

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(PROJECT_ROOT)

import api
from store import Store


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


def get_response(request, headers, context, store):
    return api.method_handler({"body": request, "headers": headers}, context, store)


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg).hexdigest()
    return request["token"]


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
def test_email_field(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field email (type EmailField) invalid' in response


@pytest.mark.parametrize("arguments", ["stupnikovotus.ru", "stupnikov", "otus.ru"])
def test_api_email_field(arguments, load_warm_store, context):
    field = api.EmailField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'Invalid email address' == str(e.value)
    assert 'ValueError' in str(e)


@pytest.mark.parametrize(
    "arguments",
    [{"phone": "7917500204", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": "89175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": "+79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": "791750020400", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"}]
)
def test_phone_number_field(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field phone (type PhoneField) invalid: Phone number should be 7**********' in response


@pytest.mark.parametrize("arguments", ["7917500204", "89175002040", "+79175002040", "791750020400"])
def test_api_phone_number_field(arguments, load_warm_store, context):
    field = api.PhoneField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'Phone number should be 7**********' == str(e.value)
    assert 'ValueError' in str(e)


@pytest.mark.parametrize(
    "arguments",
    [{"phone": 79175002040.0, "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": [79175002040], "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": 0+79175002040j, "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": {"number": "79175002040"}, "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"},
    {"phone": None, "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": "a"}]
)
def test_phone_type_field(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field phone (type PhoneField) invalid: Phone number must be number or string' in response


@pytest.mark.parametrize("arguments", [79175002040.0, [79175002040], 0+79175002040j, {"number": "79175002040"}, None])
def test_api_phone_type_field(arguments, load_warm_store, context):
    field = api.PhoneField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'Phone number must be number or string' == str(e.value)
    assert 'ValueError' in str(e)


@pytest.mark.parametrize(
    "arguments",
    [{"birthday": "01-01-2000", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"},
    {"birthday": "2000.01.01", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"},
    {"birthday": "01012000", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"},
    {"birthday": "01.13.2000", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"},
    {"birthday": "31.02.2000", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"}]
)
def test_birthday_type_field(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field birthday (type BirthDayField) invalid: Incorect date format, should be DD.MM.YYYY' in response


@pytest.mark.parametrize("arguments", ["01-01-2000", "2000.01.01", "01012000", "01.13.2000", "31.02.2000"])
def test_api_birthday_type_field(arguments, load_warm_store, context):
    field = api.BirthDayField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'Incorect date format, should be DD.MM.YYYY' == str(e.value)
    assert 'ValueError' in str(e)


@pytest.mark.parametrize("arguments", [{"birthday": "01.01.1900", "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "first_name": "a"}])
def test_too_old_birthday_type_field(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field birthday (type BirthDayField) invalid: Incorrect birth day' in response


@pytest.mark.parametrize("arguments", ["01.01.1900", "31.12.1899"])
def test_api_too_old_birthday_type_field(arguments, load_warm_store, context):
    field = api.BirthDayField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'Incorrect birth day' == str(e.value)
    assert 'ValueError' in str(e)


@pytest.mark.parametrize(
    "arguments", 
    [{"gender": -1, "phone": 79175002040, "email": "stupnikov@otus.ru", "birthday": "01.01.2000", "first_name": "a"},
    {"gender": 3, "phone": 79175002040, "email": "stupnikov@otus.ru", "birthday": "01.01.2000", "first_name": "a"},
    {"gender": "1", "phone": 79175002040, "email": "stupnikov@otus.ru", "birthday": "01.01.2000", "first_name": "a"}]
)
def test_gender_type_field(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field gender (type GenderField) invalid: Gender must be equal to 0, 1 or 2' in response


@pytest.mark.parametrize("arguments", [-1, 3, "1"])
def test_api_gender_type_field(arguments, load_warm_store, context):
    field = api.GenderField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'Gender must be equal to 0, 1 or 2' == str(e.value)
    assert 'ValueError' in str(e)


@pytest.mark.parametrize(
    "arguments",
    [{"client_ids": [1, "2", 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
    {"client_ids": [1, -1], "date": "19.07.2017"}]
)
def test_clients_ids_field(arguments, context, load_warm_store):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Client IDs should be list or positive integers' in response


@pytest.mark.parametrize("arguments", [["2"], [-1]])
def test_api_clients_id_field(arguments, load_warm_store, context):
    field = api.ClientIDsField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'Client IDs should be list or positive integers' in str(e)


@pytest.mark.parametrize("arguments", [[], 1, 1.0, "string"])
def test_arguments_field(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Field arguments (type ArgumentsField) invalid: This field must be a dict' in response


@pytest.mark.parametrize("arguments", [[], 1, 1.0, "string"])
def test_api_arguments_field(arguments, load_warm_store, context):
    field = api.ArgumentsField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'This field must be a dict' in str(e)


@pytest.mark.parametrize(
    "arguments",
    [{"first_name": ["a"], "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "last_name": "b"},
    {"first_name": 1, "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "last_name": "b"},
    {"first_name": 1.0, "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "last_name": "b"},
    {"first_name": {"k":"v"}, "phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "last_name": "b"}]
)
def test_char_field(arguments, load_warm_store, context):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert '(type CharField) invalid: This field must be a string' in response


@pytest.mark.parametrize("arguments", [["a"], 1, 1.0, {"k":"v"}])
def test_api_char_field(arguments, load_warm_store, context):
    field = api.CharField()
    with pytest.raises(Exception) as e:
        val = field.validate(arguments)
    assert 'This field must be a string' in str(e)


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
def test_required_pairs_field(arguments, load_warm_store, context):
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
def test_required_field_types(full_dict, load_warm_store, context):
    request = full_dict
    set_valid_auth(request)
    response, code = get_response(request, {}, context, load_warm_store)
    assert code == 422
    assert 'Required field' in response
    assert 'is not defined!' in response



