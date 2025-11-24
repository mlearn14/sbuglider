#!/user/bin/env python

import argparse
from dateutil import parser
import os
import pytz
import re
import sys

from sbuglider.loggers import logfile_basename, setup_logger


def main(args):
    """Initialize glider deployment(s)."""
    deployments = args.deployments
    loglevel = args.loglevel.upper()

    # set up the logger
    logfile_base = logfile_basename()
    logging_base = setup_logger("logging_base", loglevel, logfile_base)

    glider_regex = re.compile(r"^(.*)-(\d{8}T\d{4})")

    # find the glider deployments root directory
    data_home = os.getenv("GLIDER_DATA_HOME")

    if not data_home:
        logging_base.error("GLIDER_DATA_HOME not set")
        sys.exit(1)
    elif not os.path.isdir(data_home):
        logging_base.error(
            f"Invalid GLIDER_DATA_HOME: {data_home}. Be sure to create the directory '/home/SOMAS_Glider' and set the environment variable $GLIDER_DATA_HOME to it."
        )
        sys.exit(1)

    # create the deployment directory
    for deployment in deployments:
        deployment_root = os.path.join(data_home, "deployments")
        match = glider_regex.search(deployment)
        if match:
            glider, trajectory = match.groups()
            try:
                trajectory_dt = parser.parse(trajectory).replace(tzinfo=pytz.UTC)
            except ValueError as e:
                logging_base.error(
                    "Error parsing trajectory date {:s}: {:}".format(trajectory, e)
                )
                sys.exit(1)

            deployment_year = "{:0.0f}".format(trajectory_dt.year)

            deployment_dir = os.path.join(deployment_root, deployment_year, deployment)

            # get subdirectory paths
            config_dir = os.path.join(deployment_dir, "config", "proc")
            bin_stbd_dir = os.path.join(deployment_dir, "data", "in", "binary", "stbd")
            bin_debd_dir = os.path.join(deployment_dir, "data", "in", "binary", "debd")
            raw_stbd_dir = os.path.join(deployment_dir, "data", "in", "rawnc", "stbd")
            raw_debd_dir = os.path.join(deployment_dir, "data", "in", "rawnc", "debd")
            delayed_dir = os.path.join(
                deployment_dir, "data", "out", "delayed", "qc_queue"
            )
            rt_dir = os.path.join(deployment_dir, "data", "out", "rt", "qc_queue")
            proclog_dir = os.path.join(deployment_dir, "proc-logs")

            # create the deployment subdirectories
            try:
                os.makedirs(config_dir, exist_ok=True)
                os.makedirs(bin_stbd_dir, exist_ok=True)
                os.makedirs(bin_debd_dir, exist_ok=True)
                os.makedirs(raw_stbd_dir, exist_ok=True)
                os.makedirs(raw_debd_dir, exist_ok=True)
                os.makedirs(delayed_dir, exist_ok=True)
                os.makedirs(rt_dir, exist_ok=True)
                os.makedirs(proclog_dir, exist_ok=True)
            except OSError as e:
                logging_base.error(f"Error creating deployment subdirectories: {e}")
                sys.exit(1)

            logging_base.info(f"Initialized deployment: {deployment}")
        else:
            logging_base.error(f"Invalid deployment name: {deployment}")
            sys.exit(1)


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
        "-l",
        "--loglevel",
        help="Set the logging level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
    )

    args = arg_parser.parse_args()

    main(args)
