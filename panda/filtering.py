import pandas as pd

df = pd.read_csv("pokemon.csv", index_col="Name")

# Filtering : Keep the rows that match the condition

# print(df.loc["Pikachu"])

# print pokemon with certain height
tall_pokemon = df[df["Height"] >= 2 ] # this returns a Series
heavy_pokemon = df[df["Weight"] > 400]
legendary_pokemon = df[df["Legendary"] == 1]
# using OR operator
water_pokemon = df[(df["Type1"] == "Water") | (df["Type2"] == "Water")]
# using AND operator
water_and_ice_pokemon = df[(df["Type1"] == "Water") & (df["Type2"] == "Ice")]

# print(tall_pokemon.to_string())
# print(heavy_pokemon.to_string())
# print(legendary_pokemon.to_string())
# print(water_pokemon)
print(water_and_ice_pokemon)

