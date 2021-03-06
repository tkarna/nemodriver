"""
Compute required number of time steps for a NEMO run.
"""
import datetime
import os
import dateutil.parser
import numpy


def parse_namelist(infile, key, convert_func=float, run_dir=None):
    """
    Parses a keyword from f90 namelist
    """
    value = None
    filename = infile if run_dir is None else os.path.join(run_dir, infile)
    with open(filename, 'r') as f:
        for line in f.readlines():
            words = line.split()
            if len(words) > 2 and words[0] == key:
                value = convert_func(words[2])
    assert value is not None, '{:} not found in {:}'.format(key, filename)
    return value


def parse_namelist_with_cfg(infile_ref, infile_cfg, key, convert_func=float,
                            run_dir=None):
    """
    Parses a keyword from cfg and ref namelist
    """
    _ref = infile_ref if run_dir is None else os.path.join(run_dir, infile_ref)
    _cfg = infile_cfg if run_dir is None else os.path.join(run_dir, infile_cfg)
    try:
        value = parse_namelist(_cfg, key, convert_func=convert_func)
    except (AssertionError, IndexError):
        value = parse_namelist(_ref, key, convert_func=convert_func)
    return value


def parse_timestep(infile='namelist_ref', infile_cfg='namelist_cfg',
                   run_dir=None):
    """
    Parses 3D time step from NEMO namelist file
    """
    val = None
    for key in ['rn_rdt', 'rn_Dt']:
        try:
            val = parse_namelist_with_cfg(infile, infile_cfg, key,
                                          convert_func=float, run_dir=run_dir)
        except (AssertionError, IndexError):
            pass
        if val is not None:
            continue
    assert val is not None, 'Could not parse time step from {:}'.format(infile)
    return val


def compute_ntimesteps(starttime, endtime, timestep):
    if timestep is None:
        timestep = parse_timestep()

    ntime = int(numpy.ceil((endtime - starttime).total_seconds()/timestep))
    return ntime


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Compute number of time steps for a NEMO run.'
    )

    parser.add_argument('starttime', help='Start time of the run')
    parser.add_argument('endtime', help='Start time of the run')
    parser.add_argument('--timestep', type=int, help='Model time step')

    args = parser.parse_args()

    starttime = dateutil.parser.parse(args.starttime)
    endtime = dateutil.parser.parse(args.endtime)
    timestep = args.timestep

    ntime = compute_ntimesteps(starttime, endtime, timestep)
    print(ntime)

