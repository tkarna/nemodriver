"""
Create symlinks for NEMO restart files.

Usage:
python link_restart_files.py ../run00/restarts/ initialstate/ restart_out restart_in

"""
import os
import glob


def create_link(src, dst, force=False):
    """
    Create a symbolic link.

    If force is True, the existing dst will be removed, if any.
    """

    if force and (os.path.isfile(dst) or os.path.islink(dst)):
        os.remove(dst)
    print('creating link: {:} -> {:}'.format(dst, src))
    os.symlink(src, dst)


def symlink_restart_files(in_dir, input_name, out_dir, output_name):
    """
    Link the latest restart files from input dir to output in_dir.

    Will create symbolic links with a relative path.

    If a single restart file, {out_dir}/{output_name}.nc exists, will link:
    {out_dir}/{output_name}.nc -> {in_dir}/{input_name}.nc

    Otherwise links local-by-process restart files:
    {out_dir}/{output_name}_0180.nc -> {in_dir}/NORDIC_00001920_{input_name}_0180.nc

    """
    # check if single target restart file exists
    a = os.path.join(in_dir, output_name + '.nc')
    b = os.path.join(in_dir, input_name + '.nc')
    for source in [a, b]:
        if os.path.isfile(source) or os.path.islink(source):
            link_name = os.path.join(out_dir, os.path.split(source)[1])
            create_link(source, link_name, force=True)
            return

    # find lastest file for proc 0
    # {in_dir}/*{in_name}*_0000.nc
    zero_pattern = os.path.join(in_dir, '*{:}*_0000.nc'.format(input_name))
    files = glob.glob(zero_pattern)
    assert len(files) > 0, 'No files found: "{:}"'.format(zero_pattern)
    last_zero_file = sorted(files)[-1]

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
        create_link(source, link_name, force=True)


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

