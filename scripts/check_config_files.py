#!/usr/bin/env python

import argparse
import glob
import os
import shutil
import subprocess
import sys

from sbuglider.loggers import logfile_basename, setup_logger


def main(args):
    """Copy config files into deployment config directory"""
    deployments = args.deployments
    loglevel = args.loglevel.upper()

    # set up the logger
    logfile_base = logfile_basename()
    logging_base = setup_logger("logging_base", loglevel, logfile_base)

    data_home = os.getenv("GLIDER_DATA_HOME")
    config_home = os.getenv("GLIDER_CONFIG_HOME")

    if not data_home:
        logging_base.error("GLIDER_DATA_HOME not set")
        sys.exit(1)
    elif not os.path.isdir(data_home):
        logging_base.error("Invalid GLIDER_DATA_HOME: " + data_home)
        sys.exit(1)

    if not config_home:
        logging_base.error("GLIDER_CONFIG_HOME not set")
        sys.exit(1)
    elif not os.path.isdir(config_home):
        logging_base.error("Invalid GLIDER_CONFIG_HOME: " + config_home)
        sys.exit(1)

    for deployment in deployments:
        glider_name = deployment.split("-")[0]
        year = deployment.split("-")[1][:4]

        # check if config root directory and files exist
        indir = os.path.join(config_home, glider_name)
        if not os.path.isdir(indir):
            logging_base.error(f"Template config directory {indir} not found")
            sys.exit(1)

        # check if deployment config directory exists
        outdir = os.path.join(
            data_home, "deployments", year, deployment, "config", "proc"
        )
        if not os.path.isdir(outdir):
            logging_base.error(f"Deployment config directory {outdir} not found")
            sys.exit(1)

        filenames = os.path.join(indir, "*")
        files = glob.glob(filenames)

        try:
            [shutil.copy(f, outdir) for f in files]
        except Exception as e:
            logging_base.error(f"Error copying config files: {e}")
            sys.exit(1)

    # Confirmation step to make user sure that all config files are correct.
    for deployment in deployments:
        glider_name = deployment.split("-")[0]
        year = deployment.split("-")[1][:4]
        outdir = os.path.join(
            data_home, "deployments", year, deployment, "config", "proc"
        )
        subprocess.Popen(["xdg-open", outdir])  # linux specific!

        response = input(
            f"Are the config files for {deployment} correct? (y/n): "
        ).lower()
        if response != "y":
            logging_base.error(f"USER EXIT: Config files for {deployment} not correct.")
            sys.exit(1)

        logging_base.info(f"Config files for {deployment} correct.")

    logging_base.info("User confirmed all config files are correct.")


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
