from enum import IntEnum, unique
from typing import Dict, List, Optional


class Request(object):
    @unique
    class TYPE(IntEnum):
        eval = 0
        getattribute = 1
        setattr = 2
        call = 3

    def __init__(self, request_type, obj_id=None, args=None, kwds=None):
        # type: (TYPE, Optional[int], Optional[List], Optional[Dict]) -> None
        self.request_type = request_type
        self.obj_id = obj_id
        self.args = args
        self.kwds = kwds