import pandas as pd

df = pd.read_csv("pokemon.csv", index_col="Name")

# print(df.to_string())

pokemon = input("Enter a pokemon name : ")

try:
    print(df.loc[pokemon])
except KeyError:
    print(f"Pokemon {pokemon} not found")
