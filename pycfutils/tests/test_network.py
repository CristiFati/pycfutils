import socket
import sys
import time
import unittest

from pycfutils import network

_IS_WIN = sys.platform[:3].lower() == "win"


class NetworkBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.ipv6 = socket.has_ipv6
        self.lh = "localhost"
        self.lh4 = "127.0.0.1"
        self.lh6 = "::1"
        self.port = network._PORT_DEFAULT
        self.families = (network.SOCKET_FAMILY_IPV4,)
        if self.ipv6:
            self.families += (network.SOCKET_FAMILY_IPV6,)
        # if not _IS_WIN:
        #     self.families += (network.SOCKET_FAMILY_UNIX,)
        self.types = (network.SOCKET_TYPE_TCP, network.SOCKET_TYPE_UDP)
        self.timeout = network._TIMEOUT_DEFAULT
        self.min_conns = (2 if self.ipv6 else 1) - 1  # Greater


class NetworkGenericTestCase(NetworkBaseTestCase):
    def test__parse_address(self):
        self.assertRaises(KeyError, network._parse_address, "", self.port, "fam", None)
        self.assertRaises(KeyError, network._parse_address, "", self.port, None, "type")
        if _IS_WIN:
            self.assertGreater(
                len(network._parse_address("", self.port, None, None)), self.min_conns
            )
        else:
            self.assertRaises(
                socket.gaierror, network._parse_address, "", self.port, None, None
            )
        self.assertGreater(
            len(network._parse_address(self.lh, self.port, None, None)), self.min_conns
        )
        res = network._parse_address(self.lh4, self.port, None, None)
        for t in res:
            self.assertEqual(t[2], socket.AF_INET)
        if self.ipv6:
            res = network._parse_address(self.lh6, self.port, None, None)
            for t in res:
                self.assertEqual(t[2], socket.AF_INET6)
        for family in self.families:
            for typ in self.types:
                res = network._parse_address(self.lh, self.port, family, typ)
                self.assertEqual(len(res), 1)

    def test_parse_address(self):
        self.assertRaises(
            network.NetworkException,
            network.parse_address,
            "",
            self.port,
            {"family": "fam"},
        )
        self.assertRaises(
            network.NetworkException,
            network.parse_address,
            "",
            self.port,
            {"type_": "type"},
        )
        self.assertRaises(
            network.NetworkException,
            network.parse_address,
            self.lh4,
            self.port,
            {"family": network.SOCKET_FAMILY_IPV6},
        )
        self.assertRaises(
            network.NetworkException,
            network.parse_address,
            self.lh6,
            self.port,
            {"family": network.SOCKET_FAMILY_IPV4},
        )
        self.assertGreater(
            len(network.parse_address(self.lh, self.port)), self.min_conns
        )
        self.assertGreater(len(network.parse_address(self.lh4, self.port)), 0)
        if self.ipv6:
            self.assertGreater(len(network.parse_address(self.lh6, self.port)), 0)
            self.assertRaises(
                network.NetworkException,
                network.parse_address,
                self.lh,
                self.port,
                {"exact_matches": 1},
            )
        for family in self.families:
            for typ in self.types:
                res = network.parse_address(
                    self.lh, self.port, family=family, type_=typ, exact_matches=1
                )
                self.assertEqual(len(res), 1)

    def test__create_socket(self):
        families = (network._SocketFamilyMap[e] for e in self.families)
        types = (network._SocketTypeMap[e] for e in self.types)
        opts = {
            socket.SOL_SOCKET: {
                socket.SO_REUSEADDR: 1,
            }
        }
        for family in families:
            for typ in types:
                for opt in (opts, None):
                    try:
                        sock = network._create_socket(family, typ, self.timeout, opt)
                    except Exception:
                        self.assertTrue(False)
                    else:
                        sock.close()


# @unittest.skip("")
class NetworkTCPServerClientTestCase(NetworkBaseTestCase):
    def test_tcpserver(self):
        self.assertRaises(
            network.NetworkException,
            network.TCPServer,
            self.lh4,
            self.port,
            {"family": network.SOCKET_FAMILY_IPV6},
        )
        self.assertRaises(
            network.NetworkException,
            network.TCPServer,
            self.lh6,
            self.port,
            {"family": network.SOCKET_FAMILY_IPV4},
        )
        with network.TCPServer(self.lh4, self.port):
            time.sleep(0.5)
        with network.TCPServer(
            self.lh, self.port, family=network.SOCKET_FAMILY_IPV4, poll_timeout=0
        ):
            time.sleep(0.1)
        if self.ipv6:
            # self.assertRaises(network.NetworkException, network.TCPServer, self.lh, self.port)  #  /etc/hosts !!!
            with network.TCPServer(self.lh6, self.port):
                time.sleep(0.5)
            with network.TCPServer(
                self.lh, self.port, family=network.SOCKET_FAMILY_IPV6, poll_timeout=0
            ):
                time.sleep(0.1)
        srvs = []
        pofs = 0
        for family in self.families:
            s = network.TCPServer(self.lh, self.port + pofs, family=family)
            pofs += 1
            srvs.append(s)
        for srv in srvs:
            srv.start()
        time.sleep(1)
        for srv in srvs:
            srv.stop()

    def test_connect_to_server(self):
        self.assertRaises(
            network.NetworkException,
            network.connect_to_server,
            self.lh,
            self.port,
            attempt_timeout=0.5,
        )
        self.assertRaises(
            network.NetworkException,
            network.connect_to_server,
            self.lh,
            self.port,
            attempt_timeout=0,
        )

    def test_server_client(self):
        with network.TCPServer(self.lh4, self.port, silent=True):
            self.assertEqual(
                network.connect_to_server(self.lh4, self.port, attempt_timeout=0.5)[0],
                self.lh4,
            )
            self.assertRaises(
                network.NetworkException,
                network.connect_to_server,
                self.lh4,
                self.port,
                {"attempt_timeout": 0},
            )
        if self.ipv6:
            with network.TCPServer(self.lh6, self.port, silent=True):
                self.assertEqual(
                    network.connect_to_server(self.lh6, self.port, attempt_timeout=0.5)[
                        0
                    ],
                    self.lh6,
                )
                self.assertRaises(
                    network.NetworkException,
                    network.connect_to_server,
                    self.lh6,
                    self.port,
                    {"attempt_timeout": 0},
                )
