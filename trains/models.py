import typing
from dataclasses import dataclass


@dataclass
class Train:
    service_id: str
    service: typing.Dict
    details: typing.Dict
