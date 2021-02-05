from NADP_data_scraper import * # Import all functions from the nice module.
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

import os
# does this really work if I edit it in GitKraken? 

# Tell it where to save
path='C:\\Users\\jhask\\OneDrive\\Documents\\Research\\mini-UROP'

# Grab the Data either all of it or just the one site.
#df= NADP_data_grabber('All', 'NTN', savepath=path) # Get NTN Data from all sites:

#Restore the data we loaded for fastness.
df = pd.read_pickle(path+'\\NADP_NTN_native_NY10.pkl')

# Tell us where the sites are that have a lot of 2020 data:
#out=count_valids_since(df, 'NO3', year=2020, mon=1, day=1, savepath='')
#print(out[0:30]) # Print sites 0-30 with good data.

# A few functions that will allow us to do some averaging.
def avg_and_align2week(df, column2avg, begavgyr1, endavgyr1, begavgyr2, endavgyr2):
    # Function to average the column2avg between begavgyr1 and endavgyr2, and
    # also between begavgyr2 and endavgyr2. Output is averages between these periods,
    # and the week # (so aligned to same timeline.)

    date_1= datetime.datetime(begavgyr1, 1, 1) # beginning of averaging period 1
    date_2= datetime.datetime(endavgyr1, 1, 1) # end of averaging period 1
    date_3= datetime.datetime(begavgyr2, 1, 1) # beginning of averaging period 2
    date_4= datetime.datetime(endavgyr2, 1, 1) # end of averaging period. 2

    ind1=((df.dateon>=date_1) & (df. dateon < date_2)) # Find data index values between 2 dates
    ind2=((df.dateon>=date_3) & (df. dateon < date_4)) # Find data index values between 2 dates

    day_of_year = df.dateon.dt.dayofyear # convert dates to day of years.

    # Get a slice of the desired column with data only between dates 1 and 2.
    slice_1 =column2avg[ind1] # All column data between avg period 1.
    doy_1= day_of_year[ind1] # day of year only from avg period 1.

    slice_2 =column2avg[ind2] # All column data between avg period 2.
    doy_2=day_of_year[ind2] # day of year only from avg period 2.

    # Calculate average NO3 deposition between period 1 and 2 and align the average to the same
    # timeline- e.g. week of year number.
    for i in range(1,52) : # Count from 0 to 52 (52.1429 weeks in a year) # changed
     	#Get index values where doy is between  1-7(week 1) or 8-15 (week 2), 16-23 (week 3).
        this_week1=((doy_1>(i-1)*7) & (doy_1<= (i)*7))# changed
        this_week2=((doy_2>(i-1)*7) & (doy_2<= (i)*7))# changed

        if len(slice_1[this_week1])!= 0:# if you have data in avg period 1 for this week.
            val_1=np.nanmean(slice_1[this_week1])
            std_1=np.nanstd(slice_1[this_week1])
        else: #otherwise set it to a nan.
            val_1=np.nan
            std_1=np.nan
        if len(slice_2[this_week2])!= 0:# if you have data in avg period 2 for this week.
            val_2=np.nanmean(slice_2[this_week2])
            std_2=np.nanstd(slice_2[this_week2])
        else: #otherwise set it to a nan.
            val_2=np.nan
            std_2=np.nan

        if i==1: # if you're on the first pass through the loop, # changed
            avg_slice_1= val_1 # make a new array, first value with the avg.
            avg_slice_2=val_2
            stddev_1= std_1
            stddev_2= std_2
            week_no=i
        else: # otherwise, append this week's average to an array containing all the weeks values.
            avg_slice_1= np.append(avg_slice_1, val_1)
            avg_slice_2=np.append(avg_slice_2,val_2)
            stddev_1= np.append(stddev_1,std_1)
            stddev_2= np.append(stddev_2,std_2)
            week_no=np.append(week_no,i)

        i=i+1 # update the iteration variable.
    return week_no, avg_slice_1, stddev_1, avg_slice_2, stddev_2

def calc_norm_difference(week_n, avg_1, std_1, avg_2, week1, week2):
    # Function to calculate the percent difference and normalized difference
    # on a week by week basis, between two average periods.Input must be the week number
    # and concentrations/deposition indexed by week number.


    for week in range(week1, week2,):# Loop over each day from March 22nd(doy=82, week 13)- Sunday to May 10th (doy=129, week=19)- also a Sunday.

        # Calculate the difference in the avgs during this week normalized by standard deviation.
        dif= avg_2[week-1]- avg_1[week-1] # The absolute difference in this week. # changed
        norm_dif_i=dif/np.nanmean(std_1) # Divide the difference by the std deviation (will tell how many std devs the dif is above or below)
        per_dif_i= (dif/ avg_1[week-1])*100 #  The percent difference. # changed

        if week==week1: # If you're on the first loop around. Create an array to hold these values.
           norm_dif=norm_dif_i
           per_dif=per_dif_i
           tm=week
        else: # otherwise append this weeks value onto the end of our array.
           norm_dif=np.append(norm_dif, norm_dif_i)
           per_dif=np.append(per_dif,per_dif_i)
           tm=np.append(tm,week)

        week=week+1

    # Calculate the average over this time period. (once the arrays are built).
    avg_per_dif=np.nanmedian(per_dif)
    avg_norm_dif=np.nanmedian(norm_dif)

    # Plot a time series of the % difference and the Normalized Difference & the avg.
    fig, ax = plt.subplots(3,figsize=(8, 8))

    # Plot The raw data so we can see if things tend to make sense...
    ax[0].scatter(week_n, avg_1, label=" Avg 16-19", color='blue',linewidth=1)
    ax[0].scatter(week_n,avg_2, label=" Avg 2020", color='purple',linewidth=1)
    ax[0].set_xlim([week1,week2]) # changed

    ax[1].scatter(tm, per_dif, label=" Percent Difference 2020", color='green',linewidth=1)
    ax[1].plot(tm, np.full(len(tm),avg_per_dif), label=" Avg % Difference", color='green',linewidth=1)
    ax[1].set_xlim([week1,week2])# changed
    # Plot percent difference as a function of day and the average.
    ax[2].scatter(tm, norm_dif, label="Normalized Difference", color='red',linewidth=1)
    ax[2].plot(tm, np.full(len(tm),avg_norm_dif), label=" Average Normalized Difference", color='red',linewidth=1)
    ax[2].set_xlim([week1,week2])# changed

    return avg_norm_dif, avg_per_dif


# Average and align the Nitrate data. Average between 2016-2019 and then just get 2020 data.
nweek, NO3_19to16, stdNO3_19to16,NO3_2020, stdNO3_2020 = avg_and_align2week(df, df.NO3,2016, 2020,2020, 2021)

# Now pass the outputs of the function above to this function calc_norm_difference
# which calculates the normalized and percent difference between the NO319to16 and NO3_2020 data.
NO3avg_norm_dif, NO3avg_per_dif=calc_norm_difference(nweek, NO3_19to16, stdNO3_19to16, NO3_2020, 1,20)
