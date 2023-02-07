
import numpy as np
import pandas as pd

# Wikipedia psedocode for bisection root finding algorithm
"""
INPUT: Function f, 
       endpoint values a, b, 
       tolerance TOL, 
       maximum iterations NMAX
CONDITIONS: a < b, 
            either f(a) < 0 and f(b) > 0 or f(a) > 0 and f(b) < 0
OUTPUT: value which differs from a root of f(x) = 0 by less than TOL
 
N ← 1
while N ≤ NMAX do // limit iterations to prevent infinite loop
    c ← (a + b)/2 // new midpoint
    if f(c) = 0 or (b – a)/2 < TOL then // solution found
        Output(c)
        Stop
    end if
    N ← N + 1 // increment step counter
    if sign(f(c)) = sign(f(a)) then a ← c else b ← c // new interval
end while
Output("Method failed.") // max number of steps exceeded
""";



def bisection(f, a, b, TOL, NMAX = 100):
    assert a < b
    assert (f(a) < 0 and f(b) > 0) or (f(a) > 0 and f(b) < 0)

    N = 1
    a = a
    b = b
    while N <= NMAX: # limit iterations to prevent infinite loop
        c = (a+b)/2 # new midpoint
        if f(c) == 0 or (b - a)/2 < TOL:
            return c
        N += 1
        if np.sign(f(c)) == np.sign(f(a)):
            a = c
        else:
            b = c # new interval

    print(f"Bisection search failed to converge in {NMAX} iterations")
    return c


# method to parse all the sheets of the isx Excel files
def parse_xls(path: str):
    """
    Returns an array of data frames, one for each sheet.
    Strike prices with incomplete history (NAs in the price(s) columns) are ignored. 
    """
    custom_date_parser = lambda x: pd.to_datetime(x, format='%d.%m.%Y', errors='ignore')

    dfs = [] # save parsed sheets here
    for sheet in range(0,11):
        custom_date_parser = lambda x: pd.to_datetime(x, format='%d.%m.%Y')
        df = pd.read_excel('isx2010C.xls',parse_dates=True, date_parser=custom_date_parser,decimal=',' ,sheet_name = sheet)
        df.columns = ['TTM', *df.columns[1:-3], 'SP100', 'r','date']
        df['r'] = df['r']/100. # convert from basispoints to percentage
        df[df.columns[-1]] = pd.to_datetime(df['date'], dayfirst=True) # convert date column to datetime
        
        # remove last row if full of NaNs
        if not df.iloc[-1:,1:].count(1).all(axis=None):
            df = df[0:-1]

        # drop strikes with incomplete history
        df = df.loc[df.index.notnull()]
        df = df.dropna(axis='columns',how='any')

        # fix outliers, ie values that are 1000 times to large
        for strike in df.columns[1:-3]:
            df[strike] = df[strike].apply(lambda x: float(x) if type(x)!= str else float(x.replace(',','.')))
            df[strike] = df[strike].apply(lambda x: x if x < 1000 else x/1000.0)

        dfs.append(df)
    
    return dfs