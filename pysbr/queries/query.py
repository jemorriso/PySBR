from string import Template

# from graphql import build_ast_schema, parse
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from pysbr.utils import Utils


# base query class
class Query:
    # with open("schema.graphql") as source:
    #     document = parse(source.read())
    # schema = build_ast_schema(document)

    def __init__(self):

        self._transport = RequestsHTTPTransport(
            url="https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service"
        )
        # client = Client(transport=_transport, fetch_schema_from_transport=True)
        self.client = Client(
            transport=self._transport, fetch_schema_from_transport=False
        )

    @staticmethod
    def _build_query_string(q_name, q_fields, q_args=None):
        """Build up the GraphQL query string.

        Args:
            q_name (str): The name of the query object to be queried.
            q_fields (str): The fields to return.
            q_args (str, optional): The arg names to pass to the query. Defaults to
                None.

        Returns:
            str: The query string ready to be substituted using Template.substitute()
        """
        return Template(
            Utils.str_format(
                """
                query {
                    $q_name(
                        $q_args
                    ) {
                        $q_fields
                    }
                }
            """
            )
        ).substitute(
            **{
                "q_name": q_name,
                "q_args": ""
                if q_args is None
                else Utils.str_format(q_args, indent_=2, dedent_l1=True),
                "q_fields": Utils.str_format(q_fields, indent_=2, dedent_l1=True),
            }
        )

    def _execute_query(self, q, subs):
        """execute a graphql query.

        args:
            q (str): the query string.
            subs (dict): the substitutions to make. each key must match a template
                placeholder, with the value being what gets substituted into the string.

        returns:
            dict: the result of the query.
        """
        return self.client.execute(gql(Template(q).substitute(subs)))
