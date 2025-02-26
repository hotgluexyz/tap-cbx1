"""CBX1 tap class."""

import inspect
from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_cbx1 import streams


class TapCBX1(Tap):
    """CBX1 tap class."""

    name = "tap-cbx1"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=True,
        ),
        th.Property("organization_id", th.StringType, required=True),
        th.Property("user_id", th.StringType, required=True)
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [
            cls(self)
            for _, cls in inspect.getmembers(streams, inspect.isclass)
            if cls.__module__ == "tap_cbx1.streams" and hasattr(cls, "name")
        ]


if __name__ == "__main__":
    TapCBX1.cli()
