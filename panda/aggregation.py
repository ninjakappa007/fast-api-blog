import pandas as pd

df = pd.read_csv("pokemon.csv")

"""
Aggregate Functions : Reduces a set of values into a single summary value
Used to summarize and analyze data, Often used with the groupby() function
"""

#  Aggregate Functions for whole Dataframe
#  Find the Average of columns which value is numeric only
print(df.mean(numeric_only=True))
# Find sum of all numeric columns
print(df.sum(numeric_only=True))
# Find minimum of all numeric columns
print(df.min(numeric_only=True))
# Find maximum of all numeric columns
print(df.max(numeric_only=True))
# Find Count number of values , if its not null
print(df.count())
 
# Aggregate Functions for single Dataframe
print(df["Height"].mean())
print(df["Height"].sum())
print(df["Height"].min())
print(df["Height"].max())
print(df["Height"].count())

# Group By : group rows by some common property in rows
group = df.groupby("Type1")
print(group["Height"].mean())
print(group["Height"].max())
print(group["Height"].sum())



