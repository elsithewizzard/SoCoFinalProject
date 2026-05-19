import pandas as pd
import numpy as np

# 1. Load the files
df_kaggle = pd.read_csv('games_2023_filtered.csv') # Your 1751 clean games
df_reddit = pd.read_csv('games_reddit.csv')
df_master = pd.read_csv('games_master_player_counts.csv')

# 2. Clean Antonio's Master File (Convert "1,093" strings to integers)
df_master['Peak Players'] = df_master['Peak Players'].str.replace(',', '').astype(float)

# 3. Aggregate the Master File: Get the MAX peak players ever recorded per game
df_peak_counts = df_master.groupby('app_id')['Peak Players'].max().reset_index()
df_peak_counts.rename(columns={'Peak Players': 'peak_players_master'}, inplace=True)

# 4. START THE JOIN
# Base: Your clean Kaggle games
df_analysis = df_kaggle[['app_id', 'name', 'price', 'recommendations', 'median_playtime_forever']].copy()

# Join with Reddit Metrics
df_analysis = pd.merge(df_analysis, df_reddit[['app_id', 'engagement', 'valence', 'n_posts']], on='app_id', how='left')

# Join with Antonio's Peak Counts
df_analysis = pd.merge(df_analysis, df_peak_counts, on='app_id', how='left')

# 5. Final Cleanup
# Create B2P vs F2P category for H3
df_analysis['is_f2p'] = df_analysis['price'] == 0
df_analysis['price_group'] = df_analysis['is_f2p'].map({True: 'F2P', False: 'B2P'})

# Fill Reddit NaNs with 0 (No posts found = 0 engagement)
df_analysis['engagement'] = df_analysis['engagement'].fillna(0)
df_analysis['n_posts'] = df_analysis['n_posts'].fillna(0)

print(f"Final Analysis Set: {len(df_analysis)} games ready for stats!")