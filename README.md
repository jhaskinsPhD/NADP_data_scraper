# NADP_data_scraper
This repository contains functions to grab data from any Network hosted on the National Atmospheric Deposition Network (http://nadp.slh.wisc.edu/) at any frequency (e.g. weekly, monthly, annual) and easily import it into a pandas dataframe in python. Future functionalities may include quick plotting, error removal considering flags, including metadata files supplied by the NADP, and functionalities commonly used to find trends in depositional data. 

### NOTE: 
Data from NADP/NTN used in published works should abide by the NADP data use conditions (http://nadp.slh.wisc.edu/nadp/useConditions.aspx)

**Requirements:** Python 3

* `numpy`: https://numpy.org/
* `pandas`: https://pandas.pydata.org/
* `os`: https://docs.python.org/3/library/os.path.html

## Description of Functions Contained Within: 
### NADP_data_grabber(siteid, network, freq='native', valstring='', savepath=''):

Function to directly scrape data for indivudal sites or All sites from NADP website at difference time intervals, and return this as a pandas dataframe. Also combines data from site info csv (e.g. site lat, long, county, state, etc.) and data csv into a single data frame. Converts string date-times into pandas datetimes for easy plotting. 

### NADP_date_string_converter(df):
Function to identify "date like" columns in a dataframe (df) scraped from NADP data and convert them from strings of various formats to pandas datetime objects for easy use later. Output is just a dataframe with same columns as input df, but with date-like columns as datetime objs.

### get_sites(network):

Function to list valid site names, name of site, and state in a given NADP network. 

## Examples: 
```
get_sites('NTN')  # Print a list of all the sites in the NTN network. 

#df= NADP_data_grabber('All', 'NTN') # Get NTN Data from all sites 

path='C:\\Users\\user\\Documents\\myNADPdirectory\\'
df= NADP_data_grabber('CA88', 'NTN', savepath=path) # Get NTN Data from the Davis, CA site and save the data as a pickle at designated path. 

out= indv_NADP_site_grabber('WY99', 'NTN', freq='monthly') # monthly avg'd data for site WY99 from NTN 
out= indv_NADP_site_grabber('WY96', 'NTN') # weekly data for site WY99 from NTN (native freq)
out= indv_NADP_site_grabber('MS12', 'AMNet') # hourly data for site MS12 from AMNet  (native freq)
out= indv_NADP_site_grabber('CA75', 'MDN', freq='annual-cal-dep', valstring='-i')  
     # The above example  outputs precip weighted annual avg deposition that includes invalid data points. 

```
