# from pysbr.queries.query import Query
import vcr
import requests


class TestQuery:
    def test_build_query(self):
        assert True

    @vcr.use_cassette("tests/cassettes/test_cassette.yaml")
    def test_cassete(self):
        r = requests.get("https://api.github.com/users/JeMorriso")
        assert r.headers["X-Github-Request-Id"] == "D3E6:3C26:1160E7:2D5DC3:5F98DDF3"
