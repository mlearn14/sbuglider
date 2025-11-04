#!/user/bin/env python

import argparse
import os
import sys

import pyglider.ncprocess as ncprocess
import pyglider.slocum as slocum
import pyglider.utils as pgutils
import sbuglider.common as cf
from sbuglider.loggers import logfile_basename, logfile_deploymentname, setup_logger


def main(args):
    """
    Convert binary slocum glider data into raw netcdf profiles.

    def main(deployments, mode, loglevel, test):
    """
    deployments: list[str] = args.deployments
    loglevel: str = args.loglevel.upper()
    mode: str = args.mode.lower()
    compression: bool = args.compression
    test: bool = args.test

    # set up the logger
    logfile_base = logfile_basename()
    logging_base = setup_logger("logging_base", loglevel, logfile_base)

    # get the deployment and cache directories
    data_home, deployments_root = cf.find_glider_deployments_rootdir(logging_base, test)
    cacdir = os.path.join(data_home, "cac")
    if not os.path.isdir(cacdir):
        logging_base.error(f"cache file directory not found: {cacdir}")

    if isinstance(deployments_root, str):

        for deployment in deployments:

            # find the deployment binary data filepath
            binarydir, rawncdir, outdir, deployment_location = (
                cf.find_glider_deployment_datapath(
                    logging_base, deployment, deployments_root, mode
                )
            )

            # check if binarydir, rawncdir, deployment_location exist
            if not os.path.isdir(binarydir):
                logging_base.error(f"{deployment} binary file data directory not found")
                continue

            if not os.path.isdir(rawncdir):
                logging_base.error(
                    f"{deployment} raw NetCDF output file data directory not found"
                )
                continue

            if not os.path.isdir(os.path.join(deployment_location, "proc-logs")):
                logging_base.error(
                    f"{deployment} deployment proc-logs directory not found"
                )
                continue

            # set up logger
            logfilename = logfile_deploymentname(
                deployment, mode, "proc_binary_to_rawnc"
            )
            logFile = os.path.join(deployment_location, "proc-logs", logfilename)
            logging = setup_logger("logging", loglevel, logFile)

            # Set the deployment configuration path
            deployment_config_root = os.path.join(deployment_location, "config", "proc")
            if not os.path.isdir(deployment_config_root):
                logging.warning(
                    f"Invalid deployment config root: {deployment_config_root}"
                )

            # Find metadata files
            deploymentyaml = os.path.join(deployment_config_root, "deployment.yml")
            if not os.path.isfile(deploymentyaml):
                logging.warning(f"Invalid deployment.yaml file: {deploymentyaml}")

            # Find sensor list for processing binary files
            sensorlist = os.path.join(deployment_config_root, "sensors.txt")
            if not os.path.isfile(sensorlist):
                logging.warning(f"Invalid sensors.txt file: {sensorlist}")

            if mode == "rt":
                scisuffix = "tbd"
                glidersuffix = "sbd"
                search = "*.[s|t]bd"
            elif mode == "delayed":
                scisuffix = "ebd"
                glidersuffix = "dbd"
                search = "*.[d|e]bd"
            else:
                logging.warning(f"Invalid mode provided: {mode}")
                continue

            if compression:
                scisuffix = scisuffix.replace("b", "c")
                glidersuffix = glidersuffix.replace("b", "c")
                search = search.replace("b", "c")

            logging.info(f"Processing: {deployment}-{mode}")

            # convert binary *.T/EBD and *.S/DBD into *.t/ebd.nc and *.s/dbd.nc netcdf files.
            logging.info(
                f"Converting binary {search} into merged *.nc netcdf files"
            )
            logging.info(f"Binary filepath: {binarydir}")
            logging.info(f"Cache filepath: {cacdir}")
            logging.info(f"Output filepath: {rawncdir}")

            # log the number of binary files to be converted
            scicount = len(
                [f for f in os.listdir(binarydir) if f.endswith(f".{scisuffix}")]
            )
            flightcount = len(
                [f for f in os.listdir(binarydir) if f.endswith(f".{glidersuffix}")]
            )

            slocum.binary_to_profiles(
                indir=binarydir,
                cachedir=cacdir,
                outdir=rawncdir,
                deploymentyaml=deploymentyaml,
                search=search,
            )

            # log how many files were successfully converted from binary to *.nc
            ocount = len([f for f in os.listdir(rawncdir) if f.endswith(".nc")])
            logging.info(
                f"Successfully merged {scicount} science binary files and {flightcount} engineering binary files into {ocount} raw netcdf files"
            )
            logging.info(f"Finished converting binary files to raw netcdf files")


if __name__ == "__main__":
    # deploy = 'ru39-20250423T1535'  #  ru44-20250306T0038 ru44-20250325T0438 ru39-20250423T1535
    # mode = 'delayed'  # delayed rt
    # ll = 'info'
    # test = True
    # main(deploy, mode, ll, test)
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
        help="Verbosity level",
        type=str,
        choices=["debug", "info", "warning", "error"],
        default="info",
    )

    arg_parser.add_argument(
        "-test",
        "--test",
        help="Point to the environment variable key GLIDER_DATA_HOME_TEST for testing.",
        action="store_true",
    )

    parsed_args = arg_parser.parse_args()

    sys.exit(main(parsed_args))
