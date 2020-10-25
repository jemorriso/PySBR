from pysbr.helloworld import bar


class TestHello:
    def test_helloworld(self):
        assert bar() == "Hello world"
