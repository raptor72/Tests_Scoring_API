import pytest
import api
from collections import namedtuple

@pytest.fixture
def setUp():
    context = {}
    headers = {}
    settings = {}
    return {"context": context, "headers": headers, "settings": settings}

def get_response(setUp, request):
    return api.method_handler({"body": request, "headers": setUp["headers"]}, setUp["context"], setUp["settings"])

def test_empty_request(setUp):
    _, code = get_response(setUp, {})
    assert api.INVALID_REQUEST == code


