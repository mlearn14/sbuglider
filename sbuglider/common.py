#!/usr/bin/env python

from dateutil import parser
import os
import logging
import pytz
import re
import subprocess

from netCDF4 import default_fillvals
from netCDF4 import num2date
import pandas as pd
import xarray as xr


def convert_epoch_ts(data):
    """Converts a time variable to a datetime object."""
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/common.py
    if isinstance(data, xr.core.dataarray.DataArray):
        time = pd.to_datetime(
            num2date(data.values, data.units, only_use_cftime_datetimes=False)
        )
    elif isinstance(data, pd.core.indexes.base.Index):
        time = pd.to_datetime(
            num2date(
                data,
                "seconds since 1970-01-01T00:00:00Z",
                only_use_cftime_datetimes=False,
            )
        )
    elif isinstance(data, pd.core.indexes.datetimes.DatetimeIndex):
        time = pd.to_datetime(
            num2date(
                data,
                "seconds since 1970-01-01T00:00:00Z",
                only_use_cftime_datetimes=False,
            )
        )

    return time


def decompress_dbds(
    logger,
    indir,
    suffix=".*cd",
    outdir=None,
    script="/home/gsb/projects/slocum/bin2ascii/decompress_dbds.sh",
):
    """
    Decompresses each dinkum compressed data (*.*cd) file in the provided directory. Each decompressed file is written to the same directory unless specified.

    Calls John Kerfoot's decompress_dbds.sh script.

    Parameters
    ----------
        logger (Logger): logger object
        indir (str): input directory
        suffix (str): file suffix
        outdir (str): output directory
        script (str): absolute path to decompress_dbds.sh
    """
    repo_root = os.path.dirname(os.path.dirname(script))
    script_relpath = os.path.relpath(script, repo_root)

    if outdir is None:
        outdir = indir

    cmd = f"{script_relpath} -o {outdir} {indir}/*{suffix}"
    result = subprocess.run(
        cmd,
        cwd=repo_root,
        shell=True,
        capture_output=True,
        text=True,
    )

    logger.info(f"stdout: {result.stdout}")
    logger.error(f"stderr: {result.stderr}")
    if result.returncode != 0:
        logger.error(f"Decompression failed with code {result.returncode}")
    else:
        logger.info("Decompression completed successfully.")


def find_glider_deployment_datapath(
    logger, deployment, deployments_root, mode
) -> tuple[str, str, str, str]:
    """
    Find the glider deployment binary data path.

    Parameters
    ----------
        logger (Logger): logger object
        deployment (str): glider deployment/trajectory name e.g. ru44-20250306T0038
        deployments_root (str): root directory for glider deployments
    Returns
    ----------
        data_path (str): glider deployment binary data path
        nc_outpath (str): glider deployment raw netcdf output path
        outdir (str): output directory for data queued for qc processing
        deployment_location (str): fully qualified path to the deployment directory location
    """
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/common.py

    # Pre-compile regex pattern to extract glider and trajectory from deployment name
    glider_regex = re.compile(r"^(.*)-(\d{8}T\d{4})")

    # Extract glider and trajectory from deployment name
    match = glider_regex.search(deployment)
    if match:
        glider, trajectory = match.groups()

        # Parse trajectory date
        try:
            # Convert trajectory string into a datetime object
            trajectory_dt = parser.parse(trajectory).replace(tzinfo=pytz.UTC)
        except ValueError as e:
            logger.error(f"Error parsing trajectory date {deployment}: {e}")
            return None, None, None, None

        # Create fully-qualified path to the deployment location
        deployment_year = "{:0.0f}".format(trajectory_dt.year)
        deployment_location = os.path.join(
            deployments_root, deployment_year, deployment
        )

        # Set the deployment binary data path
        if mode == "delayed":
            modemap = "debd"
        elif mode == "rt":
            modemap = "stbd"
        else:
            logger.warning(f"{deployment} invalid mode provided: {mode}")
            return None, None, None, None

        # Create fully-qualified path to the binary data
        data_path = os.path.join(deployment_location, "data", "in", "binary", modemap)

        # Check if directory exists
        if not os.path.isdir(data_path):
            logger.warning(f"{deployment} data directory not found: {data_path}")
            return None, None, None, None

        # Set the deployment raw netcdf data path
        nc_outpath = os.path.join(deployment_location, "data", "in", "rawnc", modemap)

        # Set the deployment output file directory
        outdir = os.path.join(deployment_location, "data", "out", mode, "qc_queue")

        return data_path, nc_outpath, outdir, deployment_location
    else:
        logger.error(f"Cannot pull glider name from {deployment}")
        return None, None, None, None


def find_glider_deployment_location(logger, deployment, deployments_root):
    """
    Find the glider deployment location.

    Parameters
    ----------
        logger (Logger): logger object.
        deployment (str): glider deployment/trajectory name e.g. ru44-20250306T0038.
        deployments_root (str): root directory for glider deployments.
    Returns
    ----------
        - deployment_location (str): glider deployment location.
    """
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/common.py
    glider_regex = re.compile(r"^(.*)-(\d{8}T\d{4})")
    match = glider_regex.search(deployment)
    if match:
        # Parse trajectory date
        try:
            glider, trajectory = match.groups()
            try:
                trajectory_dt = parser.parse(trajectory).replace(tzinfo=pytz.UTC)
            except ValueError as e:
                logger.error(
                    "Error parsing trajectory date {:s}: {:}".format(trajectory, e)
                )
                return None

            deployment_year = "{:0.0f}".format(trajectory_dt.year)

            # Create fully-qualified path to the deployment location
            deployment_location = os.path.join(
                deployments_root, deployment_year, deployment
            )

            # Check if directory exists
            if os.path.isdir(deployment_location):
                logger.debug(f"Deployment location found: {deployment_location}")
            else:
                logger.warning(
                    f"Deployment location does not exist: {deployment_location}"
                )
                return None

        except ValueError as e:
            logger.error(f"Error parsing invalid deployment name {deployment}: {e}")
            return None
    else:
        logger.error(f"Cannot pull glider name from {deployment}")
        return None

    return deployment_location


def find_glider_deployments_rootdir(
    logger: logging.Logger, test: bool
) -> tuple[str, str]:
    """
    Returns the glider deployment directory from the environment variable *$GLIDER_DATA_HOME* as well as the environment variable itself.

    Returns
    ----------
        data_home (str): The environment variable *$GLIDER_DATA_HOME*.
        deployments_root (str): Root directory for glider deployments.
    """
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/common.py
    # Find the glider deployments root directory
    if test:
        envvar = "GLIDER_DATA_HOME_TEST"
    else:
        envvar = "GLIDER_DATA_HOME"

    data_home = os.getenv(envvar)

    if not data_home:
        logger.error("{:s} not set".format(envvar))
        return 1, 1
    elif not os.path.isdir(data_home):
        logger.error("Invalid {:s}: {:s}".format(envvar, data_home))
        return 1, 1

    deployments_root = os.path.join(data_home, "deployments")
    if not os.path.isdir(deployments_root):
        logger.warning("Invalid deployments root: {:s}".format(deployments_root))
        return 1, 1

    return data_home, deployments_root


def return_season(ts):
    """Returns the season for a given datetime object."""
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/common.py
    if ts.month in [12, 1, 2]:
        season = "DJF"
    elif ts.month in [3, 4, 5]:
        season = "MAM"
    elif ts.month in [6, 7, 8]:
        season = "JJA"
    elif ts.month in [9, 10, 11]:
        season = "SON"

    return season


def set_encoding(data_array, original_encoding=None):
    """
    Define encoding for a data array, using the original encoding from another variable (if applicable).

    Parameters
    ----------
        data_array (xarray.DataArray): data array to which encoding is added
        original_encoding (dict): optional encoding dictionary from the parent variable (e.g. use the encoding from "depth" for the new depth_interpolated variable)
    """
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/common.py
    if original_encoding:
        data_array.encoding = original_encoding

    try:
        encoding_dtype = data_array.encoding["dtype"]
    except KeyError:
        data_array.encoding["dtype"] = data_array.dtype

    try:
        encoding_fillvalue = data_array.encoding["_FillValue"]
    except KeyError:
        # set the fill value using netCDF4.default_fillvals
        data_type = f"{data_array.dtype.kind}{data_array.dtype.itemsize}"
        data_array.encoding["_FillValue"] = default_fillvals[data_type]
