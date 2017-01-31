
# coding: utf-8

# ---
#
# _You are currently looking at **version 1.1** of this notebook.
# To download notebooks and datafiles, as well as get help on Jupyter notebooks
# in the Coursera platform, visit the [Jupyter Notebook FAQ]
# (https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course
# resource._
#
# ---

# # Assignment 2 - Pandas Introduction
# All questions are weighted the same in this assignment.
# ## Part 1
# The following code loads the olympics dataset (olympics.csv), which was
# derrived from the Wikipedia entry on [All Time Olympic Games Medals]
# (https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table), and does
# some basic data cleaning.
#
# The columns are organized as # of Summer games, Summer medals, # of Winter
# games, Winter medals, total # number of games, total # of medals. Use this
# dataset to answer the questions below.

# In[ ]:
import numpy as np
import pandas as pd

df = pd.read_csv('olympics.csv', index_col=0, skiprows=1)

for col in df.columns:
    if col[:2]=='01':
        df.rename(columns={col:'Gold'+col[4:]}, inplace=True)
    if col[:2]=='02':
        df.rename(columns={col:'Silver'+col[4:]}, inplace=True)
    if col[:2]=='03':
        df.rename(columns={col:'Bronze'+col[4:]}, inplace=True)
    if col[:1]=='№':
        df.rename(columns={col:'#'+col[1:]}, inplace=True)

names_ids = df.index.str.split('\s\(') # split the index by '('

df.index = names_ids.str[0] # the [0] element is the country name (new index)
df['ID'] = names_ids.str[1].str[:3] # the [1] element is the abbreviation or ID (take first 3 characters from that)

df = df.drop('Totals')
df.head()


# ### Question 0 (Example)
#
# What is the first country in df?
#
# *This function should return a Series.*

# In[ ]:

# You should write your whole answer within the function provided. The autograder will call
# this function and compare the return value against the correct solution value
def answer_zero():
    # This function returns the row for Afghanistan, which is a Series object. The assignment
    # question description will tell you the general format the autograder is expecting
    return df.iloc[0]

# You can examine what your function returns by calling it in the cell. If you have questions
# about the assignment formats, check out the discussion forums for any FAQs
answer_zero()


# ### Question 1
# Which country has won the most gold medals in summer games?
#
# *This function should return a single string value.*

# In[ ]:

def answer_one():
    res = df.loc[:,"Gold"].idxmax()
    return res

# ### Question 2
# Which country had the biggest difference between their summer and winter gold medal counts?
#
# *This function should return a single string value.*

# In[ ]:

def answer_two():
    summer = df.loc[:, "Gold"]
    winter = df.loc[:, "Gold.1"]
    diff = summer - winter
    res = diff.idxmax()
    return res


# ### Question 3
# Which country has the biggest difference between their summer gold medal counts
# and winter gold medal counts relative to their total gold medal count?
#
# $$\frac{Summer~Gold - Winter~Gold}{Total~Gold}$$
#
# Only include countries that have won at least 1 gold in both summer and winter.
#
# *This function should return a single string value.*

# In[ ]:
def answer_three():
    cnd = (df.loc[:, ["Gold", "Gold.1"]] > 0).all(1)
    summer = df.loc[cnd, "Gold"]
    winter = df.loc[cnd, "Gold.1"]
    total = df.loc[cnd, "Gold.2"]
    res = abs(summer - winter) / total
    res = res.idxmax()
    return res


# ### Question 4
# Write a function to update the dataframe to include a new column called "Points"
# which is a weighted value where each gold medal counts for 3 points, silver medals for 2 points, and bronze mdeals for 1 point. The function should return only the column (a Series object) which you created.
#
# *This function should return a Series named `Points` of length 146*

# In[ ]:

def answer_four():
    df["Points"] = (df.iloc[:,-5:-2] * np.array([3,2,1])).sum(1)
    return df.Points


# ## Part 2
# For the next set of questions, we will be using census data from the [United States Census Bureau]
# (http://www.census.gov/popest/data/counties/totals/2015/CO-EST2015-alldata.html).
# Counties are political and geographic subdivisions of states in the United States.
# This dataset contains population data for counties and states in the US from 2010 to 2015.
# [See this document](http://www.census.gov/popest/data/counties/totals/2015/files/CO-EST2015-alldata.pdf)
# for a description of the variable names.
#
# The census dataset (census.csv) should be loaded as census_df. Answer questions using this as appropriate.
#
# ### Question 5
# Which state has the most counties in it? (hint: consider the sumlevel key carefully! You'll need this for future questions too...)
#
# *This function should return a single string value.*

# In[ ]:

census_df = pd.read_csv('census.csv')
census_df.head()
cndkey = census_df.SUMLEV == 50
dw = census_df[cndkey].copy()

# In[ ]:

def answer_five():
    res = dw.pivot_table(index="STNAME", values="COUNTY", aggfunc="count")
    res = res.idxmax()
    return res


# ### Question 6
# Only looking at the "three most populous counties for each state", what are the three most populous states (in order of highest population to lowest population)?
#
# *This function should return a list of string values.*

# In[ ]:

def answer_six():
    v = "CENSUS2010POP"
    f = lambda x: x.sort_values(v, ascending=False)[:3].sum()
    res = dw.pivot_table(index="STNAME", values=v, aggfunc=f)
    res = res.sort_values(ascending=False).iloc[:3].index.tolist()
    return res


# ### Question 7
# Which county has had the largest absolute change in population within the period 2010-2015? (Hint: population values are stored in columns POPESTIMATE2010 through POPESTIMATE2015, you need to consider all six columns.)
#
# e.g. If County Population in the 5 year period is 100, 120, 80, 105, 100, 130, then its largest change in the period would be |130-80| = 50.
#
# *This function should return a single string value.*

# In[ ]:

def answer_seven():
    v = "CTYNAME"
    popmax = dw.loc[:,"POPESTIMATE2010":"POPESTIMATE2015"].max(1)
    popmin = dw.loc[:,"POPESTIMATE2010":"POPESTIMATE2015"].min(1)
    ind = abs(popmax - popmin).idxmax()
    res = dw.loc[ind, v]
    return res


# ### Question 8
# In this datafile, the United States is broken up into four regions using the "REGION" column.
#
# Create a query that finds the counties that belong to regions 1 or 2, whose name starts with 'Washington', and whose POPESTIMATE2015 was greater than their POPESTIMATE 2014.
#
# *This function should return a 5x2 DataFrame with the columns = ['STNAME', 'CTYNAME'] and the same index ID as the census_df (sorted ascending by index).*

# In[ ]:

def answer_eight():
    f = lambda x: x.startswith("Washington")
    cnd1 = (dw.REGION == 1) | (dw.REGION == 2)
    cnd2 = dw.CTYNAME.map(f)
    cnd3 = dw.POPESTIMATE2015 > dw.POPESTIMATE2014
    cnd = cnd1 & cnd2 & cnd3
    res = dw[cnd].loc[:,["STNAME", "CTYNAME"]]
    res = res.sort_index(ascending=True)
    return res
