#!/user/bin/env python

import argparse
import os
import sys

import pyglider.ncprocess as ncprocess
import pyglider.slocum as slocum
import sbuglider.common as cf
from sbuglider.loggers import logfile_basename, logfile_deploymentname, setup_logger


def main(args):
    """
    Convert binary slocum glider data into a raw netcdf timeseries.

    def main(deployments, mode, loglevel, test):
    """
    deployments: list[str] = args.deployments
    profile_filter_time: int = args.filt_time
    min_time: int = args.min_time
    min_samples: int = args.min_samples
    gap_threshold: float = args.gap_threshold
    loglevel: str = args.loglevel.upper()
    mode: str = args.mode.lower()
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

            if not os.path.isdir(outdir):
                logging_base.error(f"{deployment} output file data directory not found")
                continue

            if not os.path.isdir(os.path.join(deployment_location, "proc-logs")):
                logging_base.error(
                    f"{deployment} deployment proc-logs directory not found"
                )
                continue

            # set up logger
            logfilename = logfile_deploymentname(deployment, mode, "proc_bin2profiles")
            logFile = os.path.join(deployment_location, "proc-logs", logfilename)
            logging = setup_logger(__name__, loglevel, logFile)

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
                # profile_filter_time = 40
            elif mode == "delayed":
                scisuffix = "ebd"
                glidersuffix = "dbd"
                search = "*.[d|e]bd"
                # profile_filter_time = 40
            else:
                logging.warning(f"Invalid mode provided: {mode}")
                continue

            logging.info(f"Processing: {deployment}-{mode}")

            # convert binary *.T/EBD and *.S/DBD into *.t/ebd.nc and *.s/dbd.nc netcdf files.
            logging.info(
                f"Converting binary *.{scisuffix} and *.{glidersuffix} into *.{scisuffix}.nc and *.{glidersuffix}.nc netcdf files"
            )
            logging.info(f"Binary filepath: {binarydir}")
            logging.info(f"Cache filepath: {cacdir}")
            logging.info(f"Output filepath: {outdir}")

            # log the number of binary files to be converted
            scicount = len(
                [f for f in os.listdir(binarydir) if f.endswith(f".{scisuffix}")]
            )
            flightcount = len(
                [f for f in os.listdir(binarydir) if f.endswith(f".{glidersuffix}")]
            )

            # convert binary files and save to a temporary netcdf timeseries file
            outname, ds = slocum.binary_to_timeseries_new(
                binarydir,
                cacdir,
                outdir,
                deploymentyaml,
                search=search,
                profile_filt_time=profile_filter_time,
                profile_min_time=min_time,
                min_samples=min_samples,
                gap_threshold=gap_threshold,
                _log=logging,
            )

            # extract profiles from the temporary netcdf timeseries file
            ncprocess.extract_timeseries_profiles(
                outname, outdir, deploymentyaml, _log=logging
            )

            # delete the temporary netcdf timeseries file
            os.remove(outname)

            # log how many files were successfully converted from binary to *.nc
            ocount = len([f for f in os.listdir(outdir) if f.endswith(".nc")])
            logging.info(
                f"Successfully merged {scicount} science binary files and {flightcount} engineering binary files into {ocount} netcdf profiles"
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
        "-m",
        "--mode",
        help="Dataset mode: real-time (rt) or delayed-mode (delayed)",
        choices=["rt", "delayed"],
        default="rt",
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

    main(parsed_args)
