#!/usr/bin/env python

import argparse
import os
import sys

from sbuglider.loggers import logfile_basename, setup_logger

# TODO: add env variable for template config file locations.


def main(args):
    deployments = args.deployments
    loglevel = args.loglevel.upper()

    # set up the logger
    logfile_base = logfile_basename()
    logging_base = setup_logger("logging_base", loglevel, logfile_base)

    data_home = os.getenv("GLIDER_DATA_HOME")

    for deployment in deployments:
        # TODO: Add check for template config directory and files from env variable
        glider_name = deployment.split("-")[0]

        config_dir = os.path.join(
            data_home, "deployments", deployment, "config", "proc"
        )
        if not os.path.isdir(config_dir):
            logging_base.error(f"Config directory {config_dir} not found")
            sys.exit(1)

        # TODO: copy files over

    # TODO: end of function. Add confirmation step to make user sure that all config files are correct.
    for deployment in deployments:
        pass  # confirmation step goes here!


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
