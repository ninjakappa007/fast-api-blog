import pandas as pd

"""
A Pandas DataFrame is a two-dimensional, size-mutable, and potentially heterogeneous tabular data
structure with labeled axes (rows and columns).
"""

data = {
    "Name" : ["Ashu", "Chunu", "Pinu"],
    "Age" : [28, 26, 24],
}

# df = pd.DataFrame(data)
df = pd.DataFrame(data, index=["Emp 1", "Emp 2", "Emp 3"])

# print full dataframe
# print(df)

# geta single value using index
# print(df.loc["Emp 1"])

# Add a new column
df["Job"] = ["IT", "Health", "Student"]
print(df)

# Add new row, create a new row and concatinate, same way we can add multiple rows and concat
new_row = pd.DataFrame(
    [
        {
            "Name" : "Kunu",
            "Age" : 28,
            "Job" : "Student"
        }, 
        {
            "Name" : "Raja",
            "Age" : 28,
            "Job" : "Student"
        }, 
        
    ]
    , index=["Emp 4", "Emp 5"])

df  = pd.concat([df, new_row])
print(df)


# use conditionals
# print(df[df >= 28])