import requests
from datetime import datetime

from pytest import mark
from gql import gql


class TestQuery:
    def test_cassete(self, use_cassette):
        with use_cassette("test_cassette"):
            r = requests.get("https://api.github.com/users/JeMorriso")
            assert (
                r.headers["X-Github-Request-Id"] == "D3E6:3C26:1160E7:2D5DC3:5F98DDF3"
            )

    def test_cassette_gql(self, utils, use_cassette, countries):
        with use_cassette("test_cassette_gql"):
            query = utils.str_format(
                """
                    query {
                        country(code: "CA") {
                                name
                        }
                    }
                    """
            )
            result = countries.execute(gql(query))
            assert result["country"]["name"] == "Canada"

    def test_build_query(self, utils, query):
        events = utils.str_format(
            """
            events {
                des
                cit
                cou
                es
                dt
                eid
                st
                participants {
                    partid
                    ih
                    source {
                        ... on Team {
                            nam
                            nn
                            sn
                            abbr
                        }
                    }
                }
            }
        """
        )
        args = utils.str_format(
            """
            "lid": $ lids,
            "startDate: $dt,
            "hoursRange": 24
            """
        )
        q_string = query._build_query_string("eventsByDateNew", events, args)
        assert q_string == utils.str_format(
            """
            query {
                eventsByDateNew(
                    "lid": $ lids,
                    "startDate: $dt,
                    "hoursRange": 24
                ) {
                    events {
                        des
                        cit
                        cou
                        es
                        dt
                        eid
                        st
                        participants {
                            partid
                            ih
                            source {
                                ... on Team {
                                    nam
                                    nn
                                    sn
                                    abbr
                                }
                            }
                        }
                    }
                }
            }
            """
        )

    @mark.parametrize("dt_str", ["2020-10-29"])
    def test_execute_query(self, utils, query, patched_execute, dt_str):
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        q_fields = utils.str_format(
            """
            events {
                eid
            }
        """
        )
        q_args = utils.str_format(
            """
            lid: $lids,
            startDate: $dt,
            hoursRange: 24
            """
        )
        result = patched_execute(
            query._build_query_string("eventsByDateNew", q_fields, q_args),
            {
                "lids": [16],
                "dt": utils.datetime_to_timestamp(dt),
            },
            "test_execute_query",
        )
        assert result["eventsByDateNew"]["events"][0]["eid"] == 4143517
