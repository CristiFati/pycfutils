import select
import socket
import threading
from typing import Any, AnyStr, Dict, Optional, Tuple

from pycfutils.exceptions import NetworkException

__all__ = (
    "SOCKET_FAMILIES",
    # "SOCKET_FAMILY_DEFAULT",
    "SOCKET_TYPES",
    # "SOCKET_TYPE_DEFAULT",
    "TCPServer",
    "parse_address",
    "connect_to_server",
)

SOCKET_FAMILY_IPV4 = "ipv4"
SOCKET_FAMILY_IPV6 = "ipv6"
SOCKET_FAMILY_UNIX = "unix"
SOCKET_FAMILY_UNSPEC = "unspec"
_SocketFamilyMap = {
    SOCKET_FAMILY_IPV4: socket.AF_INET,
    # SOCKET_FAMILY_UNIX: socket.AF_UNIX,
    # SOCKET_FAMILY_UNSPEC: socket.AF_UNSPEC,
}
__all__ += (
    "SOCKET_FAMILY_IPV4",
    # "SOCKET_FAMILY_UNIX",
    # "SOCKET_FAMILY_UNSPEC",
)
if socket.has_ipv6:
    _SocketFamilyMap[SOCKET_FAMILY_IPV6] = socket.AF_INET6
    __all__ += ("SOCKET_FAMILY_IPV6",)
SOCKET_FAMILIES = tuple(_SocketFamilyMap.keys())
SOCKET_FAMILY_DEFAULT = SOCKET_FAMILY_IPV4
if SOCKET_FAMILY_DEFAULT not in SOCKET_FAMILIES:
    raise NetworkException("Invalid default socket family")

SOCKET_TYPE_TCP = "tcp"
SOCKET_TYPE_UDP = "udp"
SOCKET_TYPE_RAW = "raw"
_SocketTypeMap = {
    SOCKET_TYPE_TCP: socket.SOCK_STREAM,
    SOCKET_TYPE_UDP: socket.SOCK_DGRAM,
    # SOCKET_TYPE_RAW: socket.SOCK_RAW,
}
__all__ += (
    "SOCKET_TYPE_TCP",
    "SOCKET_TYPE_UDP",
    # "SOCKET_TYPE_RAW",
)
SOCKET_TYPES = tuple(_SocketTypeMap.keys())
SOCKET_TYPE_DEFAULT = SOCKET_TYPE_TCP
if SOCKET_TYPE_DEFAULT not in SOCKET_TYPES:
    raise NetworkException("Invalid default socket type")

_ADDRESS_DEFAULT = "localhost"
_PORT_DEFAULT = 27183
_TIMEOUT_DEFAULT = 1

SockOpts = Optional[Dict[int, Dict[int, Any]]]


def _close_socket(s) -> None:
    if not isinstance(s, socket.socket):
        return
    try:
        s.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    s.close()


def _parse_address(
    address: AnyStr,
    port: int,
    family: Optional[AnyStr],
    type_: Optional[AnyStr],
) -> Optional[Tuple]:
    records = socket.getaddrinfo(
        address,
        port,
        family=_SocketFamilyMap[family.lower()] if family is not None else 0,
        type=_SocketTypeMap[type_.lower()] if type_ is not None else 0,
    )
    return tuple((*e[-1][:2], e[0], e[1]) for e in records)


def parse_address(
    address: AnyStr,
    port: int = 0,
    family: Optional[AnyStr] = None,
    type_: Optional[AnyStr] = None,
    exact_matches: int = 0,
) -> Optional[Tuple]:
    if (family is not None and family not in SOCKET_FAMILIES) or (
        type_ is not None and type_ not in SOCKET_TYPES
    ):
        raise NetworkException("Invalid family or type")
    try:
        records = _parse_address(
            address,
            port,
            family,
            type_,
        )
    except (socket.gaierror, socket.error) as e:
        raise NetworkException from e
    else:
        if exact_matches > 0 and exact_matches != len(records):
            raise NetworkException(
                f"Got {len(records)} records (expected {exact_matches})"
            )
        return records


def _create_socket(
    family: socket.AddressFamily,
    type_: socket.SocketKind,
    timeout: float,
    options: SockOpts,
) -> socket.SocketType:
    sock = socket.socket(family=family, type=type_)
    try:
        if timeout <= 0:
            sock.setblocking(False)
        else:
            sock.setblocking(True)
            sock.settimeout(timeout)
        if options:
            for level, opts in options.items():
                for name, value in opts.items():
                    sock.setsockopt(level, name, value)
    except Exception:
        sock.close()
        raise
    return sock


class _Server:
    def __init__(
        self,
        address: AnyStr,
        port: int,
        family: Optional[AnyStr],
        type_: Optional[AnyStr],
        poll_timeout: float,
        silent: bool,
        options: SockOpts,
        backlog: int,
    ) -> None:
        self.poll_timeout = poll_timeout
        self.silent = silent
        self.type = type_
        self.running = False
        self.thread = None
        self.socket = None
        self.daemon_thread = False
        record = parse_address(
            address, port=port, family=family, type_=type_, exact_matches=1
        )
        address, port, family, self.type = record[0]
        try:
            self.socket = _create_socket(family, self.type, 0, options)
            self.socket.bind((address, port))
            self.socket.listen(backlog)
        except Exception as e:
            self.close()
            raise NetworkException from e

    def __enter__(self):
        if not self.start():
            raise NetworkException("Could not start server")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.close()
        return exc_type is None

    def __del__(self) -> None:
        self.stop()
        self.close()

    def start(self) -> bool:
        if self.socket is None:
            return False
        if self.running:
            return True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = self.daemon_thread
        self.running = True
        self.thread.start()
        return True

    def stop(self) -> None:
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def handle_incoming(self) -> bool:
        raise NotImplementedError

    def _run(self) -> None:
        if self.socket is None:
            return
        while self.running:
            if (
                self.socket
                in select.select((self.socket,), (), (), self.poll_timeout)[0]
            ):
                self.handle_incoming()

    def close(self) -> None:
        _close_socket(self.socket)
        self.socket = None


class TCPServer(_Server):
    def __init__(
        self,
        address: AnyStr,
        port: int,
        family: Optional[AnyStr] = None,
        poll_timeout: float = _TIMEOUT_DEFAULT,
        silent: bool = False,
        options: SockOpts = None,
        backlog: int = 5,
    ) -> None:
        super().__init__(
            address,
            port,
            family,
            SOCKET_TYPE_TCP,
            poll_timeout,
            silent,
            options,
            backlog,
        )

    def handle_incoming(self) -> bool:
        try:
            client, peer = self.socket.accept()
            if not self.silent:
                print(f"Established connection from {peer[0]:s}:{peer[1]:d}")
            _close_socket(client)
            return True
        except Exception as e:
            if not self.silent:
                print(e)
            return False


def connect_to_server(
    address: AnyStr,
    port: int,
    family: Optional[str] = None,
    attempts: int = 1,
    attempt_timeout: float = _TIMEOUT_DEFAULT,
    options: SockOpts = None,
) -> Tuple:
    attempts = max(attempts, 1)
    record = parse_address(
        address, port=port, family=family, type_=SOCKET_TYPE_TCP, exact_matches=1
    )
    address, port, family, type_ = record[0]
    client = None
    try:
        client = _create_socket(family, type_, attempt_timeout, options)
        res = None
        for _ in range(attempts):
            res = client.connect_ex((address, port))
            if res == 0:
                return client.getsockname()
        else:
            raise NetworkException(f"Connect returned {res}")
    except Exception as e:
        raise NetworkException from e
    finally:
        _close_socket(client)
