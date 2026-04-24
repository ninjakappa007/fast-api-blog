import pandas as pd

"""
In Pandas, a Series is a one-dimensional, labeled array capable of holding data of any type,
such as integers, strings, floating-point numbers, and Python objects
"""


# data = [100, 101, 102, 103, 104]

# series = pd.Series(data)
# series = pd.Series(data, index = ["A", "B", "C"])

# get and modify specific indexes , if custom index also we can pass that
# series.iloc[1] = 2000
# print(series.iloc[1])

# series.loc[0] = 99
# print(series.loc[0])

# Filter based on condition
# print(series[series >= 102])


calories = {
    "Day 1" : 1750,
    "Day 2" : 2100,
    "Day 3" : 1800,
    "Day 4" : 1900,
    "Day 5" : 2700
}

series = pd.Series(calories)

# print(series)

# access certain property

print(series.loc['Day 5'])

# modify properties
series.loc["Day 3"] += 100
print("Day 3 Value ",series.loc["Day 3"])

print(series[series > 1800])



