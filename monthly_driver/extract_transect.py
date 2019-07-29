import numpy
import netCDF4
import datetime
from dateutil.relativedelta import relativedelta


def extract_transect(infile, domainfile, ncvarname, transect_lonlat, outfile):
    """
    Extract a transect for the given netCDF file.

    :arg infile: input netCDF4 file containing Nemo 3D grid T field
    :arg domainfile: Nemo 4.0 domain_cfg.nc file
    :arg ncvarname: netCDF variable name to extract
    :arg transect_lonlat: transect coordinates in (npoints, 2) array
    :arg outfile: output filename
    """
    transect_lon = transect_lonlat[:, 0]
    transect_lat = transect_lonlat[:, 1]
    npoints = len(transect_lat)

    def _extract(src, var, ix_lon, ix_lat):
        src_var = src[var]
        ntime, nz, nlat, nlon = src_var.shape
        vals = numpy.zeros((ntime, nz, npoints))
        for i in range(ntime):
            tslice = src_var[i, ...]  # read to memory
            v = tslice[numpy.arange(nz)[:, numpy.newaxis],
                       ix_lat[numpy.newaxis, :],
                       ix_lon[numpy.newaxis, :]]
            vals[i, ...] = v
        return vals

    def _extract_2d(src, var, ix_lon, ix_lat):
        src_var = src[var]
        ntime, nlat, nlon = src_var.shape
        vals = numpy.zeros((ntime, npoints))
        for i in range(ntime):
            tslice = src_var[i, ...]  # read to memory
            v = tslice[ix_lat, ix_lon]
            vals[i, ...] = v
        return vals

    with netCDF4.Dataset(infile) as src, netCDF4.Dataset(outfile, 'w') as dst:
        # load lat, lon
        grid_lat = src['nav_lat'][:]
        grid_lon = src['nav_lon'][:]
        # collapse to 1d
        grid_lat = numpy.max(grid_lat, axis=1)
        grid_lon = numpy.max(grid_lon, axis=0)

        # find nearest neighbors
        nnix_lon = numpy.argmin(
            numpy.abs(grid_lon[:, numpy.newaxis] -
                      transect_lon[numpy.newaxis, :]), axis=0)
        nnix_lat = numpy.argmin(
            numpy.abs(grid_lat[:, numpy.newaxis] -
                      transect_lat[numpy.newaxis, :]), axis=0)
        # lon,lat of the actual nearest neighbors
        out_lon = grid_lon[nnix_lon]
        out_lat = grid_lon[nnix_lat]

        # write output
        nz = len(src['deptht'])
        dst.createDimension('time', None)
        dst.createDimension('depth', nz)
        dst.createDimension('bounds', 2)
        dst.createDimension('index', npoints)

        dst_lat = dst.createVariable('latitude', 'f', ('index', ))
        dst_lat.standard_name = 'latitude'
        dst_lat.units = 'degree'
        dst_lat[:] = out_lat
        dst_lon = dst.createVariable('longitude', 'f', ('index', ))
        dst_lon.standard_name = 'longitude'
        dst_lon.units = 'degree'
        dst_lon[:] = out_lon

        src_time = src['time_centered']
        dst_time = dst.createVariable('time', 'd', ('time', ))
        dst_time.standard_name = 'time'
        dst_time.units = src_time.units
        dst_time.calendar = src_time.calendar
        dst_time[:] = src_time[:]

        src_depth = src['deptht']
        depth0 = src_depth[:]
        dst_depth0 = dst.createVariable('depth0', 'f', ('depth', ))
        dst_depth0.standard_name = 'depth'
        dst_depth0.units = src_depth.units
        dst_depth0[:] = depth0

        # extract and store the variable
        vals = _extract(src, ncvarname, nnix_lon, nnix_lat)
        src_var = src[ncvarname]
        dst_var = dst.createVariable(ncvarname, 'f',
                                     ('time', 'depth', 'index', ))
        for key in src_var.ncattrs():
            dst_var.setncattr(key, src_var.getncattr(key))
        dst_var.setncattr('coordinates', 'time depth latitude longitude')
        dst_var[:] = vals

        # compute vertical coordinates
        with netCDF4.Dataset(domainfile) as dom:
            def _get_dom_grid(dom, var, grid_arr, collapse_ix):
                # read domain lat coords in 1d array
                dom_arr = dom[var][:]
                dom_arr = numpy.max(dom_arr, axis=collapse_ix)
                # compute mappint grid_lat index -> dom_lat index
                distm = numpy.abs(dom_arr[:, numpy.newaxis] -
                                  grid_arr[numpy.newaxis, :])
                map2dom = numpy.argmin(distm, axis=0)
                d = numpy.min(distm, axis=0)
                assert numpy.all(d < 1e-3), 'Could not map {:}'.format(var)
                return dom_arr, map2dom

            # load full domain grid
            dom_lat, map2dom_lat = _get_dom_grid(dom, 'nav_lat', grid_lat, 1)
            dom_lon, map2dom_lon = _get_dom_grid(dom, 'nav_lon', grid_lon, 0)

            # extract bathymetry at transect points
            bath = _extract_2d(dom, 'bathy_metry',
                               map2dom_lon[nnix_lon], map2dom_lat[nnix_lat])

        # compute vertical grid boundaries (w points without bathymetry)
        z0 = numpy.zeros((nz+1, ))
        z0[0] = 0
        z0[1] = 2*depth0[0]
        for i in range(1, nz):
            z0[i+1] = 2*depth0[i] - z0[i]

        # compute z_w grid for transect
        z_w = numpy.tile(z0[:, numpy.newaxis], (1, npoints))
        z_w = numpy.minimum(bath, z_w)

        # compute t-point z coordinates
        z_t = 0.5*(z_w[:-1, :] + z_w[1:, :])

        # compute t-cell bounds
        z_bounds = numpy.zeros((nz, npoints, 2))
        z_bounds[:, :, 0] = z_w[:-1, :]
        z_bounds[:, :, 1] = z_w[1:, :]

        # apply masks
        nan_mask = ~numpy.isfinite(vals[0, :, :])
        z_t[nan_mask] = numpy.nan
        # z_w[1:, :][nan_mask] = numpy.nan
        # NOTE: for plotting it's better not to mask bounds
        # z_bounds[:, :, 0][nan_mask] = numpy.nan
        # z_bounds[:, :, 1][nan_mask] = numpy.nan

        dst_depth = dst.createVariable('depth', 'f', ('depth', 'index'))
        dst_depth.standard_name = 'depth'
        dst_depth.units = src_depth.units
        dst_depth.bounds = 'depth_bounds'
        dst_depth[:] = z_t

        dst_depthb = dst.createVariable('depth_bounds', 'f',
                                        ('depth', 'index', 'bounds'))
        dst_depthb.long_name = 'depth bounds'
        dst_depthb.units = src_depth.units
        dst_depthb[:] = z_bounds


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract a transect from Nemo 3D output files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('infile',
                        help='Input file name, a NEMO 3D netCDF file')
    parser.add_argument('domainfile',
                        help='Nemo 4.0 domain_cfg.nc file')
    parser.add_argument('var',
                        help='Variable to extract, netCDF variable name')
    parser.add_argument('transect_file',
                        help='A text file that defines transect (lon,lat) '
                        'coordinates, one pair in each line')
    parser.add_argument('outfile',
                        help='Output netCDF file name')
    args = parser.parse_args()

    transect_lonlat = numpy.loadtxt(args.transect_file)
    extract_transect(args.infile, args.domainfile,
                     args.var, transect_lonlat, args.outfile)
