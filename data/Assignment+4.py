
# coding: utf-8

# ---
#
# _You are currently looking at **version 1.0** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
#
# ---

# In[1]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_colwidth', 200)

# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
#
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
#
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
#
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
#
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_1samp
from scipy.stats import normaltest
import re


# In[41]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan","Ann Arbor"], ["Michigan", "Yipsilanti"] ],
    columns=["State","RegionName"]  )'''
    with open('university_towns.txt') as file:
        data = file.readlines()
    state_town = []
    for line in data:
        if '[edit]' in line:
            state = line.split('[')[0].strip()
        elif '(' in line:
            town = line.split('(')[0].strip()
            state_town.append([state,town])
        else:
            town = line.strip()
            state_town.append([state,town])
    df = pd.DataFrame(state_town,columns = ['State','RegionName'])
    return df


# In[45]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a
    string value in a format such as 2005q3'''
    df = pd.read_excel("gdplev.xls", skiprows=5, index_col=4)
    df = df.iloc[2:, 5].loc["2000q1":]
    c1 = df.pct_change() < 0
    c2 = df.pct_change().shift(-1) < 0
    return (c1 & c2).argmax()


# In[46]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a
    string value in a format such as 2005q3'''
    df = pd.read_excel("gdplev.xls", skiprows=5, index_col=4)
    df = df.iloc[2:, 5].loc[get_recession_start():]
    c0 = df.pct_change() > 0
    c1 = df.pct_change().shift(1) > 0
    return (c0 & c1).argmax()


# In[50]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a
    string value in a format such as 2005q3'''
    df = pd.read_excel("gdplev.xls", skiprows=5, index_col=4)
    df = df.iloc[2:, 5].loc["2000q1":]
    start = get_recession_start()
    end = get_recession_end()
    return df.loc[start:end].idxmin()


# In[103]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].

    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.

    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    # ts = pd.read_csv('City_Zhvi_AllHomes.csv',
    #                  header=0)
    #
    # ts.loc[:, 'State'] = ts.State.map(lambda x: states[x])
    # ts.set_index(['RegionName', 'State'], inplace=True)
    # ts = ts.T.iloc[49:]
    # ts.index = pd.DatetimeIndex(ts.index.values, freq='MS')
    # df_index_name = pd.DataFrame()
    # df_index_name['y'] = ts.index.year.astype(str)
    # df_index_name['q'] = ts.index.quarter.astype(str)
    # df_index_name['yq'] = df_index_name.y + 'q' + df_index_name.q
    # ts.index = df_index_name.yq
    # ts = ts.groupby(level=0).apply(sum, axis=0)
    filename = 'City_Zhvi_AllHomes.csv'
    housing_df = pd.read_csv(filename)

    for year in range(2000,2017):
        for quarter in range(1,5):
            if quarter == 4 and year == 2016:
                break
            cname = '{0}q{1}'.format(year, quarter)
            begin_month = (quarter-1)*3 + 1
            end_month = quarter*3
            begin_column = '{0}-{1:02d}'.format(year,begin_month)
            end_column = '{0}-{1:02d}'.format(year,end_month)
            if quarter == 3 and year == 2016:
                cname = '2016q3'
                begin_month = 6
                end_month = 8
                begin_column = '{0}-{1:02d}'.format(year,begin_month)
                end_column = '{0}-{1:02d}'.format(year,end_month)

            data = housing_df.loc[:,begin_column:end_column]

            housing_df[cname] = data.mean(axis=1)
    housing_df['State'] = housing_df['State'].apply(lambda x: states[x])
    housing_df = housing_df.set_index(['State','RegionName'])

    begin = housing_df.columns.get_loc('1996-04')
    end = housing_df.columns.get_loc('2016-08')

    housing_df.drop(housing_df.columns[begin:end+1], axis=1, inplace=True)
    housing_df.drop(housing_df.columns[0:4], axis=1, inplace=True)
    #housing_df.drop(housing_df.columns['1996-04':'2016-08'], inplace=True)
    return housing_df
    # return ts

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].

    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.

    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    ts = pd.read_csv('City_Zhvi_AllHomes.csv',
                     header=0)

    ts.loc[:, 'State'] = ts.State.map(lambda x: states[x])
    ts.set_index(['State', 'RegionName'], inplace=True)
    ts = ts.T.iloc[49:]
    ts.index = pd.DatetimeIndex(ts.index.values, freq='MS')
    ts = ts.resample('Q').sum()
    df_index_name = pd.DataFrame()
    df_index_name['y'] = ts.index.year.astype(str)
    df_index_name['q'] = ts.index.quarter.astype(str)
    df_index_name['yq'] = df_index_name.y + 'q' + df_index_name.q
    ts.index = df_index_name.yq
    return ts.T.to_excel('convert_housing2.xlsx')

convert_housing_data_to_quarters().to_excel('convert_housing.xlsx')

# In[97]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values,
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence.

    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''

    recStart = get_recession_start()
    recEnd = get_recession_end()
    recBottom = get_recession_bottom()
    housingDF = convert_housing_data_to_quarters()
    uniDF = get_list_of_university_towns()
    uniDF.set_index(['State', 'RegionName'], inplace=True)

    colInds = [colN for colN, thisCol in enumerate(housingDF.columns) if thisCol == recStart or thisCol == recBottom]
    sbDF = housingDF.loc[:,housingDF.columns[colInds[0]-1]:housingDF.columns[colInds[1]]]
    diffCols = [thisCol+'-'+sbDF.columns[colN+1] for colN, thisCol in enumerate(sbDF.columns) if colN < 4]

    uni_sb_diffDF = (pd.merge(sbDF, uniDF, how='inner', left_index=True, right_index=True)
                     )
    uni_sb_diffDF['Price Ratio'] = np.divide(uni_sb_diffDF[uni_sb_diffDF.columns[0]],uni_sb_diffDF[uni_sb_diffDF.columns[3]])
    uni_sb_diffDF.dropna(inplace=True)

    nonUni_sb_diffDF = sbDF.drop(uni_sb_diffDF.index)
    nonUni_sb_diffDF['Price Ratio'] = np.divide(nonUni_sb_diffDF.loc[:,nonUni_sb_diffDF.columns[0]],nonUni_sb_diffDF.loc[:,nonUni_sb_diffDF.columns[3]])
    nonUni_sb_diffDF.dropna(inplace=True)


    if uni_sb_diffDF['Price Ratio'].mean() > nonUni_sb_diffDF['Price Ratio'].mean():

        better = "non-university town"
    else:

        better = "university town"


    firstT = ttest_ind(uni_sb_diffDF['Price Ratio'], nonUni_sb_diffDF['Price Ratio'])
    p=firstT.pvalue

    if p>0.01:
        different = False
        return (different, p, better)

    elif p<0.01:
        different = True
        return (different, p, better)



# In[ ]:
