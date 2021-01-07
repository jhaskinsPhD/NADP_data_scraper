# NADP_data_grabber
This repository contains functions to grab data from any Network hosted on the National Atmospheric Deposition Program (http://nadp.slh.wisc.edu/) at any frequency (e.g. weekly, monthly, annual) and easily import it into a pandas dataframe in Python for analysis. Future functionalities may include quick plotting, error removal considering flags, including metadata files supplied by the NADP, and functionalities commonly used to find trends in depositional data. 

**Requirements:** Python 3

* `numpy`: https://numpy.org/
* `pandas`: https://pandas.pydata.org/
* `os`: https://docs.python.org/3/library/os.path.html

### NOTE: 
Data from NADP/NTN used in published works should abide by the NADP data use conditions (http://nadp.slh.wisc.edu/nadp/useConditions.aspx)

## Description of Functions Contained Within: 
### NADP_data_grabber(siteid, network):

Function to directly scrape data for indivudal sites or All sites from NADP website at different time intervals, and return this as a pandas dataframe. Also combines data from site info .csv files (e.g. site lat, long, county, state, etc.) and data .csv into a single dataframe. Converts string date-times into pandas datetimes for easy plotting. 

```
# -------------------Inputs: ----------------------------------------------------------
#       siteid   - String corresponding to the NADP site ID you want data from or 'All' if
#		you'd like to get data from all sites. Individual site names are typically
#		len 4 strings like 'WY99'. Will error if site name doesn't exist. 
#
#       network   - String containing which network you'd like to get data from. 
#		Will push error if invalid network name. Valid options are: 
#                       'NTN'   : National Trends network data 
#                       'MDN'   : Mercury Deposition Network. 
#                       'AIRMoN': Atmospheric Integrated Research Monitoring Network
#                       'AMNet' : Atmospheric Mercury Network
#                       'AMoN'  : Ammonia Monitoring Network
#
#       freq     - String containing the frequency of the data you'd like to retreive 
#                   for this site. Valid options are dependent on which network is chosen. 
#                   Only 1 data frequency is available for AIRMon, AMNet, and AMoN. Therefore
#                   this input is redundant for those networks. If data network is 
#                   NTN or MDN, then valid options are as follows with brackets indicating the 
#                   supported networks for each data frequency. Valid options are as follows:
#
#                      'weekly'          : weekly deposition data [NTN, MDN] ** Default if no freq is passed.**  
#                      'annual-cal-dep'  : annual deposition on calendar year [NTN, MDN]			
#                      'monthly'         : average monthly deposition data [NTN only]  
#                      'annual-cal-conc' :  Pecip weighted annual concentrations on calendar year [NTN only]  
#                      'annual-wy'       : annual deposition on water year  [NTN only]  
#                      'seasonal-conc'   : Pecip weighted seasonal concentrations [NTN only]  
#                      'seasonal-dep'    : Seasonal deposition [NTN only] 
# 
#     valstring   - Redundant input unless your network is 'MDN'. Options are: 
#                   ''   - An empty string which will return only data which the NADP has 
#                         determined to be valid. This is default. 
#                   '-i'  - A string that will return all data (valid and invalid). 
#                           These samples can be identified by the qrCode field, 
#                           which will have a value of "C".
#
#     savepath    - Path to a driectory in which to save a pickle of this datafram. Default is empty which 
#                   does not save a pickle. Name of pickle file is auto generated based on network, siteid, 
#                   and frequency of selected data. 
#
# -------------------Output: --------------------------------------------------------------- 
#
#      df       - pandas dataframe containing all csv data from the NADP. 
#     
#      NADP_NTN_weekly_WA99.pkl  - (OPTIONAL) a pickle file containing the dataframe, df, if a 
#                                  savepath was passed as input.  
```     
### NADP_date_string_converter(df):
Function to identify "date like" columns in a dataframe (df) scraped from NADP data and convert them from strings of various formats to pandas datetime objects for easy use later. Output is just a dataframe with same columns as input df, but with date-like columns as datetime objs.

### get_sites(network):

Function to list valid site names, name of site, and state in a given NADP network. 

## Examples: 

(1) Print a list of all the sites in the NTN Network: 
```
get_sites('NTN')  
```
(2) Get NTN Data from the Davis, CA site,  and make a timeseries of NO3 deposition data. 
```
import matplotlib.pyplot as plt

df_indv= NADP_data_grabber('CA88', 'NTN') 

fig, ax = plt.subplots(1,figsize=(8, 8)) # Create a figure and axis. 
ax.plot(df_indv.dateon, df_indv.NO3) # plot the date on X axis vs. nitrate data on Y axis (units mg/L)
plt.show() 
```
(3) Get weekly NTN data from all the sites, save the data as a pickle at designated path.
 ```
path='C:\\Users\\user\\Documents\\myNADPdirectory\\'
df_all= NADP_data_grabber('All', 'NTN', savepath=path) 
```
(4) Other examples: 
```
out1= NADP_data_grabber('WY99', 'NTN', freq='monthly') # monthly avg'd data for site WY99 from NTN 
out2= NADP_data_grabber('WY96', 'NTN') # weekly data for site WY99 from NTN (native freq)
out3= NADP_data_grabber('MS12', 'AMNet') # hourly data for site MS12 from AMNet  (native freq)
out4= NADP_data_grabber('CA75', 'MDN', freq='annual-cal-dep', valstring='-i')  
#         The above example  outputs precip weighted annual avg deposition that includes invalid data points. 
```
