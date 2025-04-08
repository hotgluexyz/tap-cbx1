"""TapCBX1 Authentication."""

import json
import requests
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from singer_sdk.helpers._util import utc_now
from singer_sdk.streams import Stream as RESTStreamBase
from typing import Optional

# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class TapCBX1Auth(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for TapCBX1."""

    def __init__(
        self,
        stream: RESTStreamBase,
        auth_endpoint: Optional[str] = None,
        oauth_scopes: Optional[str] = None
    ) -> None:
        super().__init__(stream=stream, auth_endpoint=auth_endpoint, oauth_scopes=oauth_scopes)
        self._tap = stream._tap
        self.stream = stream

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the TapCBX1 API."""
        return {
            "authenticationType": "ACCESS_KEY",
            "code": self.stream.config.get("access_key")
        }

    @classmethod
    def create_for_stream(cls, stream) -> "TapCBX1Auth":
        return cls(
            stream=stream,
            auth_endpoint="https://qa-api.cbx1.app/api/g/v1/auth/token/generate",
        )

    # Authentication and refresh
    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`.

        Raises:
            RuntimeError: When OAuth login fails.
        """
        request_time = utc_now()
        auth_request_payload = self.oauth_request_payload
        headers = {
            "x-organisation-id": self.stream.config.get("organization_id")
        }
        token_response = requests.get(self.auth_endpoint, params=auth_request_payload, headers=headers)
        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")

        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            )
        token_json = token_response.json().get("data")
        self.access_token = token_json["sessionToken"]
        self.expires_in = token_json.get("maxAge", 10)
        if self.expires_in is None:
            self.logger.debug(
                "No expires_in receied in OAuth response and no "
                "default_expiration set. Token will be treated as if it never "
                "expires."
            )
        self.last_refreshed = request_time

        # store access_token in config file
        self._tap._config["access_token"] = token_json["sessionToken"]
        # self._tap._config["refresh_token"] = token_json["refresh_token"]

        with open(self._tap.config_file, "w") as outfile:
            json.dump(self._tap._config, outfile, indent=4)
