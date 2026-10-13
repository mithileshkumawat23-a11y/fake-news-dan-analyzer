import pandas as pd

data = pd.read_csv("ai-service/data/processed/news_dataset.csv")

print("Dataset Shape:", data.shape)
print("\nColumn Names:")
print(data.columns.tolist())

print("\nFirst News Text:")
print(data.iloc[0].to_dict())

print("\nLabel Counts:")
print(data["label"].value_counts())

print("\nSample News:")
print(data[["title", "label"]].head(10))

print("\nMissing Labels:")
print(data["label"].isnull().sum())

print("\nUnique Labels:")
print(data["label"].unique())