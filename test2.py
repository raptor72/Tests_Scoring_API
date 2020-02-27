import pytest
import api
import hashlib
from collections import namedtuple
from store import Store


class TestSomeThing:
    @pytest.fixture
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = Store
        return {"context": self.context, "headers": self.headers, "store": self.store}

    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "replace")
        print(dir(x))

    def get_response(self, request):
#        return api.method_handler({"body": request, "headers": self.setUp["headers"]}, self.setUp["context"], self.setUp["store"])
        return api.method_handler({"body": request, "headers": {}}, {}, Store)

    def test_empty_request(self):
        _, code = self.get_response({})
        assert api.INVALID_REQUEST == code

