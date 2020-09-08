from django.test import SimpleTestCase
from graphql_jwt.testcases import JSONWebTokenClient
from gw_bilby.schema import schema
from graphql_jwt.shortcuts import get_token
from graphql_jwt.settings import jwt_settings


class CustomJSONWebTokenClient(JSONWebTokenClient):
    """Test client with a custom authentication method."""

    def authenticate(self, user):
        """Payload for authentication which requires a special userID parameter."""
        self._credentials = {
            jwt_settings.JWT_AUTH_HEADER_NAME: "{0} {1}".format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX, get_token(user, userId=user.id)
            ),
        }


class CustomJwtTestCase(SimpleTestCase):
    """
    Test cases that require graphene authentication should inherit from this test class.

    It overrides some settings that will be common to most db search test cases.

    Attributes
    ----------

    GRAPHQL_SCHEMA : schema object
        Uses the db search schema file as the default schema.

    GRAPHQL_URL : str
        Sets the graphql url to the current db search url.

    client_class : class
        Sets client to be a specific object that uses a custom authentication.
        method.
    """

    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/graphql"
    client_class = CustomJSONWebTokenClient
