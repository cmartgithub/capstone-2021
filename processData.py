import yfinance as yf

#This script is for downloading options data of specified tickers

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
    longterm = []
    for line in file:
        access, near, long = line.split(' | ')
        accessdate.append(access)
        nearterm.append(near)
        longterm.append(long)
    return accessdate, nearterm, longterm

accessdate, nearterm, longerm = parse_file('Dates.txt')

print(accessdate)
