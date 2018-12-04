"""
Create symlinks for NEMO restart files
"""
import os
import glob

in_dir = 'output/restarts/'
out_dir = 'tmp'
input_name = 'restart_out'
output_name = 'restart_in'


def symlink_restart_files(in_dir, input_name, out_dir, output_name):
    """
    Link the latest restart files from input dir to output in_dir.

    Will create symbolic links with a relative path.

    {out_dir}/{output_name}_0180.nc -> {in_dir}/NORDIC_00001920_{input_name}_0180.nc

    """

    # find lastest file for proc 0
    # {in_dir}/*{in_name}*_0000.nc
    zero_pattern = os.path.join(in_dir, '*{:}*_0000.nc'.format(input_name))
    last_zero_file = sorted(glob.glob(zero_pattern))[-1]

    # seach pattern for the latest restart files
    # in_dir/NORDIC_00001920_restart_out_*.nc
    pattern = last_zero_file.replace('_0000.nc', '_*.nc')
    files = glob.glob(pattern)
    # drop path
    files = [os.path.split(f)[1] for f in files]


    def gen_output_file(output_name, proc):
        return '{:}_{:}.nc'.format(output_name, proc)


    for f in files:
        # parse processor index
        proc = os.path.splitext(f)[0].split('_')[-1]
        o = gen_output_file(output_name, proc)
        rel_path = os.path.relpath(in_dir, out_dir)
        source = os.path.join(rel_path, f)
        link_name = os.path.join(out_dir, o)
        print('creating link: {:} -> {:}'.format(link_name, source))
        os.symlink(source, link_name)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Create symlinks for NEMO restart files.'
    )

    parser.add_argument('input_dir', help='Source directory')
    parser.add_argument('output_dir', help='Target directory')
    parser.add_argument('input_suffix', help='Restart file suffix')
    parser.add_argument('output_suffix', help='Restart file suffix for link files')

    args = parser.parse_args()

    symlink_restart_files(args.input_dir, args.input_suffix,
                          args.output_dir, args.output_suffix)

