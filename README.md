# Tiingo-Pandas-Functions
A small library for performing elementary calculations on equity data from Tiingo.


# Usage

First you will need an API key from Tiingo.

### Getting Data

```python
finance.get_daily(ticker, api_key, clean = False):
```
`ticker` takes a string and determines which asset to pull fata for. `api_key` should be your Tiingo API key (as string). Set `clean` to `True` if you would like the dataframe index reset.
#### Example:
```python
df = finance.get_daily('SPY', 'XXXXX...', clean = True):
```
Will get daily values for SPY and reset the index in a new dataframe named `df`.

### Adding Moving Average Column
```python
finance.add_moving_average(length, dataframe, adjusted = False)
```
Adds a moving average of specified length to the pandas dataframe. `length` specifies the length of the simple moving average. `dataframe` specifies which dataframe to add the column to. `adjusted` determines if the split adjusted closing price should be used for calculation.

### Calculating Percent From Simple Moving Average
```python
finance.add_pct_from_sma(sma, dataframe, adjusted = False)
```
Adds a column with each day's percent difference from `sma` based on closing price if `adjusted = False` or split adjusted closing price if `adjusted = True`.
