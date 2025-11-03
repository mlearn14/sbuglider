#!/usr/bin/env python

import os
import pwd
from datetime import datetime
import logging


def logfile_basename() -> str:
    """Returns the base qc log file name."""
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/loggers.py
    user: str = pwd.getpwuid(os.getuid())[0]
    return f"/home/SOMAS_Glider/logs/{user}-glider_qc.log"


def logfile_deploymentname(deployment: str, mode: str, fname: str) -> str:
    """Returns the deployment proc-log file name."""
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/loggers.py
    user: str = pwd.getpwuid(os.getuid())[0]
    return f"{user}-{datetime.now().strftime('%Y%m%d')}-{deployment}-{mode}-{fname}.log"


def setup_loggers(name: str, loglevel: str, logfile: str):
    """Sets up and retruns a foramtted logger object."""
    # originally written by lgarzio: https://github.com/lgarzio/ruglider_processing/blob/master/ruglider_processing/loggers.py
    logger = logging.getLogger(name)

    # if the logger doesn't already exist, set it up
    if not logger.handlers:
        log_format = logging.Formatter(
            "%(asctime)s%(module)s:%(levelname)s:%(message)s [line %(lineno)d]"
        )
        handler = logging.FileHandler(logfile)
        handler.setFormatter(log_format)

        log_level = getattr(logging, loglevel)
        logger.setLevel(log_level)
        logger.addHandler(handler)

    return logger
