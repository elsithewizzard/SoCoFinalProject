import pandas as pd
import os

basepath = os.getcwd()
file_path = os.path.join(basepath, "Analysis", "data", "games_clean_summary.csv")

df = pd.read_csv(file_path)

print(f"Full Dataset: Total games: {len(df)}")
