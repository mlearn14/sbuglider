#!/usr/bin/env python

import argparse
import sys

from scripts import (
    bin2timeseries,
    init_deployment,
    copy_delayed_files,
    check_config_files,
    generate_deploymentyaml,
)


def main(args):

    # initialize deployment directory structure
    init_deployment.main(args)
    print("Deployment directory structure initialized.")

    # copy over delayed mode files
    # TODO: handle real-time compressed files
    if args.mode == "delayed":
        # the decompression step isn't really necessary with this version, but it's here in case other functions are added.
        print("Decompressing delayed mode binary files...", end=" ")
        copy_delayed_files.main(args)
        print("Done!")

    # check if config files are present
    check_config_files.main(args)
    print("Config files copied and confirmed.")

    # create deployment yaml
    generate_deploymentyaml.main(args)
    print("Deployment yaml created.")

    # convert binary data to raw netcdfs
    print("Converting binary data to raw netcdfs...", end=" ", flush=True)
    bin2timeseries.main(args)
    print("Done!")

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
        "-f",
        "--filt_time",
        help="Profile filter time in seconds",
        type=int,
        default=40,
    )

    arg_parser.add_argument(
        "-mt",
        "--min_time",
        help="Minimum profile time in seconds",
        type=int,
        default=120,
    )

    arg_parser.add_argument(
        "-ms",
        "--min_samples",
        help="Minimum samples to be included in a profile",
        type=int,
        default=75,
    )

    arg_parser.add_argument(
        "-gt",
        "--gap_threshold",
        help="Minimum gap in seconds in a profile to be considered a gap",
        type=int,
        default=30,
    )

    arg_parser.add_argument(
        "-test",
        "--test",
        help="Point to the environment variable key GLIDER_DATA_HOME_TEST for testing.",
        action="store_true",
    )

    args = arg_parser.parse_args()

    sys.exit(main(args))
