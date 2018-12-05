"""
Compress NEMO netCDF4 output files.
"""
import os
import argparse
import subprocess
import netCDF4


def create_directory(path):
    """
    Create a directory on disk

    Raises IOError if a file with the same name already exists.
    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise IOError('file with same name exists', path)
    else:
        os.makedirs(path)
    return path


def compare_netcdf_files(one, two):
    """
    Check that both files contain the same fiels and metadata
    """
    with netCDF4.Dataset(one, 'r') as nc1:
        with netCDF4.Dataset(two, 'r') as nc2:
            vars1 = nc1.variables.keys()
            vars2 = nc2.variables.keys()
            msg = 'Mismatching variables in files {:} and {:}:\n\
                {:} {:}'.format(one, two, vars1, vars2)
            assert vars1 == vars2, msg
            for varname in vars1:
                s1 = nc1.variables[varname].shape
                s2 = nc2.variables[varname].shape
                msg = 'Variable shape mismatch in files {:} and {:}:\n\
                    {:} {:}'.format(one, two, s1, s2)
                assert s1 == s2, msg
            meta1 = nc1.ncattrs()
            meta2 = nc2.ncattrs()
            msg = 'Attribute mismatch in files {:} and {:}:\n\
                {:} {:}'.format(one, two, meta1, meta2)
            assert meta1 == meta2, msg


def compress_file(source_file, outputdir, comp_opts, delete_src=False, verbose=0):
    """
    Compress netCDF file with given options
    """
    create_directory(outputdir)
    inputdir, fname = os.path.split(source_file)
    target_file = os.path.join(outputdir, fname)
    assert os.path.isfile(source_file), \
        'File not found: {:}'.format(source_file)
    cmd = ['nccopy']
    cmd.append(comp_opts)
    cmd.append(source_file)
    cmd.append(target_file)
    if verbose > 0:
        print('Excecuting "{:}"'.format(' '.join(cmd)))
    try:
        subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise(e)

    if verbose > 1:
        print('Comparing files: {:} {:}'.format(source_file, target_file))
    compare_netcdf_files(source_file, target_file)
    if verbose > 1:
        print('  Success.')
    if delete_src:
        if verbose > 0:
            print('Removing "{:}"'.format(source_file))
        os.remove(source_file)


def process_files(files, outputdir, comp_opts, delete_src=False, verbose=0):
    """
    Process all given files
    """
    for f in files:
        compress_file(f, outputdir, comp_opts,
                      delete_src=delete_src, verbose=verbose)


def process_args():
    parser = argparse.ArgumentParser(
        description='Compress NEMO netCDF output files.\n\
        Compresses all given files and saves them in output directory with the\
        same filename.',
        # includes default values in help entries
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('output_directory', metavar='ODIR',
                        help='directory where the compressed files are stored')
    parser.add_argument('files', metavar='FILE', nargs='+',
                        help='a netCDF file to process')
    parser.add_argument('-D', '--delete-source', action='store_true',
                        help='Delete source netCDF file once compression')
    parser.add_argument('-s', '--compression-options', metavar='OPT',
                        default='-d1',
                        help='netCDF compression options in a string. \
                        E.g "-d1 -c x/12,y/12,deptht/56,time_counter/1"')
    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='increase output verbosity')
    args = parser.parse_args()

    process_files(args.files, args.output_directory,
                  args.compression_options, delete_src=args.delete_source,
                  verbose=args.verbosity)


if __name__ == '__main__':
    process_args()
