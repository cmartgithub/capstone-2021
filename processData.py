import os
import pandas as pd

#This script is for processing of options data of specified tickers

def grabTickers(filename):
    """
    Parses the specified text file containing the ticker symbols in the following format:
        XLB | XLE | XLK | ...
    Returns a list tickersymbs of 'tickersymb',...
    """
    f = open(filename,'r')
    tickersymbs = []
    for x in f:
        tickersymbs.append(x)
    f.close()
    return tickersymbs[0].split()

#Parse a text file of exp dates and access dates given a ticker symbol.
#return expry dates and access dates
#textfile:
#ACCESS DATE | NEAR TERM | LONG TERM
#-----------------
# 02-03-2021 | 2021-02-12 | 2021-03-12
#-----------------
def parse_file(filename):
    file = open(filename, "r")
    accessdate = []
    nearterm = []
    nextterm = []
    for line in file:
        access, near, next = line.split(' | ')
        accessdate.append(access)
        nearterm.append(near)
        nextterm.append(next.strip())
    return accessdate, nearterm, nextterm

#Returns file paths of nearterm and nextterm excel files given an option ticker
#and date for vix calculation

def grabDataPaths(tickersymb,date,nearterm,nextterm):
    filepath = os.getcwd()+'/Data/'+tickersymb
    for entry in os.listdir(filepath):
        if date in entry and nearterm in entry:
            nearTermPath = os.path.join(filepath,entry)
        elif date in entry and nextterm in entry:
            nextTermPath = os.path.join(filepath,entry)
    return nearTermPath, nextTermPath

#Return the relavant data needed for calculating the VIX given a nearterm filepath
#and nextterm filepath
def grabData(nearTermPath,nextTermPath):
    #Need: Strike, Midpoint,
    df_near = pd.read_csv(nearTermPath)
    df_next = pd.read_csv(nextTermPath)
    df_near_call = df_near[df_near['Type'].isin(['Call'])]
    df_next_call = df_next[df_next['Type'].isin(['Call'])]
    df_near_put = df_near[df_near['Type'].isin(['Put'])]
    df_next_put = df_next[df_next['Type'].isin(['Put'])]
    #Get near and next term strike prices for calls and puts
    near_term_call_strike = df_near_call.loc[:,'Strike'].values
    next_term_call_strike = df_next_call.loc[:,'Strike'].values
    near_term_put_strike = df_near_put.loc[:,'Strike'].values
    next_term_put_strike = df_next_put.loc[:,'Strike'].values
    #get near and next term midpoints for calls and puts
    near_term_call_mid = df_near_call.loc[:,'Midpoint'].values
    next_term_call_mid = df_next_call.loc[:,'Midpoint'].values
    near_term_put_mid = df_near_put.loc[:,'Midpoint'].values
    next_term_put_mid = df_next_put.loc[:,'Midpoint'].values

    return near_term_call_strike,next_term_call_strike, near_term_put_strike, next_term_put_strike,near_term_call_mid,next_term_call_mid,near_term_put_mid,next_term_put_mid


tickers = grabTickers('tickersymbs.txt')

#Return the access dates and nearterm, and nextterm call expry dates
accessdate, nearterm, nextterm = parse_file('Dates.txt')

#TESTING
near, next = grabDataPaths(tickers[0],accessdate[0],nearterm[0],nextterm[0])
near_term_call_strike,next_term_call_strike, near_term_put_strike, next_term_put_strike,near_term_call_mid,next_term_call_mid,near_term_put_mid,next_term_put_mid = grabData(near,next)
