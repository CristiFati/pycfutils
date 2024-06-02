#!/usr/bin/env python

import argparse
import socket
import sys
import time

from pycfutils.exceptions import NetworkException
from pycfutils.io import read_key
from pycfutils.network import SOCKET_FAMILIES, SOCKET_TYPE_TCP, TCPServer, parse_address


def parse_args(*argv):
    parser = argparse.ArgumentParser(description="Start listening server")
    parser.add_argument(
        "--address",
        "-a",
        default="",
        help="address to listen on (must resolve to exactly one IP)",
    )
    parser.add_argument(
        "--family",
        "-f",
        choices=SOCKET_FAMILIES,
        default=None,
        help="address family",
    )
    parser.add_argument(
        "--poll_timeout",
        "-t",
        default=1,
        type=float,
        help="time the server polls for incoming connections",
    )
    parser.add_argument("--port", "-p", default=0, type=int, help="port to listen on")
    parser.add_argument(
        "--reuse_port",
        "-r",
        action="store_true",
        help="reuse address/port (other sockets may bind to it)",
    )

    args, unk = parser.parse_known_args()
    if unk:
        print(f"Warning: Ignoring unknown arguments: {unk}")

    if args.port <= 0:
        parser.exit(status=-1, message="Invalid port\n")

    try:
        record = parse_address(
            args.address or "",
            args.port,
            family=args.family,
            type_=SOCKET_TYPE_TCP,
            exact_matches=1,
        )[0]
    except NetworkException as e:
        parser.exit(status=-1, message=f"Invalid address: {e}\n")
    args.address = record[0], record[2]

    return args, unk


def main(*argv):
    args, _ = parse_args()
    print(
        f"Attempting to start a TCP server listening on"
        f" {args.address[0].join('[]') if args.address[-1] == socket.AF_INET6 else args.address[0]}"
        f":{args.port} (family: {str(args.address[-1])})"
        f" (with a {args.poll_timeout:.2f}s connection check timeout).\n"
        "Press any key to interrupt...\n"
    )
    total, ok = 0, 0
    fail = False
    options = (
        {socket.SOL_SOCKET: {getattr(socket, "SO_REUSEPORT", socket.SO_REUSEADDR): 1}}
        if args.reuse_port
        else None
    )
    start_time = time.time()
    try:
        with TCPServer(
            args.address[0],
            args.port,
            family=args.family,
            poll_timeout=args.poll_timeout,
            silent=False,
            options=options,
        ) as srv:
            while True:
                if read_key(timeout=0.5, poll_interval=0.1) is not None:
                    print("Interrupted by user")
                    break
            total = srv.handled_total
            ok = srv.handled_ok
    except NetworkException as e:
        print(f"  FAILURE: {e}\n")
        fail = True
    print(
        f"Handled {total} (successfully {ok}) connections in {time.time() - start_time:.3f} seconds"
    )
    return int(fail)


if __name__ == "__main__":
    print(
        "Python {:s} {:03d}bit on {:s}\n".format(
            " ".join(elem.strip() for elem in sys.version.split("\n")),
            64 if sys.maxsize > 0x100000000 else 32,
            sys.platform,
        )
    )
    rc = main(*sys.argv[1:])
    print("\nDone.\n")
    sys.exit(rc)
