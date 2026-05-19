import pandas as pd
import os

repo_root = os.getcwd()
file_path = os.path.join(repo_root, "Data Collection", "MASTER_ALL_DATA.csv")

df = pd.read_csv(file_path)

print(f"Full Dataset: Total games: {len(df)}")
df.head()
