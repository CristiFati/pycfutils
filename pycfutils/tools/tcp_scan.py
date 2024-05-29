#!/usr/bin/env python

import argparse
import socket
import sys
import time

from pycfutils.exceptions import NetworkException
from pycfutils.io import read_key
from pycfutils.network import SOCKET_TYPE_TCP, connect_to_server, parse_address


def _ip_string(ip: int, family: socket.AddressFamily) -> str:
    size = 16 if family == socket.AF_INET6 else 4
    addr = socket.inet_ntop(family, ip.to_bytes(length=size, byteorder="big"))
    return addr.join("[]") if family == socket.AF_INET6 else addr


def parse_args(*argv):
    parser = argparse.ArgumentParser(
        description="IP(v4):Port scanner",
        epilog="Scans the IP:port combination in the given ranges",
    )
    parser.add_argument(
        "--first_ip", "-f", default="127.0.0.1", help="first IP to scan"
    )
    parser.add_argument("--last_ip", "-l", help="last IP to scan (defaults to first)")
    parser.add_argument(
        "--first_port", "-p", default=0, type=int, help="first port to scan"
    )
    parser.add_argument(
        "--last_port",
        "-r",
        default=0,
        type=int,
        help="last port to scan (defaults to first)",
    )
    parser.add_argument(
        "--timeout", "-t", default=1, type=float, help="connection timeout"
    )

    args, unk = parser.parse_known_args()
    if unk:
        print(f"Warning: Ignoring unknown arguments: {unk}")

    if args.timeout < 0:
        parser.exit(status=-1, message="Timeout can't be negative\n")
    if args.first_port <= 0 or args.first_port > 0xFFFF:
        parser.exit(status=-1, message="Invalid first port\n")
    if args.last_port < 0 or args.last_port > 0xFFFF:
        parser.exit(status=-1, message="Invalid last port\n")
    elif args.last_port == 0:
        args.last_port = args.first_port
    try:
        record = parse_address(
            args.first_ip or "", 0, type_=SOCKET_TYPE_TCP, exact_matches=1
        )[0]
    except NetworkException as e:
        parser.exit(status=-1, message=f"Invalid first IP: {e}\n")
    ipn = int.from_bytes(socket.inet_pton(record[2], record[0]), byteorder="big")
    args.first_ip = ipn, record[2]
    if args.last_ip:
        try:
            record = parse_address(
                args.last_ip or "", 0, type_=SOCKET_TYPE_TCP, exact_matches=1
            )[0]
        except NetworkException as e:
            parser.exit(status=-1, message=f"Invalid last IP: {e}\n")
        ipn = int.from_bytes(socket.inet_pton(record[2], record[0]), byteorder="big")
        args.last_ip = ipn, record[2]
    else:
        args.last_ip = args.first_ip
    if args.first_ip[-1] != args.last_ip[-1]:
        parser.exit(status=-1, message="IP families don't match\n")

    return args, unk


def main(*argv):
    args, _ = parse_args()
    print(
        f"Scanning network from {_ip_string(*args.first_ip)}"
        f" to {_ip_string(*args.last_ip)}"
        f" on ports {args.first_port} to {args.last_port}"
        f" with a {args.timeout:.2f}s connection timeout.\n"
        "Press any to interrupt...\n"
    )
    fam = args.first_ip[-1]
    total, ok = 0, 0
    start_time = time.time()
    brk = False
    for ip in range(args.first_ip[0], args.last_ip[0] + 1):
        addr = _ip_string(ip, fam)
        for port in range(args.first_port, args.last_port + 1):
            print(
                "Probing {:s}:{:d} (for {:.2f} seconds)...".format(
                    addr, port, args.timeout
                )
            )
            try:
                total += 1
                connect_to_server(addr, port, attempts=1, attempt_timeout=args.timeout)
                print("  --- !!! SUCCESS !!! ---")
            except NetworkException:
                pass
            else:
                ok += 1
            if read_key(timeout=0.5, poll_interval=0.1) is not None:
                print("\nInterrupted by user")
                brk = True
                break
        if brk:
            break
    print(
        f"\nAttempted {total} ({ok} successful) connection(s) in {time.time() - start_time:.3f} seconds"
    )


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
