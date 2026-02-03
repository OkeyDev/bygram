from _typeshed import Incomplete

class TdlibException(Exception):
    code: Incomplete
    message: Incomplete
    def __init__(self, code: int, message: str) -> None: ...
