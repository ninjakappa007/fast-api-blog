import pandas as pd

df = pd.read_csv("pokemon.csv")

"""
Data Cleaning : Process of fixing/cleaning incomplete, incorrect or irrelevant data.
"""
print(df)
# drop not required columns
df = df.drop(columns = ["Name"]) # this returns modified Dataframe
print(df)

df = df.dropna(subset=["Type2"]) # drop not available values, so dropna
print(df.to_string())
print(df["No"].count())

# Handle missing data
df = df.fillna({"Type2" : "None"})

# Fix inconsistant value
df["Type1"] = df["Type1"].replace({"Grass" : "GRASS", "Fire": "FIRE", "Water": "WATER"})

print(df.to_string())