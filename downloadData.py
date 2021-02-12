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

tickersymbs = grabTickers('tickersymbs.txt')

#create a new ticker class
xlb = yf.Ticker("XLB")

#show stock info
xlb.info

print(xlb.options)

opt = xlb.option_chain(xlb.options[2])

print(opt.calls)
