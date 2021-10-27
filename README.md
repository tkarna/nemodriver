# nemodriver

Scripts to run NEMO ocean model simulations

## Monthly driver

Scripts are found under `monthly_driver` subdirectory.

- `run_month.sh`: creates a run directory for a 1-month run and submits it in the queue
- `run_all.sh`: queues a sequence of 1-month runs as defined in the `env_path.sh` file
- `env_path.sh`: environment variables to define a NEMO run configuration and dates

## Typical usage:

### Execute a single 1-month simulation

Define parameters in the `env_path.sh` for the model configuration.

```
./run_month.sh -s 2014-10
```
Execute `./run_month.sh -h` for more options.

This creates a directory for the NEMO run, `$RUN_ROOT_DIR/run_2014-10`, where `RUN_ROOT_DIR` is a user-defined directory, e.g. `../../run01`.
It copies binary input files from the directory `CFG_TEMPLATE_DIR` to the run directory. It also generates NEMO namelists based on the user-defined namelist template. The template is defined by `NMLCONFIG` and the template namelist files are located under `template/namelist/$NMLCONFIG` directory.

By default, the system uses the `slurm` queue manager. The template for the job submission script is `monthly_driver/job_nemo.slurm`. The system also queues a post-processing job that is run after the NEMO run has (successfully) finished; the template is `monthly_driver/job_postproc.slurm`.

### Queue a sequence of 1-month runs

```
./run_all.sh
```

This runs a sequence of 1-month runs, as defined by the `start_date` and `end_date` environment variables. If the `start_date` coincides with `init_date`, the simulation will be initialsed from a cold start (`HOTSTART=0`) or from restart files (`HOTSTART=1`, restart files sought under `HOTSTART_DIR`). Otherwise, the simulation will be hotstarted from the previous month.


## Environment variables in `env_path.sh`

- `RUNTAG`: a short human-readable name for the simulation, e.g. `run01`. Should not contain spaces or underscores.
- `RUN_ROOT_DIR`: directory under which the monthly subdiretories will be created. Default: `../../$RUNTAG`
- `RUNDIR_PREFIX`: prefix to be used in run directory names. The monthly subdirectories are called `${RUNDIR_PREFIX}_2016-06`. Default: `run`.
- `CFG_TEMPLATE_DIR`: directory that contains all the binary etc files necessary for running the simulation. This includes netCDF files, forcing files, `*.xml` files, as well as NEMO and XIOS binaries. NOTE: the Fortran namelist files should **not** be in this directory.
- `NMLCONFIG`: name of the namelist template to use. The actual template namelist file are stored in `template/namelist/$NMLCONFIG` directory.
- `start_date`, `end_date`: Dates defining the first/last months of the simulation, e.g. `2014-10-01` and `2015-03-01` defines a 6 month run. NOTE: the day digit has no effect, i.e. only year and month counts.
- `init_date`: Defines the date for cold/hot start.
- `HOTSTART`: if `1` will use hot start from restart files.
- `HOTSTART_DIR`: directory where restart files are sought
- `MASTER_PARENT_JOB`: Slurm job ID. If defined, will wait for this job to finish before starting the first run.
- `SINGLE_NML`: If `1` will use a single namelist file for NEMO, i.e. the `namelist_cfg` files will be empty and all the parameters are defined in `namelist_ref`
- `QUEUE_MANAGER`: chooses the queue manager for the computing cluster, either `slurm` or `pbs`.
- `FLAG_WAVE` etc: additional namelist parameters that will be substituted to the nameslist files.

## Namelist templates

Templates are defined in `template/namelist/$NMLCONFIG` directory. It contains files:

- `namelist_ref`
- `namelist_ice_ref`
- `namelist_cfg`
- `namelist_ice_cfg`

The namelist files contain the parameters for the said configuration.

Some parameters can be set dynamically. Those parameters contain tags identified with double underscores:
```
   nn_itend    = __NTIMESTEP__ !  last  time step (std 29760)
   nn_date0    = __INITDATE__ !  date at nit_0000 (format yyyymmdd) used if ln_rstart=F or (ln_rstart=T and nn_rstctl=0 or 1)

```
These values will be substituted by the `run_month.sh` script.

If `SINGLE_NML` is `1`, the `*_cfg` files are empty and all substitutions are made to the `*_ref` files directly. If not, the replacements are made to the `*_cfg` files.
