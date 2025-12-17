import ctypes
import platform


class TdLibWrapper:
    def __init__(self, cdll: ctypes.CDLL) -> None:
        self.cdll = cdll

        self._create_client = self.cdll.td_create_client_id
        self._create_client.argtypes = []
        self._create_client.restype = ctypes.c_int

        self._json_client_send = self.cdll.td_send
        self._json_client_send.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self._json_client_send.restype = None

        self._json_client_receive = self.cdll.td_receive
        self._json_client_receive.argtypes = [ctypes.c_double]
        self._json_client_receive.restype = ctypes.c_char_p

        self._json_client_execute = self.cdll.td_execute
        self._json_client_execute.argtypes = [ctypes.c_char_p]
        self._json_client_execute.restype = ctypes.c_char_p

    def create_client(self) -> int:
        return self._create_client()

    def send(self, client_id: int, request: bytes) -> None:
        self._json_client_send(client_id, request)

    def receive(self, timeout: float) -> bytes | None:
        return self._json_client_receive(timeout)

    def execute(self, request: bytes) -> bytes:
        return self._json_client_execute(request)


def _to_full_path(path: str) -> str:
    return path


def _load_linux(path: str) -> ctypes.CDLL:
    return ctypes.CDLL(path)


def load_library(path: str) -> TdLibWrapper:
    path = _to_full_path(path)
    if platform.system() == "Linux":
        cdll = _load_linux(path)
    else:
        raise RuntimeError("Sorry but your OS is not supported")

    return TdLibWrapper(cdll)
