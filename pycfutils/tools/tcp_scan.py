#!/usr/bin/env python

import argparse
import socket
import sys
import time

from pycfutils.exceptions import NetworkException
from pycfutils.io import read_key
from pycfutils.miscellaneous import uniques
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
        "--first_address",
        "-a",
        action="append",
        dest="first_addresses",
        default=[],
        help="first address to scan. Can be specified multiple times"
             " (in that case only the specified addresses (resolved IPs) will be attempted)",
    )
    parser.add_argument(
        "--first_port",
        "-p",
        action="append",
        default=[],
        dest="first_ports",
        type=int,
        help="first port to scan. Can be specified multiple times"
             " (in that case only the specified ports will be attempted)",
    )
    parser.add_argument(
        "--last_ip",
        "-i",
        help="last IP to scan (defaults to first). Must be the same family with first."
             " If more than one first address is specified (or it resolves to multiple IPs),"
             " this is ignored",
    )
    parser.add_argument(
        "--last_port",
        "-r",
        default=0,
        type=int,
        help="last port to scan (defaults to first, must be greater or equal to first)."
             " If more than one first port is specified, this is ignored",
    )
    parser.add_argument(
        "--timeout", "-t", default=0.5, type=float, help="connection timeout"
    )

    args, unk = parser.parse_known_args()
    if unk:
        print(f"Warning: Ignoring unknown arguments: {unk}")

    if args.timeout < 0:
        parser.exit(status=-1, message="Timeout can't be negative\n")
    args.first_ports = uniques(args.first_ports)
    if not args.first_ports:
        parser.exit(status=-1, message="At least one first port must be specified\n")
    for fp in args.first_ports:
        if fp <= 0 or fp > 0xFFFF:
            parser.exit(status=-1, message="Invalid first port\n")
    if len(args.first_ports) == 1:
        if args.last_port < 0 or args.last_port > 0xFFFF:
            parser.exit(status=-1, message="Invalid last port\n")
        elif args.last_port == 0:
            args.last_port = args.first_ports[0]
    else:
        if args.last_port != 0:
            print("Last port passed with multiple first ports. Ignoring")
    addr_strs = tuple(e for e in uniques(args.first_addresses) if e)
    if not addr_strs:
        parser.exit(
            status=-1, message=f"At least one first address must be specified\n"
        )
    addrs = []
    for addr_str in addr_strs:
        try:
            records = parse_address(addr_str, 0, type_=SOCKET_TYPE_TCP)
        except NetworkException as e:
            print(f"Address {addr_str} could not be resolved ({e}). Ignoring")
            continue
        for record in records:
            ipn = int.from_bytes(
                socket.inet_pton(record[2], record[0]), byteorder="big"
            )
            addrs.append((ipn, record[2]))
    if not addrs:
        parser.exit(status=-1, message="No valid (first) address passed\n")
    args.first_addresses = addrs
    if len(args.first_addresses) == 1:
        if args.last_ip:
            try:
                record = parse_address(
                    args.last_ip or "", 0, type_=SOCKET_TYPE_TCP, exact_matches=1
                )[0]
            except NetworkException as e:
                parser.exit(status=-1, message=f"Invalid last IP: {e}\n")
            ipn = int.from_bytes(
                socket.inet_pton(record[2], record[0]), byteorder="big"
            )
            args.last_ip = ipn, record[2]
        else:
            args.last_ip = args.first_addresses[0]
        if args.first_addresses[0][-1] != args.last_ip[-1]:
            parser.exit(status=-1, message="IP families don't match\n")
    else:
        if args.last_ip:
            print("Last ip passed with multiple first addresses. Ignoring")

    return args, unk


def main(*argv):
    args, _ = parse_args()
    ips = len(args.first_addresses) > 1
    ports = len(args.first_ports) > 1
    addr_text = (
        f"addresses: {', ' .join(_ip_string(*e) for e in args.first_addresses)}"
        if ips
        else f"from {_ip_string(*args.first_addresses[0])} to {_ip_string(*args.last_ip)}"
    )
    port_text = (
        f"{', ' .join(str(e) for e in args.first_ports)}"
        if ports
        else f"from {args.first_ports[0]} to {args.last_port}"
    )
    print(
        f"Scanning network ({addr_text}) on ports {port_text}"
        f" with a {args.timeout:.2f}s connection timeout.\n"
        "Press any to interrupt...\n"
    )
    total, ok = 0, 0
    start_time = time.time()
    brk = False
    for ip in (
        args.first_addresses
        if ips
        else (
            (e, args.first_addresses[0][-1])
            for e in range(args.first_addresses[0][0], args.last_ip[0] + 1)
        )
    ):
        addr = _ip_string(*ip)
        for port in (
            args.first_ports
            if ports
            else range(args.first_ports[0], args.last_port + 1)
        ):
            print(
                "Probing {:s}:{:d} (for {:.2f} seconds)...".format(
                    addr, port, args.timeout
                )
            )
            try:
                total += 1
                cur_start_time = time.time()
                connect_to_server(addr, port, attempts=1, attempt_timeout=args.timeout)
                print(
                    f"  --- !!! SUCCESS !!! --- (took {time.time() - cur_start_time:.3f} seconds)"
                )
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
