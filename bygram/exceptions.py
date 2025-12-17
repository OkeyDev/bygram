class TdlibException(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
