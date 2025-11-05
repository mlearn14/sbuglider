#!/user/bin/env python

import argparse
import glob
import shutil
import sys
import os
from tabnanny import check

import sbuglider.common as cf
from sbuglider.loggers import logfile_basename, setup_logger


def _check_files(
    flight_dir, flight_suffix, science_dir, sci_suffix, logging
) -> tuple[list, list]:
    flight_files = glob.glob(os.path.join(flight_dir, flight_suffix))
    science_files = glob.glob(os.path.join(science_dir, sci_suffix))

    if len(flight_files) == 0 or len(science_files) == 0:
        logging.error(
            f"No {flight_suffix} or {sci_suffix} files found in {flight_dir} and {science_dir}"
        )
        return None
    else:
        logging.info(f"Found {len(flight_files)} flight files in {flight_dir}")
        logging.info(f"Found {len(science_files)} science files in {science_dir}")
        return flight_files, science_files


def main(args):
    """Copy delayed mode binary files into its proper subdirectory"""
    # FIXME: Add support for multiple deployments!!!
    deployments = args.deployments
    loglevel = args.loglevel.upper()
    compression = args.compression

    # set up the logger
    logfile_base = logfile_basename()
    logging_base = setup_logger("logging_base", loglevel, logfile_base)

    data_home = os.getenv("GLIDER_DATA_HOME")

    for deployment in deployments:
        flight_dir = os.path.join(data_home, "raw", deployment, "flight", "logs")
        science_dir = os.path.join(data_home, "raw", deployment, "science", "logs")

        # check if raw directories exist
        if not os.path.isdir(flight_dir):
            logging_base.error(f"Flight directory {flight_dir} not found")
        if not os.path.isdir(science_dir):
            logging_base.error(f"Science directory {science_dir} not found")

        # get suffixes
        u_flight_suffix = "*.dbd"
        u_sci_suffix = "*.ebd"

        # check if files exist
        if compression:
            flight_suffix = "*.dcd"
            sci_suffix = "*.ecd"
            flight_files, science_files = _check_files(
                flight_dir, flight_suffix, science_dir, sci_suffix, logging_base
            )
        else:
            flight_suffix = "*.dbd"
            sci_suffix = "*.ebd"
            flight_files, science_files = _check_files(
                flight_dir, flight_suffix, science_dir, sci_suffix, logging_base
            )

        # get binary directory
        deployment_root = os.path.join(data_home, "deployments")
        deployment_dir = cf.find_glider_deployment_location(
            logging_base, deployment, deployment_root
        )
        binary_dir = os.path.join(deployment_dir, "data", "in", "binary", "debd")

        # check if deployment directory exists
        if not os.path.isdir(deployment_dir):
            logging_base.error(f"Binary directory {deployment_dir} not found")

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
