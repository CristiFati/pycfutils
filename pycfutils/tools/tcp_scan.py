#!/usr/bin/env python

import argparse
import sys

from pycfutils.exceptions import NetworkException
from pycfutils.io import read_key
from pycfutils.network import connect_to_server


def _parse_ipv4_string(ip: str) -> int:
    arr = ip.split(".")
    if len(arr) != 4:
        return None
    try:
        arr = tuple(int(e) for e in arr)
    except ValueError:
        return None
    for b in arr:
        if b < 0 or b > 0xFF:
            return None
    return sum(e << (i * 8) for i, e in enumerate(reversed(arr)))


def _ipv4_string(ip: int, zero_pad: bool = False) -> str:
    if ip < 0 or ip > 0xFFFFFFFF:
        return ""
    ip_bytes = (ip >> 24) & 0xFF, (ip >> 16) & 0xFF, (ip >> 8) & 0xFF, ip & 0xFF
    if zero_pad:
        return "{:03d}.{:03d}.{:03d}.{:03d}".format(*ip_bytes)
    else:
        return "{:d}.{:d}.{:d}.{:d}".format(*ip_bytes)


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
        print("Warning: Ignoring unknown arguments: {:}".format(unk))

    if args.timeout < 0:
        parser.exit(status=-1, message="Timeout can't be negative\n")
    if args.first_port <= 0 or args.first_port > 0xFFFF:
        parser.exit(status=-1, message="Invalid first port\n")
    if args.last_port < 0 or args.last_port > 0xFFFF:
        parser.exit(status=-1, message="Invalid last port\n")
    elif args.last_port == 0:
        args.last_port = args.first_port
    args.first_ip = _parse_ipv4_string(args.first_ip or "")
    if args.first_ip is None:
        parser.exit(status=-1, message="Invalid first IP\n")
    if args.last_ip:
        args.last_ip = _parse_ipv4_string(args.last_ip)
        if args.last_ip is None:
            parser.exit(status=-1, message="Invalid last IP\n")
    else:
        args.last_ip = args.first_ip

    return args, unk


def main(*argv):
    args, _ = parse_args()
    print(
        f"Scanning network from {_ipv4_string(args.first_ip)}"
        f" to {_ipv4_string(args.last_ip)}"
        f" on ports {args.first_port} to {args.last_port}"
        f" with a {args.timeout:.2f} connection timeout.\n"
        "Press any to interrupt...\n"
    )
    for ip in range(args.first_ip, args.last_ip + 1):
        addr = _ipv4_string(ip)
        for port in range(args.first_port, args.last_port + 1):
            print(
                "Probing {:s}:{:d} (for {:.2f} seconds)...".format(
                    addr, port, args.timeout
                )
            )
            try:
                connect_to_server(addr, port, attempts=1, attempt_timeout=args.timeout)
                print("  --- SUCCESS !!! ---")
            except NetworkException:
                pass
            if read_key() is not None:
                print("\nInterrupted by user.")
                break


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
