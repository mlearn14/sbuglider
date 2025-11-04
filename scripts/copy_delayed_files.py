#!/user/bin/env python

import argparse
import glob
import shutil
import sys
import os

import sbuglider.common as cf
from sbuglider.loggers import logfile_basename, setup_logger


def main(args):
    """Copy delayed mode binary files into its proper subdirectory"""
    deployment = args.deployment
    loglevel = args.loglevel.upper()
    compression = args.compression

    # set up the logger
    logfile_base = logfile_basename()
    logging_base = setup_logger("logging_base", loglevel, logfile_base)

    data_home = os.getenv("GLIDER_DATA_HOME")

    # get suffix
    if compression:
        flight_suffix = "*.dcd"
        sci_suffix = "*.ecd"
    else:
        flight_suffix = "*.dbd"
        sci_suffix = "*.ebd"

    # get binary file paths
    flight_dir = os.path.join(data_home, "raw", deployment, "flight", "logs")
    science_dir = os.path.join(data_home, "raw", deployment, "science", "logs")

    flight_files = glob.glob(os.path.join(flight_dir, flight_suffix))
    science_files = glob.glob(os.path.join(science_dir, sci_suffix))

    # get binary directory
    deployment_root = os.path.join(data_home, "deployments")
    deployment_dir = cf.find_glider_deployment_location(
        logging_base, deployment, deployment_root
    )
    binary_dir = os.path.join(deployment_dir, "data", "in", "binary", "debd")

    # copy files
    try:
        ffiles = [shutil.copy(f, binary_dir) for f in flight_files]
        sfiles = [shutil.copy(f, binary_dir) for f in science_files]
    except shutil.Error as e:
        logging_base.error(f"Error copying files: {e}")
        sys.exit(1)

    logging_base.info(
        f"Copied {len(ffiles)} flight and {len(sfiles)} science files from to {binary_dir}"
    )
    sys.exit(0)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description=main.__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument(
        "deployment",
        help="Glider deployment name formatted as glider-YYYYmmddTHHMM",
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

    main(args)
