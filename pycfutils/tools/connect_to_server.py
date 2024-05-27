#!/usr/bin/env python

import argparse
import sys
import time

from pycfutils.exceptions import NetworkException
from pycfutils.network import SOCKET_FAMILIES, connect_to_server


def parse_args(*argv):
    parser = argparse.ArgumentParser(description="Test listening server")
    parser.add_argument(
        "--address",
        "-a",
        default="",
        help="address to connect to",
    )
    parser.add_argument(
        "--attempt_timeout",
        "-t",
        default=1,
        type=int,
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
        print("Warning: Ignoring unknown arguments: {:}".format(unk))

    if args.port <= 0:
        parser.exit(status=-1, message="Invalid port")

    return args, unk


def main(*argv):
    args, _ = parse_args()
    print(
        f"Attempting to connect to {args.address}:{args.port} (family: {args.family})"
        f" {args.attempts} times (with a {args.attempt_timeout} timeout)..."
    )
    start_time = time.time()
    try:
        connect_to_server(
            args.address,
            args.port,
            family=args.family,
            attempts=args.attempts,
            attempt_timeout=args.attempt_timeout,
        )
    except NetworkException as e:
        print(e)
    print(f"Stopped after {time.time() - start_time:.3f} seconds")


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
