import pytest
import api
import hashlib
from collections import namedtuple
from store import Store

@pytest.fixture
def setUp():
    context = {}
    headers = {}
    store = Store
#    store = None

#    return {"context": context, "headers": headers, "store": Store}

print(setUp.context)



def get_response(setUp, request):
    return api.method_handler({"body": request, "headers": setUp["headers"]}, setUp["context"], setUp["store"])


def set_valid_auth(setUp, request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg).hexdigest()

#    return request["token"]

def test_empty_request(setUp):
    _, code = get_response(setUp, {})
    assert api.INVALID_REQUEST == code



#def test_ok_score_request(setUp, arguments={"phone": "79175002040", "email": "stupnikov@otus.ru"}):
#    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
#    set_valid_auth(setUp, request)
#    response, code = get_response(setUp, request)
#    return response, code
#    assert api.OK == code
#    assert code == arguments
#    score = response.get("score")
#    self.assertTrue(isinstance(score, (int, float)) and score >= 0, arguments)
#    self.assertEqual(sorted(self.context["has"]), sorted(arguments.keys()))



#test_ok_score_request(setUp, arguments={"phone": "79175002040", "email": "stupnikov@otus.ru"})


#print(get_response(setUp, {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru"}}))

