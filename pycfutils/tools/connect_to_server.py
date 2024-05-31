#!/usr/bin/env python

import argparse
import socket
import sys
import time

from pycfutils.exceptions import NetworkException
from pycfutils.network import (
    SOCKET_FAMILIES,
    SOCKET_TYPE_TCP,
    connect_to_server,
    parse_address,
)


def parse_args(*argv):
    parser = argparse.ArgumentParser(description="Test listening server")
    parser.add_argument(
        "--address",
        "-a",
        default="",
        help="address to connect to (must resolve to exactly one IP)",
    )
    parser.add_argument(
        "--attempt_timeout",
        "-t",
        default=1,
        type=float,
        help="wait time for each attempt",
    )
    parser.add_argument(
        "--attempts", "-c", default=1, type=int, help="number of connection attempts"
    )
    parser.add_argument("--port", "-p", default=0, type=int, help="port to connect to")
    parser.add_argument(
        "--family",
        "-f",
        choices=SOCKET_FAMILIES,
        default=None,
        help="address family",
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
        "Attempting to connect to"
        f" {args.address[0].join('[]') if args.address[-1] == socket.AF_INET6 else args.address[0]}"
        f":{args.port} (family: {str(args.address[-1])})"
        f" {args.attempts} times (with a {args.attempt_timeout:.2f}s timeout)..."
    )
    start_time = time.time()
    try:
        connect_to_server(
            args.address[0],
            args.port,
            family=args.family,
            attempts=args.attempts,
            attempt_timeout=args.attempt_timeout,
        )
    except NetworkException as e:
        print(f"  FAILURE: {e} (took {time.time() - start_time:.3f} seconds)")
        return 1
    else:
        print(
            f"  --- !!! SUCCESS !!! --- (took {time.time() - start_time:.3f} seconds)"
        )
        return 0


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
