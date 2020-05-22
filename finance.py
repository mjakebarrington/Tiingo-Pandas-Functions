from statistics import mean
from statistics import median
import pandas as pd
import pandas_datareader.data as web

# ALL FUNCTIONS ASSUME DATAFRAME TAKES PANDAS DATAFRAME AS ARGUMENT. THESE WILL NOT WORK WITH ANY OTHER TYPE OF DATAFRAME.

def get_daily(ticker, api_key, clean=False):
    """Pulls daily data for ticker using api_key strings. Clean resets index."""
    # Ex: finance.get_daily('GOOG', 'XXXXXXX.....')
    if clean:
        df = web.get_data_tiingo(ticker, api_key=api_key)
        df = df.reset_index()
        return df
    else:
        return web.get_data_tiingo(ticker, api_key=api_key)


def add_moving_average(length, dataframe, adjusted=False):
    """Adds moving average of length to dataframe adjusted allows for calculation based on split adjusted price."""
    moving_averages = []
    # Stack for calculating mean
    memo = []

    choice = determine_adjusted(adjusted)

    for i in range(len(dataframe)):
        # Adds element to top of stack
        memo.append(dataframe[choice][i])

        if i >= (length - 1):
            # Pops first element off stack
            memo.pop(0)
            moving_averages.append(mean(memo))
        else:
            moving_averages.append(0)

    # Inserts moving_averages to dataframe.
    dataframe.insert(len(dataframe.columns), str(length) + ' MA', moving_averages, allow_duplicates = True)




def add_multi_day_change(days, dataframe, adjusted=False):
    """
    Calculates the change over x number of days.
    days = the number of days out. IE 3 will calculate how much the value changes over the course of 3 days.
    dataframe = pandas dataframe to add column to
    """

    # List of percent changes over x number of days.
    pct_changes = []

    # Sets column
    choice = determine_adjusted(adjusted)

    for element in range(len(dataframe)):
        # If the element is less than the difference between the length of the dataframe and number of days.
        # Calculate percentage difference and add to list.
        if element < (len(dataframe) - days):
            pct_changes.append(pct_change(dataframe[choice][element], dataframe[choice][element + days]))
        # Otherwise add 0 to the list.
        else:
            pct_changes.append(0)
    
    # Inset list to dataframe in new column.
    dataframe.insert(len(dataframe.columns), str(days) + ' DAY CHANGE', pct_changes, allow_duplicates = True)




def add_pct_from_sma(sma, dataframe, adjusted=False):
    """
    Calculates percent difference from SMA.
    sma = Simple Moving Average length
    dataframe = dataframe to apply updates to
    """

    # Ensures that SMA column exists. If not, creates new column. Honors split adjusted argument passed to caller.
    if (str(sma) + ' MA') not in dataframe.columns:
        add_moving_average(sma, dataframe, adjusted)

    # Sets column
    choice = determine_adjusted(adjusted)
    
    # List of values to apply
    differences_from_sma = []

    for element in range(len(dataframe)):
        # If the simple moving average for element is 0, add 0 to list.
        if dataframe[str(sma) + ' MA'][element] == 0:
            differences_from_sma.append(0)
        # Otherwise, calculate the percent difference and add result to list.
        else:
            price = dataframe[choice][element]
            simple_move = dataframe[str(sma) + ' MA'][element]
            differences_from_sma.append(pct_change(simple_move, price))
    
    # Insert list to dataframe
    dataframe.insert(len(dataframe.columns), 'Diff from ' + str(sma) + ' SMA', differences_from_sma, allow_duplicates = True)




def add_price_sma_cross(sma, dataframe, adjusted=False):
    """Determines if closing PRICE has crossed SMA and which direction."""
    # 'above' - Price has crossed above SMA from below.
    # 'below' - Price has crossed below SMA from above.
    # 'False' - Price has not crossed SMA from either direction but there IS an SMA for that cell. Most common value.
    # 'None' - There is no SMA for that cell.

    # Column of results
    crossed = []

    # Choice for split adjusted
    choice = determine_adjusted(adjusted)

    # Ensures that SMA column exists. If not, creates new column. Honors split adjusted argument passed to caller.
    if (str(sma) + ' MA') not in dataframe.columns:
        add_moving_average(sma, dataframe, adjusted)

    for element in range(len(dataframe)):
        # If there is no moving average, None.
        if dataframe[str(sma) + ' MA'][element] == 0 or element <= sma:
            crossed.append(None)
        # If price is greater than or equal to MA and previous price was less than MA, crossed above.
        elif dataframe[choice][element] >= dataframe[str(sma) + ' MA'][element] and dataframe[choice][element - 1] < dataframe[str(sma) + ' MA'][element - 1]:
            crossed.append('above')
        # If price is less than or equal to MA and previous price was greater than MA, crossed below.
        elif dataframe[choice][element] <= dataframe[str(sma) + ' MA'][element] and dataframe[choice][element - 1] > dataframe[str(sma) + ' MA'][element - 1]:
            crossed.append('below')
        # Otherwise, price did not cross. Append False.
        else:
            crossed.append(False)
    
    # Insert output to new column in pandas dataframe.
    dataframe.insert(len(dataframe.columns), 'PA crossed ' + str(sma) + ' SMA', crossed, allow_duplicates = True)




def add_sma_cross_sma(sma_one, sma_two, dataframe, adjusted=False):
    """Calculates if sma_one has crossed sma_two and which direction"""
    # 'above' - sma_one has crossed above sma_two from below
    # 'below' - sma_one has crossed below sma_two from above
    # 'False' - sma_one has not crossed sma_two but both SMAS exist
    # 'None' - one or both SMAs are missing

    # Ensures SMAS exist. If not, creates.
    if (str(sma_one) + ' MA') not in dataframe.columns:
        add_moving_average(sma_one, dataframe, adjusted)
    if (str(sma_two) + ' MA') not in dataframe.columns:
        add_moving_average(sma_two, dataframe, adjusted)
    
    sma_cross_sma = []

    # Determines larger of SMAs
    if sma_one > sma_two:
        lsma = sma_one
    elif sma_one < sma_two:
        lsma = sma_two

    for i in range(len(dataframe)):
        if i <= lsma:
            sma_cross_sma.append(None)
        elif dataframe[str(sma_one) + ' MA'][i] >= dataframe[str(sma_two) + ' MA'][i] and dataframe[str(sma_one) + ' MA'][i - 1] < dataframe[str(sma_two) + ' MA'][i - 1]:
            sma_cross_sma.append('above')
        elif dataframe[str(sma_one) + ' MA'][i] <= dataframe[str(sma_two) + ' MA'][i] and dataframe[str(sma_one) + ' MA'][i - 1] > dataframe[str(sma_two) + ' MA'][i - 1]:
            sma_cross_sma.append('below')
        else:
            sma_cross_sma.append(False)
    
    # Insert values to new end column
    dataframe.insert(len(dataframe.columns), str(sma_one) + ' SMA crossed ' + str(sma_two) + ' SMA', sma_cross_sma, allow_duplicates = True)
    




# Misc "helper functions"

def pct_change(start, end):
    """Calculates percent change from start to end. There's probably a library for this."""
    return ((end - start) / start) * 100

def determine_adjusted(adjusted):
    """Determines weather split adjusted closing price should be used."""
    if adjusted == False:
        return 'close'
    elif adjusted == True:
        return 'adjClose'
