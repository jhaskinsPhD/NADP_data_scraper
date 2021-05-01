# NADP_data_scraper
This repository contains functions to grab data from any Network hosted on the National Atmospheric Deposition Program (http://nadp.slh.wisc.edu/) at any frequency (e.g. weekly, monthly, annual) and easily import it into an xarray dataset in Python for analysis with metadata attached. Future functionalities may include quick plotting, error removal considering flags, including metadata files supplied by the NADP, and functionalities commonly used to find trends in depositional data. 

**Requirements:** Python 3

* `numpy`: https://numpy.org/
* `pandas`: https://pandas.pydata.org/
* `os`: https://docs.python.org/3/library/os.path.html

### NOTE: 
Data from NADP/NTN used in published works should abide by the NADP data use conditions (http://nadp.slh.wisc.edu/nadp/useConditions.aspx)

## Description of Functions Contained Within: 
### NADP_data_grabber(siteid, network):

Function to directly scrape data for indivudal sites or All sites from NADP website at different time intervals, and return this as an xArray DataSet. Also combines data from site info .csv files (e.g. site lat, long, county, state, etc.) and meatdata into a single dataframe. Converts string date-times into datetimes for easy plotting. If grabbing data from all NTN sites, it can align all the data into a single timeline (every Tuesday from when data collection began to the most recent Tuesday in the dataset), so that the resulting x-Array is indexed by both siteID and time. 

```
Args: 
    -----
          siteid   - String corresponding to the NADP site ID you want data from or 'All' if
                        you'd like to get data from all sites. Individual site names are typically
                        len 4 strings like 'WY99'. Will error if site name doesn't exist.
    
          network   - String containing which network you'd like to get data from.
                        Will push error if invalid network name. Valid options are:
                          'NTN'   : National Trends network data
                          'MDN'   : Mercury Deposition Network.
                          'AIRMoN': Atmospheric Integrated Research Monitoring Network
                          'AMNet' : Atmospheric Mercury Network
                          'AMoN'  : Ammonia Monitoring Network
    
          freq     - String containing the frequency of the data you'd like to retreive
                      for this site. Valid options are dependent on which network is chosen.
                      Only 1 data frequency is available for AIRMon, AMNet, and AMoN. Therefore
                      this input is redundant for those networks. If data network is
                      NTN or MDN, then valid options are as follows with brackets indicating the
                      supported networks for each data frequency. Valid options are as follows:
    
                          'weekly'          : weekly deposition data [NTN, MDN] ** Default if no freq is passed.**
                          'annual-cal-dep'  : annual deposition on calendar year [NTN, MDN]
                          'monthly'         : average monthly deposition data [NTN only]
                          'annual-cal-conc' :  Pecip weighted annual concentrations on calendar year [NTN only]
                          'annual-wy'       : annual deposition on water year  [NTN only]
                          'seasonal-conc'   : Pecip weighted seasonal concentrations [NTN only]
                          'seasonal-dep'    : Seasonal deposition [NTN only]
    
        valstring   - Redundant input unless your network is 'MDN'. Options are:
                       ''   - An empty string which will return only data which the NADP has
                              determined to be valid. This is default.
                      '-i'  - A string that will return all data (valid and invalid).
                              These samples can be identified by the qrCode field,
                              which will have a value of "C".
    
        savepath    - Path to a driectory in which to save a netcdf file of this Datset. Default is
                      to save in the current working director. Name of  file is auto generated based on 
                      network, siteid, and frequency of selected data.
                      
        align      -  Boolean of whether you'd like to align all of the data to the same time 
                      index & save as a netcdf file indexed by (Time, SiteID). 
                      This is only a valid arguement if pulling ALL data from the NTN network.
                      Future functionality may extend this. 
                      
        min_monyr  -  array of [month, year] of beginning of when you want to save aligned data. 
                      Default is to get data when it began (first Tuesday in July 1978). 
                      Only a relevant argument if align is True, network is NTN, grabbing all data.
     
        min_monyr -   array of [month, year] of end of when you want to save aligned data. 
                      Default is to get data up until end of current data
                      Only a relevant argument if alignt is True, network is NTN, grabbing all data.
     
    Output: 
    -------
           ds       - xarray dataset containing all csv data from the NADP & metadata. 
    
           NADP_NTN_weekly_WA99.nc - A netcdf file containing the datset 
```   

### NADP_date_string_converter(df):
Function to identify "date like" columns in a dataframe (df) scraped from NADP data and convert them from strings of various formats to pandas datetime objects for easy use later. Output is just a dataframe with same columns as input df, but with date-like columns as datetime objs.

### get_sites(network):
Function to list valid site names, name of site, and state in a given NADP network. 


### count_valids_since(df, column_name, year=1975, mon=1, day=1, savepath='')
**Note: Currently broken since migration from pandas to xarray... 
Function to count how many valid samples in column_name were taken at all site since a given date, and save the siteIDs and 
of valid data samples in a dataframe with an option to save it. This function may be useful for identifying 
which sites have robust records in a time period of interest. Input df is that from the NADP_data_grabber for All sites data. 
This function is redundant for dataframes with only 1 site's data contained within it. 



## Examples: 

(1) Print a list of all the sites in the NTN Network: 
```
get_sites('NTN')  
```
(2) Get NTN Data from the Davis, CA site,  and make a timeseries of NO3 deposition data. 
```
import matplotlib.pyplot as plt

ds_indv= NADP_data_grabber('CA88', 'NTN') 

fig, ax = plt.subplots(1,figsize=(8, 8)) # Create a figure and axis. 
ax.plot(ds_indv.dateon, ds_indv.NO3) # plot the date on X axis vs. nitrate data on Y axis (units mg/L)
plt.show() 
```
(3) Get weekly NTN data from all the sites on the actual date the data ws collected, save the data as a xarray at designated path.
 ```
path='C:\\Users\\user\\Documents\\myNADPdirectory\\'
ds_all= NADP_data_grabber('All', 'NTN', savepath=path) 
```
(4) Get weekly NTN data from all the sites, but align the data to a common timeline (every Tuesday)...
 ```
path='C:\\Users\\user\\Documents\\myNADPdirectory\\'
ds_all= NADP_data_grabber('All', 'NTN', savepath=path, align=True)                                                                                       
```

(5) Determine which sites have the most valid nitrate records during 2020 until now. 
```
df= count_valids_since(df, 'NO3', year=2020, savepath=path)
```

(6) Other examples: 
```
out1= NADP_data_grabber('WY99', 'NTN', freq='monthly') # monthly avg'd data for site WY99 from NTN 
out2= NADP_data_grabber('WY96', 'NTN') # weekly data for site WY99 from NTN (native freq)
out3= NADP_data_grabber('MS12', 'AMNet') # hourly data for site MS12 from AMNet  (native freq)
out4= NADP_data_grabber('CA75', 'MDN', freq='annual-cal-dep', valstring='-i')  
#         The above example  outputs precip weighted annual avg deposition that includes invalid data points. 
```
