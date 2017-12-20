# gcmplots

A library of python routines for plotting output from general circulation models (GCMs). Initially we will work with data from ECCOv4, with the intention of generalizing to netcdf output from any model. 

## Libraries used

1. [xmitgcm](http://xmitgcm.readthedocs.io/en/latest/) - a library of low level routines for reading in MITgcm MDS binary output into [xarray](http://xarray.pydata.org/en/stable/) and [dask](https://dask.pydata.org/en/latest/) objects. 
2. [xgcm](http://xgcm.readthedocs.io/en/latest/) - a library for generic operations on general circulation models
3. [GeoViews](http://geo.holoviews.org/) - visualization and data analysis library for geophysical data 
4. [Datashader](https://bokeh.github.io/datashader-docs/) - a graphics pipeline for handling large datasets

These libraries give the general pipeline: MITgcm output is read into an xarray in python or ipython notebook via xmitgcm routines. It can be associated with a grid via xgcm **this may or may not be necessary**. It is then passed to a GeoViews Dataset or Datashader canvas for visualization.

## Dependencies

TBD

## License 

TBD

