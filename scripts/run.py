#!/usr/bin/env python

import argparse
import sys

import bin2raw
import copy_delayed_files
import generate_deploymentyaml
import init_deployment


def main(args):

    # initialize deployment directory structure
    init_deployment.main(args)

    # copy over delayed mode files
    if args.mode == "delayed":
        copy_delayed_files.main(args)

    # check if config files are present
    # TODO: add script to check for config files

    # create deployment yaml
    generate_deploymentyaml.main(args)

    # convert binary data to raw netcdfs
    bin2raw.main(args)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description=main.__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument(
        "deployments",
        nargs="+",
        help="Glider deployment name(s) formatted as glider-YYYYmmddTHHMM",
    )

    arg_parser.add_argument(
        "-m",
        "--mode",
        help="Dataset mode: real-time (rt) or delayed-mode (delayed)",
        choices=["rt", "delayed"],
        default="rt",
    )

    arg_parser.add_argument(
        "-c",
        "--compression",
        help="Compression mode: .*bd or .*cd",
        action="store_true",
    )

    arg_parser.add_argument(
        "-l",
        "--loglevel",
        help="Set the logging level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
    )

    args = arg_parser.parse_args()

    sys.exit(main(args))
