#!/usr/bin/env python

import argparse
import os
import sys
import time

from pycfutils.system import cpu_stress


def parse_args(*argv):
    parser = argparse.ArgumentParser(description="CPU Stress")
    parser.add_argument(
        "--cpus",
        "-c",
        choices=range(1, os.cpu_count() + 1),
        default=1,
        type=int,
        help="number of CPUs to stress",
    )
    parser.add_argument(
        "--time", "-t", default=10, type=float, help="time (seconds) to stress"
    )

    args, unk = parser.parse_known_args()
    if unk:
        print("Warning: Ignoring unknown arguments: {:}".format(unk))

    args.time = max(0, args.time)

    return args, unk


def main(*argv):
    args, _ = parse_args()
    print(
        f"Attempting to start {args.cpus} process(es)"
        f" for{f' {args.time} seconds' if args.time else 'ever'}..."
    )
    start_time = time.time()
    try:
        cpu_stress(duration=args.time, count=args.cpus)
    except KeyboardInterrupt:
        pass
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
