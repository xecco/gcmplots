"""
This module defines "plotters", or classes wrapping xgcm data sets for
plotting. In general, the workflow will be to construct a plotter from a parent
data set, set some data variable to be plotted, then call geoviews/holoviews/
datashader routines to do the plotting (return type of object undecided? 
Probably the underlying holoviews object so that things can be composed to make
fancy plots).

Currently only implements a plotter for the LLC grid.
"""

from dask.array import concatenate
import xarray as xr
import numpy as np

def has_vertical_dim(var):
    "Helper to make sure a variable is two dimensional data"
    suffixes = ('', '_u', '_l', '_p1')
    for suffix in suffixes:
        if 'k' + suffix in var.dims:
            return True
    return False

class LLC_plotter:
    """
    The `LLC_plotter` class wraps logic needed for plotting data from the gcm to
    hopefully avoid the user needing to interface *too much* with the 
    underlying libraries and their complex interfaces.
    
    This version of the class is intended only to work the LLC grid as used by
    the ECCO project.
    
    @todo More documentation here once I've worked it out...
    """
    def __init__(self, parent_ds):
        """
        The plotter is constructed from a parent data set. From the parent's 
        `XC` and `YC` variables, it constructs its own coordinates XC and YC, 
        and an internal xarray Dataset object based on these coordinates.
        """
        if not isinstance(parent_ds, xr.Dataset):
            raise TypeError('LLC_plotter must be constructed from an xarray dataset')
            
        self.parent = parent_ds
        XC = concatenate([parent_ds.XC[i,:,:].data \
                          for i in range(parent_ds.XC.shape[0])])
        YC = concatenate([parent_ds.YC[i,:,:].data \
                          for i in range(parent_ds.YC.shape[0])])
        XG = concatenate([parent_ds.XG[i,:,:].data \
                          for i in range(parent_ds.XG.shape[0])])
        YG = concatenate([parent_ds.YG[i,:,:].data \
                          for i in range(parent_ds.YG.shape[0])])
        
        # Important assumption - this certainly *should* be the case for any
        # sane data set.
        assert XC.shape == YC.shape and XG.shape == YG.shape
        assert XC.shape == XG.shape
        
        jdim, idim = XC.shape
        i = xr.DataArray(np.arange(idim), coords=[('i', np.arange(idim))])
        j = xr.DataArray(np.arange(jdim), coords=[('j', np.arange(jdim))])
        i_g = xr.DataArray(np.arange(idim), coords=[('i_g', np.arange(idim))])
        j_g = xr.DataArray(np.arange(jdim), coords=[('j_g', np.arange(jdim))])
        
        XC = xr.DataArray(XC, coords=[('j', j), ('i', i)])
        YC = xr.DataArray(YC, coords=[('j', j), ('i', i)])
        XG = xr.DataArray(XG, coords=[('j_g', j_g), ('i_g', i_g)])
        YG = xr.DataArray(YG, coords=[('j_g', j_g), ('i_g', i_g)])
        
        self.ds = xr.Dataset(coords={'i': i, 'j': j, 'i_g': i_g, 'j_g': j_g, 
                                     'XC': XC, 'XG': XG, 'YC': YC, 'YG': YG})

    def set_data_variable(self, var_name):
        """
        Set the data variable to be plotted by the plotter. The variable is
        specified by name (`var_name`), and must represent 2 dimensional data
        (what to do with 3D data would be pretty unclear). The data variable
        must be present in the parent data set, and should still be in the LLC
        format with 'face' as one of the dimension names. Each face will be
        concatenated along the 'j' dimension, as we did for the physical
        coordinates in constructing the internal data set, and it will be added
        to the internal dataset as 'var_to_plot'.
        """
        if not var_name in self.parent.data_vars:
            raise KeyError('Variable {v}'.format(v = var_name) + 
                           'is not contained in the parent dataset')
        
        var = self.parent[var_name]
        if has_vertical_dim(var):
            raise ValueError('The current plotter implementation ' +
                             'only accepts 2-dimensional data')
        elif not 'face' in var.dims:
            raise ValueError("The plotter doesn't know what to do " +
                             "with non-LLC data.")
        
        j_axis_name = 'j' if 'j' in var.dims else 'j_g'
        i_axis_name = 'i' if 'i' in var.dims else 'i_g'
        j_axis = var.sel(face=0).dims.index('j')
            
        raw_var = concatenate([var.sel(face=i) for i in range(var.face.size)],
                              axis = j_axis)
        
        coords = [(j_axis_name, np.arange(raw_var.shape[j_axis])),
                  (i_axis_name, var[i_axis_name])]
        if 'time' in var.dims:
            coords.insert(0, ('time', var.time))
            
        var = xr.DataArray(raw_var, coords=coords)
        self.ds['var_to_plot'] = var
        return self
     
     # TODO: Implement plotting. I'm running up against trouble with GeoViews,
     # I think I may need to file a bug report or two (or fix them myself).
