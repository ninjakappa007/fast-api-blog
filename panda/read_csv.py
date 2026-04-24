import pandas as pd

df = pd.read_csv("pokemon.csv", index_col="Name")

# by default this print first and last 5 rows so to print everything use to_string()
# print(df)
# print(df.to_string())


# Selection techniques

# Selection by Column
# print(df["Name"].to_string())
# print(df["Weight"].to_string())

# To print specific columns
# print(df[["Name", "Height", "Weight"]].to_string())

# Selection by Rows

# To print specific row using index
# This will print entire row
# print(df.iloc[0])

# To print specific row using column value, set the column name as index_col while creating df obj
# print(df.loc["Pikachu"]) # this prints all columns

# print(df.loc["Pikachu", ["Height", "Weight"]]) # this prints specific columns

# print(df.iloc[0:11]) # this prints first 10 rows, this works same as slicing in string and list
