## dea_bandindices.py
'''
Description: This file contains a set of python functions for computing remote sensing band indices on Digital Earth Australia data.

License: The code in this notebook is licensed under the Apache License, Version 2.0 (https://www.apache.org/licenses/LICENSE-2.0). Digital Earth Australia data is licensed under the Creative Commons by Attribution 4.0 license (https://creativecommons.org/licenses/by/4.0/).

Contact: If you need assistance, please post a question on the Open Data Cube Slack channel (http://slack.opendatacube.org/) or on the GIS Stack Exchange (https://gis.stackexchange.com/questions/ask?tags=open-data-cube) using the `open-data-cube` tag (you can view previously asked questions here: https://gis.stackexchange.com/questions/tagged/open-data-cube). 

If you would like to report an issue with this script, you can file one on Github (https://github.com/GeoscienceAustralia/dea-notebooks/issues/new).

Last modified: September 2019

'''


# Define custom functions
def calculate_indices(ds,
                      index=None,
                      collection=None,
                      custom_varname=None):
    """
    Takes an xarray dataset containing spectral bands, calculates one of
    a set of remote sensing indices, and adds the resulting array as a 
    new variable in the original dataset.  
    
    Last modified: September 2019
    
    Parameters
    ----------  
    ds : xarray Dataset
        A two-dimensional or multi-dimensional array with containing the 
        spectral bands required to calculate the index. These bands are 
        used as inputs to calculate the selected water index.
    index : str
        A string giving the name of the index to calculate:
        'NDVI' (Normalised Difference Vegetation Index, Rouse 1973)
        'EVI' (Enhanced Vegetation Index, Huete 2002),
        'LAI' (Leaf Area Index, Boegh 2002),
        'SAVI' (Soil Adjusted Vegetation Index, Huete 1988),
        'NDMI' (Normalised Difference Moisture Index, Gao 1996),
        'NBR' (Normalised Burn Ratio, Lopez Garcia 1991),
        'BAI' (Burn Area Index, Martin 1998),
        'NDBI' (Normalised Difference Built-Up Index, Zha 2003),
        'NDSI' (Normalised Difference Snow Index, Hall 1995),
        'NDWI' (Normalised Difference Water Index, McFeeters 1996), 
        'MNDWI' (Modified Normalised Difference Water Index, Xu 1996), 
        'AWEI_ns (Automated Water Extraction Index,
                  no shadows, Feyisa 2014)',
        'AWEI_sh' (Automated Water Extraction Index,
                   shadows, Feyisa 2014), 
        'WI' (Water Index, Fisher 2016),
        'TCW' (Tasseled Cap Wetness, Crist 1985),
        'TCG' (Tasseled Cap Greeness, Crist 1985),
        'TCB' (Tasseled Cap Brightness, Crist 1985),
        'CMR' (Clay Minerals Ratio, Drury 1987),
        'FMR' (Ferrous Minerals Ratio, Segal 1982),
        'IOR' (Iron Oxide Ratio, Segal 1982)   
    collection : str
        An string that tells the function what data collection is 
        being used to calculate the index. This is necessary because 
        different collections use different names for bands covering 
        a similar spectra. Valid options are 'ga_landsat_2' (for GA 
        Landsat Collection 2), 'ga_landsat_3' (for GA Landsat 
        Collection 3) and 'ga_sentinel2_1' (for GA Sentinel 2 
        Collection 1).
    custom_varname : str, optional
        By default, the original dataset will be returned with 
        a new index variable named after `index` (e.g. 'NDVI'). To 
        specify a custom name instead, you can supply e.g. 
        `custom_varname='custom_name'`. 
        
    Returns
    -------
    ds : xarray Dataset
        The original xarray Dataset inputted into the function, with a 
        new varible containing the remote sensing index as a DataArray.
    """

    # Dictionary containing remote sensing index band recipes
    index_dict = {
                  # Normalised Difference Vegation Index, Rouse 1973
                  'NDVI': lambda ds: (ds.nir - ds.red) /
                                     (ds.nir + ds.red),

                  # Enhanced Vegetation Index, Huete 2002
                  'EVI': lambda ds: ((2.5 * (ds.nir - ds.red)) /
                                     (ds.nir + 6 * ds.red -
                                      7.5 * ds.blue + 1)),

                  # Leaf Area Index, Boegh 2002
                  'LAI': lambda ds: (3.618 * ((2.5 * (ds.nir - ds.red)) /
                                     (ds.nir + 6 * ds.red -
                                      7.5 * ds.blue + 1)) - 0.118),

                  # Soil Adjusted Vegetation Index, Huete 1988
                  'SAVI': lambda ds: ((1.5 * (ds.nir - ds.red)) /
                                      (ds.nir + ds.red + 0.5)),

                  # Normalised Difference Moisture Index, Gao 1996
                  'NDMI': lambda ds: (ds.nir - ds.swir1) /
                                     (ds.nir + ds.swir1),

                  # Normalised Burn Ratio, Lopez Garcia 1991
                  'NBR': lambda ds: (ds.nir - ds.swir2) /
                                    (ds.nir + ds.swir2),

                  # Burn Area Index, Martin 1998
                  'BAI': lambda ds: (1.0 / ((0.10 - ds.red) ** 2 +
                                            (0.06 - ds.nir) ** 2)),

                  # Normalised Difference Built-Up Index, Zha 2003
                  'NDBI': lambda ds: (ds.swir1 - ds.nir) /
                                     (ds.swir1 + ds.nir),

                  # Normalised Difference Snow Index, Hall 1995
                  'NDSI': lambda ds: (ds.green - ds.swir1) /
                                     (ds.green + ds.swir1),

                  # Normalised Difference Water Index, McFeeters 1996
                  'NDWI': lambda ds: (ds.green - ds.nir) /
                                     (ds.green + ds.nir),

                  # Modified Normalised Difference Water Index, Xu 2006
                  'MNDWI': lambda ds: (ds.green - ds.swir1) /
                                      (ds.green + ds.swir1),

                  # Automated Water Extraction Index (no shadows), Feyisa 2014
                  'AWEI_ns': lambda ds: (4 * (ds.green - ds.swir1) -
                                        (2.5 * ds.nir * + 2.75 * ds.swir2)),

                  # Automated Water Extraction Index (shadows), Feyisa 2014
                  'AWEI_sh': lambda ds: (ds.blue + 2.5 * ds.green -
                                         1.5 * (ds.nir + ds.swir1) -
                                         2.5 * ds.swir2),

                  # Water Index, Fisher 2016
                  'WI': lambda ds: (1.7204 + 171 * ds.green + 3 * ds.red -
                                    70 * ds.nir - 45 * ds.swir1 -
                                    71 * ds.swir2),

                  # Tasseled Cap Wetness, Crist 1985
                  'TCW': lambda ds: (0.0315 * ds.blue + 0.2021 * ds.green +
                                     0.3102 * ds.red + 0.1594 * ds.nir +
                                    -0.6806 * ds.swir1 + -0.6109 * ds.swir2),

                  # Tasseled Cap Greeness, Crist 1985
                  'TCG': lambda ds: (-0.1603 * ds.blue + -0.2819 * ds.green +
                                     -0.4934 * ds.red + 0.7940 * ds.nir +
                                     -0.0002 * ds.swir1 + -0.1446 * ds.swir2),

                  # Tasseled Cap Brightness, Crist 1985
                  'TCB': lambda ds: (0.2043 * ds.blue + 0.4158 * ds.green +
                                     0.5524 * ds.red + 0.5741 * ds.nir +
                                     0.3124 * ds.swir1 + -0.2303 * ds.swir2),

                  # Clay Minerals Ratio, Drury 1987
                  'CMR': lambda ds: (ds.swir1 / ds.swir2),

                  # Ferrous Minerals Ratio, Segal 1982
                  'FMR': lambda ds: (ds.swir1 / ds.nir),

                  # Iron Oxide Ratio, Segal 1982
                  'IOR': lambda ds: (ds.red / ds.blue)
    }

    # Select a water index function based on 'water_index'      
    index_func = index_dict.get(index)
    
    # If no index is provided or if no function is returned due to an 
    # invalid option being provided, raise an exception informing user to 
    # choose from the list of valid options
    if index is None:
        
        raise ValueError(f"No remote sensing `index` was provided. Please "
                          "refer to the function \ndocumentation for a full "
                          "list of valid options for `index` (e.g. 'NDVI')")
        
    elif index_func is None:
        
        raise ValueError(f"The selected index '{index}' is not one of the "
                          "valid remote sensing index options. \nPlease "
                          "refer to the function documentation for a full "
                          "list of valid options for `index`")

    # Rename bands to a consistent format if depending on what collection
    # is specified in `collection`. This allows the same index calculations
    # to be applied to all collections. If no collection was provided, 
    # raise an exception.
    if collection is None:

        raise ValueError("'No `collection` was provided. Please specify "
                         "either 'ga_landsat_2', 'ga_landsat_3' \nor "
                         "'ga_sentinel2_1' to ensure the function calculates "
                         "indices using the correct spectral bands")
    
    elif collection == 'ga_landsat_3':

        # Dictionary mapping full data names to simpler 'red' alias names
        bandnames_dict = {
            'nbart_nir': 'nir',
            'nbart_red': 'red',
            'nbart_green': 'green',
            'nbart_blue': 'blue',
            'nbart_swir_1': 'swir1',
            'nbart_swir_2': 'swir2',
            'nbar_red': 'red',
            'nbar_green': 'green',
            'nbar_blue': 'blue',
            'nbar_nir': 'nir',
            'nbar_swir_1': 'swir1',
            'nbar_swir_2': 'swir2'
        }

        # Rename bands in dataset to use simple names (e.g. 'red')
        bands_to_rename = {
            a: b for a, b in bandnames_dict.items() if a in ds.variables
        }

    elif collection == 'ga_sentinel2_1':

        # Dictionary mapping full data names to simpler 'red' alias names
        bandnames_dict = {
            'nbart_red': 'red',
            'nbart_green': 'green',
            'nbart_blue': 'blue',
            'nbart_nir_1': 'nir',
            'nbart_swir_2': 'swir1',
            'nbart_swir_3': 'swir2',
            'nbar_red': 'red',
            'nbar_green': 'green',
            'nbar_blue': 'blue',
            'nbar_nir': 'nir',
            'nbar_swir_2': 'swir1',
            'nbar_swir_3': 'swir2'
        }

        # Rename bands in dataset to use simple names (e.g. 'red')
        bands_to_rename = {
            a: b for a, b in bandnames_dict.items() if a in ds.variables
        }

    elif collection == 'ga_landsat_2':

        # Pass an empty dict as no bands need renaming
        bands_to_rename = {}
    
    # Raise error if no valid collection name is provided:
    else:
        raise ValueError(f"'{collection}' is not a valid option for "
                          "`collection`. Please specify either \n"
                          "'ga_landsat_2', 'ga_landsat_3' or "
                          "'ga_sentinel2_1'")
        
    # Apply index function after normalising to 0.0-1.0 by dividing by 10K
    try:
        index_array = index_func(ds.rename(bands_to_rename)/1000.0)
    except AttributeError:
        raise ValueError(f'Please verify that all bands required to '
                         f'compute {index} are present in `ds`. \n'
                         f'These bands may vary depending on the `collection` '
                         f'(e.g. the Landsat `nbart_nir` band \n'
                         f'is equivelent to `nbart_nir_1` for Sentinel 2)')

    # Add as a new variable in dataset
    output_band_name = custom_varname if custom_varname else index
    ds[output_band_name] = index_array

    # Return input dataset with added water index variable
    return ds
