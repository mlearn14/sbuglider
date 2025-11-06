#!/usr/bin/env python

import argparse
import sys

from scripts import (
    init_deployment,
    copy_delayed_files,
    # copy_config_files,
    generate_deploymentyaml,
    bin2raw,
)


def main(args):

    # initialize deployment directory structure
    init_deployment.main(args)
    print("Deployment directory structure initialized.")

    # copy over delayed mode files
    if args.mode == "delayed":
        copy_delayed_files.main(args)
        print("Delayed mode files copied.")

    # check if config files are present
    # TODO: add script to check for config files

    # create deployment yaml
    generate_deploymentyaml.main(args)
    print("Deployment yaml created.")

    # convert binary data to raw netcdfs
    print("Converting binary data to raw netcdfs...", end=" ")
    bin2raw.main(args)
    print("Done!")

    # TODO: raw to trajectory?

    return 0


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

    arg_parser.add_argument(
        "-test",
        "--test",
        help="Point to the environment variable key GLIDER_DATA_HOME_TEST for testing.",
        action="store_true",
    )

    args = arg_parser.parse_args()

    sys.exit(main(args))
