import pandas as pd
a  = pd.read_csv("iris.csv")
print(a.head())
print(a.describe(include="all"))
