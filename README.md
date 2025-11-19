# sbuglider

Collection of scripts to process raw slocum glider data into netcdf profiles using a forked version of [pyglider](https://github.com/c-proof/pyglider). Works for both real-time and delayed mode datasets.

## THIS REPOSITORY IS IN DEVELOPMENT! USE WITH CAUTION

## Acknowledgements

## Installation

1. Clone this repository: `git clone https://github.com/mlearn14/sbuglider.git`
2. Clone forked version of pyglider: `git clone https://github.com/mlearn14/pyglider.git`
3. Clone slocum repository: `git clone https://github.com/kerfoot/slocum.git`
4. Navigate to the cloned repo on your local machine: `cd sbuglider`
5. Create environment: `conda env create -f environment.yml`
6. Activate environment: `conda activate sbuglider`
7. Install local package to environment" `pip install .`
8. Navigate to local forked pyglider: `cd pyglider`
9. Install forked version of pyglider: `pip install .`
   * For an editable version: `pip install -e .`
10. Set environment variables
    1. Open ~/.bashrc: `nano ~/.bashrc`
    2. Add the following lines to the file, substituting appropriate paths inside the <>:
        * `export GLIDER_DATA_HOME="/home/<glider_user>/"`
        * `export GLIDER_CONFIG_HOME="/home/<glider_user>/config/"`
        * `export SLOCUM_EXE_ROOT="/<path>/slocum/linux-bin/"`
    3. Save and quit.
    4. Reload the shell `source ~/.bashrc`

## Deployment Directory Structure

```java
~/deployments/YYYY/glider-YYYYmmddTHHMM
├── config
│   ├── qc
│   └── proc
├── data
│   └── in 
│       └── binary
│           └── debd
│           └── stbd
│       └── rawnc
│           └── debd
│           └── stbd
│   └── out
│       └── delayed
│           └── qc_queue
│       └── rt
│           └── qc_queue
└── proc-logs
```

** Currently the rawnc subdirectory is unused, but this might change in future versions.

## Usage

The following may be done manually or by using the included processing script.

### Manual Method

1. Create the deployment directory structure as displayed above.
2. The following template [config files](https://github.com/mlearn14/sbuglider/tree/main/example_config) don't need modification but need to be in ../config/proc/
   * deployment-template.yml
   * sensor_defs-raw.json
   * sensor_defs-sci_profile.json
3. Generate the following [files](https://github.com/mlearn14/sbuglider/tree/main/example_config) based on the instruments that are installed on the glider and put them in ../config/proc/
   * instruments.json (using build_deployment_instrument_configurations.py not included in this package)
   * sensors.txt
4. Manually modify the [config files](https://github.com/mlearn14/sbuglider/tree/main/example_config) for the deployment and put them in ../config/proc/
   * deployment-globalattrs.yml
   * platform.yml
5. Once all of the config files are in ../config/proc/, run [generate_deploymentyaml.py](https://github.com/mlearn14/sbuglider/blob/main/scripts/generate_deploymentyaml.py) to create the deployment.yml file that is used to convert the raw glider data files to merged trajectory NetCDF files.

    `python -m scripts.generate_deploymentyaml glider-YYYYmmddTHHMM`

6. Run [bin2profiles.py](https://github.com/mlearn14/sbuglider/blob/main/scripts/bin2profiles.py) to convert realtime (-m rt) sbd/tbd binary files located in ../data/in/binary/stbd/ or delayed (-m delayed) dbd/ebd binary files located in ../data/in/binary/debd/ to NetCDF files (../data/out/delayed(rt)/qc_queue/) using [pyglider](https://pyglider.readthedocs.io/en/latest/pyglider/pyglider.html). This generates one file per glider profile, calculates basic science variables (e.g. depth, salinity, density), indexes glider profiles, and will generate a log file in ../proc-logs/.

    `python -m scripts.bin2profiles glider-YYYYmmddTHHMM -m delayed`

### Automated Method

1. Run the following [script](https://github.com/mlearn14/sbuglider/blob/main/run.py):

    `python run.py glider-YYYYmmddTHHMM -m delayed`

This script will create the deployment directory structure, move all raw files from ../raw/glider-YYYYmmddTHHMM/flight(science), decompress files if necessary, copy all template config files, and process the raw data into NetCDF profiles files.
