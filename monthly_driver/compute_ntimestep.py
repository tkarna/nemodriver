"""
Compute required number of time steps for a NEMO run.
"""
import datetime
import os
import dateutil.parser
import numpy


def parse_namelist(infile, key, convert_func=float):
    """
    Parses a keyword from f90 namelist
    """
    value = None
    assert os.path.getsize(infile) > 0, 'File {:} is empty'.format(infile)
    with open(infile, 'r') as f:
        for line in f.readlines():
            words = line.split()
            if len(words) > 2 and words[0] == key:
                value = convert_func(words[2])
    assert value is not None, '{:} not found in {:}'.format(infile)
    return value


def parse_namelist_with_cfg(infile_ref, infile_cfg, key, convert_func=float):
    """
    Parses a keyword from cfg and ref namelist
    """
    try:
        value = parse_namelist(infile_cfg, key, convert_func=convert_func)
    except AssertionError:
        value = parse_namelist(infile_ref, key, convert_func=convert_func)
    return value


def parse_timestep(infile='namelist_ref', infile_cfg='namelist_cfg'):
    """
    Parses 3D time step from NEMO namelist file
    """
    return parse_namelist_with_cfg(infile, infile_cfg, 'rn_rdt', float)


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

