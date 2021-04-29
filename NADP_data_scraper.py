import pandas as pd
import numpy as np
import datetime
import calendar
import xarray as xr
import os
import sys

def attach_meta_data(ds, network): 
    """Function to attach NADP metadata to an x-array dataset.
    
    Written by Dr. Jessica D. Haskins, 4/28/2021, github: https://github.com/jdhask/
    Contact at jhaskins@alum.mit.edu 
    """
    
    # Unless they moved it, this is where metadata lives... 
    meta_folder =  os.path.dirname(os.path.abspath(__file__)) +'/metadata/'

    # Read in a csv file containing meta data about all vars
    meta_df= pd.read_csv(meta_folder+network+'_metadata.csv', header=0, delimiter=",")
    meta_df=meta_df.replace(np.nan, 'n/a')

    case_dict=dict() # make a dict connecting data vars to all lower case datavar. 
    for lc in ds.data_vars:
        case_dict[lc.lower()]= lc
    
    for field in meta_df.Field:  # Loop over each field we have meta for. 
        if field.lower() in case_dict.keys(): # Check for match in ds vars, independent of case. 
            uc=case_dict[field.lower()]
            # Assign variable attributes from metadata. 
            ds[uc].attrs['Description'] = str(meta_df.Description[(meta_df.Field==field)].values[:])
            ds[uc].attrs['Units'] = str(meta_df.Units[(meta_df.Field==field)].values[:])
        else: 
            print('Could not assign metadata to:', field)
    
    return ds 


def get_sites(network):
    """Function to list valid site names, name of site, and state in a 
    given NADP network.

    Written by Dr. Jessica D. Haskins, 1/6/2021, github: https://github.com/jdhask/
    Contact at jhaskins@alum.mit.edu 
    """

    # Check that the network passed by the user is valid.
    n=['NTN', 'MDN', 'AIRMoN','AMNet', 'AMoN'] # list of valid options.

    if network in n:
        sites='http://nadp.slh.wisc.edu/data/sites/CSV/?net='+network # URL for NTN or MDN site lists

        s= pd.read_csv(sites) # dataframe containing sites & site info (e.g. lat/long, etc)

        for i in range(0,len(s)):
            print(s.siteid[i], s.siteName[i], ', ', s.state[i])


def NTN_column_clean_up(df): 
    """Function to make sure columns have consistent data types (e.g. numerical 
    columns are all numerical, string columns are all string cols, etc.)
    Specific to NTN data...

    Written by Dr. Jessica D. Haskins, 4/28/2021, github: https://github.com/jdhask/
    Contact at jhaskins@alum.mit.edu 
    
    """ 
    
    # Loop over flags, and convert empty strings (no flags) to boolean == False 
    # and flags '<' to boolean =True so whole flag column is dtype boolean. 
    flags= [name for name in df.columns if 'flag' in name]
    for flg in flags:  
        # Create boolean array full of "False" for if there's a flag same len as data. 
        flag_bool=np.full(len(df[flg]), 0, dtype=bool)
                           
        has_flag = (df[flg]!=' ') # Get indicies of where there is a flag 
        flag_bool[has_flag]=True # Set to "true" if there's a flag. 
        
        df[flg]= flag_bool 
    
    # Loop over variables we expect to be string types and fill any "nans" with
    # empty stirngs so that the column has one consistent data type. 
    str_vars=['siteID', 'labno', 'network','siteName', 'county', 'state',
              'valcode','invalcode', 'status']
    for var in str_vars:
       df[var]=df[var].astype(str)  # Force this column to be a string type column. 
       df[var]=df[var].replace(to_replace ="nan", value ="") # remove "nan" frpm strs
       
    return df 
   
   
def NADP_date_string_converter(df):
    """
    Function to identify "date like" columns in a dataframe (df) scraped from NADP data and
    convert them from strings to pandas datetime objects for easy use later. Output is
    just a dataframe with same columns as input df, but with date-like columns as datetime objs.
    
    Written by Dr. Jessica D. Haskins, 11/13/2020,   github: https://github.com/jdhask/
    Contact at jhaskins@alum.mit.edu
    """

    #Dictionary containing date related columns in all networks & the format we expect them in:
    datelist_dict={0:df.filter(like='date'), 1:df.filter(like='modifiedOn'), 2:df.filter(like='yrmonth'),
    3:df.filter(like='CollStart'), 4:df.filter(like='CollEnd'), 5:df.filter(like='DATE'), 6:df.filter(like='dateon'),
    7:df.filter(like='dateoff'),8:df.filter(like='startdate'),9:df.filter(like='stopdate'),}

    datefmt_dict= {0:'%Y-%m-%d %H:%M', 1:'%m/%d/%Y %H:%M:%S %p', 2:'%Y%m', 3:'%Y-%m-%d %H:%M' ,
    4:'%Y-%m-%d %H:%M', 5:'%Y-%m-%d %H:%M', 6:'%Y-%m-%d %H:%M:%S', 7:'%Y-%m-%d %H:%M:%S', 8:'%Y-%m-%d %H:%M:%S',
    9:'%Y-%m-%d %H:%M:%S'   }

    for t in range(0,10): # Loop over number of "like" statements we have... (doesn't include #10)
        datelist=datelist_dict.get(t) # get the column names in this iteration
        datefmt=datefmt_dict.get(t) # and their expected format in this iteration

        if len(datelist.columns)>0: # Don't try to convert columns that don't exist in this file.
            for (columnName, columnData) in datelist.iteritems(): # Convert each name matching this "like" statement
                df[columnName] = pd.to_datetime(columnData, format=datefmt)

    return df


def get_tuesdays(month, year):
    """Function to get the date of all Tuesdays in a month/ year.
    
    Written by Dr. Jessica D. Haskins, 4/28/2021,   github: https://github.com/jdhask/
    Contact at jhaskins@alum.mit.edu
    """

    #Dates of all tuesdays in a given month and year. (NADP data collected on Tuesdays...)
    tuesdays = np.array([week[1] for week in calendar.monthcalendar(year, month)])
    tuesdays=tuesdays[tuesdays!=0] # has dates as 0 for some reason... 
    
    date_stamp=list() # empty list to hold all dates. 
    for wk in range(0,len(tuesdays)):
        date_stamp.append(str(year)+'-'+str(month)+'-'+str(tuesdays[wk]) + ' 12:00')
        
    return(date_stamp)
     

def aligntimes(df, min_monyr=[7,1978], max_monyr=[11,2020]):
    """Function to align all NADP data to the same time axis in a netcdf, 
    indexed by time/site ID.
    
    Written by Dr. Jessica D. Haskins, 4/28/2021,  github: https://github.com/jdhask/
    Contact at jhaskins@alum.mit.edu

    
    Args:
    -----
     df - dataframe created by NADP_data_grabber for NTN all data. 
     
     min_monyr- array of [month, year] of beginning of when you want to save data. 
                Default is to get data when it began (first Tuesday in July 1978)
     
     min_monyr- array of [month, year] of end of when you want to save data. 
                   Default is to get data up until end of current data
                   (last Tuesday of Nov 2020) as of 4/18/2021. 
         
    
    Output: 
    -------
    
    ds - an x-array data set with all data in df indexed by(time, siteID), all on the 
        same time axis. 
        
    NOTE: The date on which samples are aligned to is the "dateoff" date, so they 
    represent the samples collected on the week prior to the date they're 
    indexed on. e.g. if date on 07-04-1978 and datoeff = 07-11-1978 then
    in the resulting xarray, that same data would appear on 07-11-1978. 
    """
    
    # Get the beginning/end of the collection period we're making a datset of. 
    # Must begin and end on same day of week (Tuesday), when samples collected. 
    min_dt= get_tuesdays(min_monyr[0],min_monyr[1])[0] # First tuesday of month
    
    # Get the date of the  last tuesday in the max mon/year 
    max_dt= get_tuesdays(max_monyr[0],max_monyr[1])[-1] # last tuesday of month.

    # Create a datetime index every Tuesday between the min/max date. 
    dts = pd.date_range(min_dt, max_dt, freq=str(7)+ 'D') 
    
    sites= np.unique(df.siteID) # List of unique site names 
    varnames = list(df.columns) # List of all variables  
    count = 0 # initialize the counter variable. 
    
    irrelevant=['dateon', 'dateoff', 'modifiedon', 'siteID']
    for this_var in range(0, len (varnames)): # Loop over all  variables.
    
        # Don't do this for columns that are time/site coordinates in xarray. 
        if varnames[this_var] not in irrelevant:  
            
            # Make a large array to hold data from all sites of this specific variable. 
            if type(df[varnames[this_var]][0]) == str:
                # Data is str so make empty array of all empty strings same len as data. 
               all_dat = np.full([len(dts), len(sites)], '', dtype= str)  
            else: 
                # Assume data is float, so make array of nans same len as data.  
               all_dat = np.full([len(dts), len(sites)], np.nan) 
                    
            for this_site in range (0,len(sites)): # Loop over each individual site. 
    
                # Get index values of where this site specifically was sampled in larger df
                this_site_only=(df.siteID==sites[this_site]) 
            
                # Create a smaller df containing data from this site only. 
                small_df=df[this_site_only][[varnames[this_var],'dateoff']]
                
                # Make a duplicate column of "dateoff" called "datetime". 
                small_df['datetime']= small_df['dateoff']
                
                # Make column "datetime" the "index" of the dataframe. 
                small_df = small_df.set_index('datetime')  
                
                # Remove any duplicate rows. 
                small_df = small_df[~small_df.index.duplicated()]  
        
                # "Re-sample" the small data frame for the master timeline. 
                small_df_new = small_df.reindex(dts, method='nearest', fill_value=np.NaN,limit=1)
                
                # Grab only this variable after being re-sampled. 
                arr=small_df_new[varnames[this_var]]
                
                # Fill column of larger array that holds data indexed by (DATE, SITE ID)
                # with data for all these dates at this site only. 
                all_dat[:,this_site]=arr
                
            # Once we have assigned data in this variable from all sites to all_dat,
            # then save it as a dataArray in the larger dataset. 
            if count==0: # If first variable we're doing then create the xarray. 
                ds = xr.Dataset({varnames[this_var]: (('index','siteID'), all_dat)}, 
                                coords= {'index': dts, 'siteID': sites})         
            else: # Otherwise append this new DataArray to the existing DataSet
                ds = ds.assign({varnames[this_var]: (('index','siteID'), all_dat)})
                
            count=count+1 # Update counter for which variable we're doing. 
            
            if count ==1: print('Progress converting to merged x-Array:')
            progress=np.round((count/len(varnames))*100)
            print(progress,'%')
            
    return ds


def NADP_data_grabber(siteid, network, freq='native', valstring='', savepath='',
                      aligntimes:bool = False, 
                      min_monyr=[7,1978], max_monyr=[11,2020]):
    """ Function to directly scrape data for individual sites or All sites from 
    NADP website at different time intervals, and return this as an xarray datset. 
    Also combines data from site info csv (e.g. site lat, long, county, state, etc.) 
    and metadata into a single dataset. Converts string date-times into timezone
    aware datetimes for easy plotting.
    
    Written by Dr. Jessica D. Haskins, 11/13/2020,github: https://github.com/jdhask/
    Contact at jhaskins@alum.mit.edu
   
    NOTE: Data from NADP/NTN used in published works should abide by the NADP data
           use conditions (http://nadp.slh.wisc.edu/nadp/useConditions.aspx)
    
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
    
        savepath    - Path to a driectory in which to save a pickle of this datafram. Default is empty which
                      does not save a pickle. Name of pickle file is auto generated based on network, siteid,
                      and frequency of selected data.
                      
        aligntimes -  Boolean of whether you'd like to align all of the data to the same time 
                      index & save as a netcdf file indexed by (Time, SiteID). 
                      This is only relevant if pulling ALL data from the NTN. 
                      
        min_monyr  -  array of [month, year] of beginning of when you want to save aligned data. 
                      Default is to get data when it began (first Tuesday in July 1978). 
                      Only a relevant argument if aligntimes is True. 
     
        min_monyr -   array of [month, year] of end of when you want to save aligned data. 
                      Default is to get data up until end of current data
                      (last Tuesday of Nov 2020) as of 4/18/2021. 
                      Only a relevant argument if aligntimes is True. 
     
    Output: 
    -------
           ds       - xarray dataset containing all csv data from the NADP & metadata. 
    
           NADP_NTN_weekly_WA99.nc - A netcdf file containing the datset 
                                      
    
    Examples: 
    ---------
      out= NADP_data_grabber('all', 'NTN', aligntimes=True) # Get data for all sites from NTN (native freq),
                                              and align to a common times line across all sites. 
      out= NADP_data_grabber('WY99', 'NTN', freq='monthly') # monthly avg'd data for site WY99 from NTN
      out= NADP_data_grabber('WY96', 'NTN') # weekly data for site WY99 from NTN (native freq)
      out= NADP_data_grabber('MS12', 'AMNet') # hourly data for site MS12 from AMNet  (native freq)
      out= NADP_data_grabber('CA75', 'MDN', freq='annual-cal-dep', valstring='-i')
            ^ Above Returns Precip weighted Annual avg dep that includes invalid data points. 
                
     """
    # Check that the network passed by the user is valid.
    n=['NTN', 'MDN', 'AIRMoN','AMNet', 'AMoN']

    if network in n:
        # Validate that the user input is a real site by cross checking input with the site list.
        sites='http://nadp.slh.wisc.edu/data/sites/CSV/?net='+network # URL for NTN or MDN site lists

        s= pd.read_csv(sites) # dataframe containing sites & site info (e.g. lat/long, etc)

        # If user provided site ID is present in the sites list, proceed. Otherwise, exit with error.
        if s['siteid'].str.contains(siteid).any() or siteid=='All':

            # Craft the url based on the sitename & frequency of the pull request.
            std_url= 'http://nadp.slh.wisc.edu/datalib/'

            # Dictionary containing urls of dif types of data for indv sites:
            if network=='AMoN':
                cases={'native': std_url+'/Amon/csv/'+siteid+'-rep.csv'} # is actually a bi-weekly collection
                merger='SITEID'
                
            if network=='AMNet':
                cases={'native': std_url+network+'/'+'/AMNet-'+siteid+'.csv'} # is actually a daily collection...
                merger='SiteID'

            if network=='AIRMoN':
                cases= {'native': std_url+network+'/'+'/AIRMoN-'+siteid+'.csv'}
                merger='siteID'

            if network=='MDN':
                cases= {'native': std_url+network+'/'+'weekly/MDN-'+siteid+'-w'+valstring+'.csv', # weekly data is native freq period
                'weekly': std_url+network+'/'+freq+'/MDN-'+siteid+'-w'+valstring+'.csv',
                'annual-cal-dep': std_url+network+'/'+'annual/MDN-'+siteid+'-a'+valstring+'.csv'}
                merger='siteID'

            if network =='NTN':
                cases= {'monthly': std_url+network+'/'+freq+'/NTN-'+siteid+'-m.csv',
                'native': std_url+network+'/'+'weekly/NTN-'+siteid+'-w.csv',  # weekly data is native freq period.
                'weekly': std_url+network+'/'+freq+'/NTN-'+siteid+'-w.csv',
                'annual-cal-conc': std_url+network+'/'+'cy/NTN-'+siteid+'-cy.csv',
                'annual-cal-dep': std_url+network+'/'+'cydep/NTN-'+siteid+'-cydep.csv',
                'annual-wy' : std_url+network+'/'+'wy/NTN-'+siteid+'-wy.csv',
                'seasonal-conc': std_url+network+'/'+'seas/NTN-'+siteid+'-s.csv',
                'seasonal-dep': std_url+network+'/'+'seasdep/NTN-'+siteid+'-sdep.csv'}
                merger='siteID'
            url = cases.get(freq, None) # Set default to None incase there's a user error in freq

            if url is None: # Check to make sure the url exists:
                sys.exit('ERROR: frequency not defined. See valid inputs for freq.')
            else:   # Read in data from that site and return it.
                print('Loading data... This can take ~5s-3mins. Faster for loading data from 1 site than all site data. Please wait! ')

                df= pd.read_csv(url) # Read in the data from the specified URL

                # rename siteID in s so its the same as keys as in df, so we can merge.
                s.rename(columns = {'siteid':merger}, inplace = True)

                # Take info from site file and add it into the master dataframe (site lat/lon info)
                df_out= df.merge(s, how='left', on=merger)

                # Convert all date related columns from strings to date-time objects for easy plotting.
                df_new= NADP_date_string_converter(df_out)
                
                # Make sure all columns have a consistent data type (all are floats, strs, bool, etc.)
                if network =='NTN': 
                    df_new=NTN_column_clean_up(df_new)
                    
                # Align all of the times to a master time line if asked. 
                # Currently only works for NTN and "all" data.. 
                if (siteid=='All') and (network=='NTN') and (aligntimes==True):
                    print('Aligning times of all NTN Data...')
                    ds = aligntimes(df_new,min_monyr=min_monyr, max_monyr=min_monyr)
                else: 
                    print('Converting to X-Array, please wait...')
                    ds = df_new.to_xarray()
                
                # Attach the appropriate metadata to the dataset. 
                print('Attaching Metadata...')
                ds = attach_meta_data(ds, network)
                
                # If the user has passed a savepath variable, check to see if its valid, and save data as a pickle.
                isValidPath = os.path.isdir(savepath)
                if isValidPath ==False:
                    savepath= os.getcwd()
                    isValidPath = os.path.isdir(savepath)
                        
                if isValidPath ==True:
                    name='\\NADP_'+network+'_'+freq+'_'+siteid+'.nc'
                    ds.to_netcdf(savepath+name)
                    print('File saved as: '+ savepath+name)

                return ds # Return the dataset 
        else:
            sys.exit('ERROR: The site name provided is not a valid site.')
    else:
        sys.exit('ERROR: The network identified is not supported.')


# count_valids_since CURRENTLY BROKEN AFTER MOVE TO X-ARRAY! 
def count_valids_since(df, column_name, year=1975, mon=1, day=1, savepath=''):

    #  Function to count how many valid samples were taken at a site since a given date.
    #  May be useful for identifying which sites have robust records in a time period of interest.
    #
    #  ######   Inputs: #########################################################################
    #
    #   df             - a dataframe generated from NADP_date_grabber()
    #
    #    column_name   - the column you'd like to count valids in.
    #
    #    year(optional)-  Year you'd like to get valid points of data from. Default is 1975.
    #
    #   mon (optional) - Month you'd like to get valid points of data from. Default is 1.
    #
    #   day (optional) - Day you'd like to get valid points of data from. Default is 1.
    #
    #   savepath (optional) - Path to a driectory in which to save a pickle of this datafram. Default is empty which
    #                   does not save a pickle. Name of pickle file is auto generated based on column name, date.
    #
    #  ######   Outputs: #########################################################################
    #
    #    out     - Dataframe containing the site names and valid counts since your date.
    #              Results presented in descending order with most valid points at top.
    #
    #  Written by Dr. Jessica D. Haskins, 1/12/2020,   github: https://github.com/jdhask/
    #  Contact at jhaskins@alum.mit.edu
    # ----------------------------------------------------------------------------------------

    sites=df.siteID.unique() # Get list of unique siteIDs.
    date1= datetime.datetime(year,mon,day) # Datetime object of date you'd like to count valids from.

    for i in range(0,len(sites)):  #Loop over each individual site. and (df.dateon > date1)

        msk1=df.index[df.siteID.str.match(sites[i])==True].tolist() # index vals of where we're looking at this site.
        msk2= df.index[df.dateon> date1].tolist() # index values of where the dates are when we want.
        msk=np.intersect1d(msk1, msk2) # must fit both conditions.

        sliced=df.iloc[msk] # values in df at site i since inputted date.

        valid=len(sliced[column_name]) -np.count_nonzero(np.isnan(sliced[column_name])) # number of valids at this site.

        if i== 0: # Create array, of valid # since date indexed same as sites list.
            valids=valid
        else:
            valids=np.append(valids, valid)

        if i % 10 ==0: # Print a progress update occassionally.
            print('Progress:', np.round(i/len(sites)*10000)/100, '%')

        i=i+1 # move to next site.

    # Create data frame with site name and valid counts:
    out=pd.DataFrame(sites, columns=['siteIDs'])
    out['Valid_n']= valids

    # Sort by the sites with the most valid points.
    out.sort_values( 'Valid_n',axis=0, inplace=True, ascending=False, ignore_index=True)

    # If the user has passed a savepath variable, check to see if its valid, and save data as a pickle.
    isValidPath = os.path.isdir(savepath)
    if isValidPath ==True and len(savepath)>=1:
        name='\\NADP_'+column_name+'_valids_since'+str(year)+'.pkl'
        out.to_pickle(savepath+name)
        print('File saved as: '+ savepath+name)

    if isValidPath ==False and len(savepath)>=1:
        sys.exit('ERROR: Inputted SavePath is not a valid directory.')

    return out