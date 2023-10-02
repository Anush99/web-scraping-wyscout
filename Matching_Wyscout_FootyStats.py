#!/usr/bin/env python
# coding: utf-8

# In[2]:


import psycopg2
import pandas as pd
import warnings
import numpy as np
from rapidfuzz import fuzz
from fuzzywuzzy import fuzz
import re
from WyscoutBot import get_league_data
from football.soupify import convert_to_csv

get_league_data("Colombia", "League A")
convert_to_csv()

warnings.simplefilter(action='ignore', category=FutureWarning)
#
# class DatabaseMerger:
#
#     def __init__(self):
#         self.conn = psycopg2.connect(
#             database="FootyStats",
#             user="postgres",
#             password="",
#             host="localhost",
#             port="5432"
#         )
#         self.cur = self.conn.cursor()
#         print("Connected to the database.")
#
#     def merge_tables(self, season_ids):
#         df_list = []  # List to store DataFrame for each season
#         for season_id in season_ids:
#             # Get all match_ids for a given season_id
#             query = f"""
#             SELECT *
#             FROM match_id
#             WHERE season_id = {season_id};
#             """
#             self.cur.execute(query)
#             result = self.cur.fetchall()
#             print(f"Number of match_id records for season {season_id}: {len(result)}")
#
#             # Get all team_ids for a given season_id
#             query = f"""
#             SELECT *
#             FROM teams
#             WHERE season_id = {season_id};
#             """
#             self.cur.execute(query)
#             result = self.cur.fetchall()
#             print(f"Number of team records for season {season_id}: {len(result)}")
#
#             # Get all records from detailed_match_data that have a match_id in the match_id table for the given season_id
#             query = f"""
#             SELECT *
#             FROM detailed_match_data
#             WHERE id IN (
#                 SELECT match_id
#                 FROM match_id
#                 WHERE season_id = {season_id}
#             );
#             """
#             self.cur.execute(query)
#             result = self.cur.fetchall()
#             print(f"Number of detailed_match_data records for matches in season {season_id}: {len(result)}")
#
#             # Now merge everything together
#             query = f"""
#             SELECT
#                 match_id.match_id,
#                 home_teams.team_name as home_team,
#                 away_teams.team_name as away_team,
#                 detailed_match_data.*
#             FROM
#                 match_id
#             INNER JOIN
#                 teams as home_teams ON match_id.homeID = home_teams.team_id AND home_teams.season_id = {season_id}
#             INNER JOIN
#                 teams as away_teams ON match_id.awayID = away_teams.team_id AND away_teams.season_id = {season_id}
#             INNER JOIN
#                 detailed_match_data ON match_id.match_id = detailed_match_data.id
#             WHERE
#                 match_id.season_id = {season_id};
#             """
#             self.cur.execute(query)
#             result = self.cur.fetchall()
#             print(f"Number of merged records for season {season_id}: {len(result)}")
#
#             columns = [desc[0] for desc in self.cur.description]
#             df = pd.DataFrame(result, columns=columns)
#             df_list.append(df)  # Add DataFrame to the list
#
#         return pd.concat(df_list, ignore_index=True)  # Concatenate all DataFrames
#
# data = pd.read_csv('r"C:\Users\oskar\Downloads\eng_4th.csv"')
#
# # Convert the 'season_id' column into a list.
# season_ids = data['season_id'].tolist()
#
# db_merger = DatabaseMerger()
#
# merged_df = db_merger.merge_tables(season_ids)

df = pd.read_csv('spa_ter_14_18.csv')

df = df.sort_values(by='date_unix', ascending=True)

# Convert Unix timestamps to datetime
df['date_unix'] = pd.to_datetime(df['date_unix'], unit='s')

# Convert datetime to DD_MM_YYYY format
df['date'] = df['date_unix'].dt.strftime('%d_%m_%Y')

df = df.loc[:, ~df.columns.duplicated()]

df

# In[3]:

# Concat all csv files
folder_path = "/Users/anushik/Downloads/wyscout/football/"
files = os.listdir(folder_path)
csv_files = [file for file in files if file.endswith(".csv")]
dataframes = []
for i, csv_file in enumerate(csv_files):
    file_path = os.path.join(folder_path, csv_file)
    if i == 0:
        # For the first file, include the header
        data = pd.read_csv(file_path)
    else:
        data = pd.read_csv(file_path, header=None, skiprows=1)
    dataframes.append(data)
combined_data = pd.concat(dataframes, ignore_index=True)
combined_data.to_csv("combined_data.csv", index=False)

data = pd.read_csv("combined_data.csv", encoding='ISO-8859-1')

data


# In[4]:


# Step 1: Define a function to parse the 'match' column
def parse_match(match):
    pattern = r'(.+?)\s(\d+:\d+)\s(.+)'
    match_data = re.search(pattern, match)
    if match_data:
        home_team = match_data.group(1)
        score = match_data.group(2)
        away_team = match_data.group(3)
        return pd.Series([home_team.strip(), away_team.strip(), score])
    else:
        return pd.Series([None, None, None])


# Step 2: Apply the function to the 'match' column
data[['home_team', 'away_team', 'score']] = data['match'].apply(parse_match)

# Step 3: Drop the 'score' column
data.drop(columns=['score'], inplace=True)

# Print the 'home_team' and 'away_team' columns
print(data[['home_team', 'away_team']])

col_names = data.columns

col_names_1 = col_names[:4]
col_names_2 = col_names[4:]

# Step 2: Create team a (home team) and team b (away team) dataframes based on the team name
df_a = data[data['team'] == data['home_team']].copy()
df_b = data[data['team'] == data['away_team']].copy()

# Step 3: Rename the columns in df_a and df_b
df_a.columns = [col if col in col_names_1 else col + '_a' for col in df_a.columns]
df_b.columns = [col if col in col_names_1 else col + '_b' for col in df_b.columns]

# Step 4: Reset the index of both dataframes
df_a.reset_index(drop=True, inplace=True)
df_b.reset_index(drop=True, inplace=True)

# Step 5: Join df_a and df_b on the shared columns
wyscout_df = df_a.merge(df_b, how='outer', left_on=list(col_names_1), right_on=list(col_names_1))

# Step 6: Remove NaN values
wyscout_df = wyscout_df.dropna()

# Step 6: Rename the specified columns to remove the '_a' suffix
wyscout_df.rename(
    columns={'date_a': 'date', 'match_a': 'match', 'competition_a': 'competition', 'duration_a': 'duration'},
    inplace=True)
wyscout_df.rename(
    columns={'team_a': 'home_team1', 'team_b': 'away_team1', 'goals_a': 'homeGoalCount1', 'goals_b': 'awayGoalCount1',
             'date': 'date1'}, inplace=True)

# Convert 'homeGoalCount' and 'awayGoalCount' to integer
wyscout_df['homeGoalCount1'] = wyscout_df['homeGoalCount1'].astype(int)
wyscout_df['awayGoalCount1'] = wyscout_df['awayGoalCount1'].astype(int)

wyscout_df['date1'] = pd.to_datetime(wyscout_df['date1'], format='%d/%m/%Y')
wyscout_df['date1'] = wyscout_df['date1'].dt.strftime('%d_%m_%Y')

# Display the first few rows of the updated DataFrame
wyscout_df

# In[5]:


wyscout_df.to_csv("22.csv", index=False)

wyscout_df = wyscout_df.drop_duplicates(subset='match', keep='last')

wyscout_df = wyscout_df[wyscout_df['competition'] == 'England. League Two']

wyscout_df

# In[6]:


# Reset the indices of df
df = df.reset_index(drop=True)

from fuzzywuzzy import fuzz


def get_extra_points(string1, string2):
    points = 0
    for word1 in string1.split():
        for word2 in string2.split():
            if len(word1) >= 4 and len(word2) >= 4 and word1 == word2:
                points += 30
    return points


def find_matches(wyscout_df, df):
    # Placeholder for the match_ids
    match_ids = []

    # Loop through each row in wyscout_df
    for idx_w, row_w in wyscout_df.iterrows():

        # Initialize the best score for this row
        best_score = 0
        best_match_id = None

        # Loop through each row in df
        for idx_d, row_d in df.iterrows():

            # Calculate the fuzz ratio for home_team and away_team
            home_team_score = fuzz.ratio(row_w['home_team1'], row_d['home_team']) + get_extra_points(
                row_w['home_team1'], row_d['home_team'])
            away_team_score = fuzz.ratio(row_w['away_team1'], row_d['away_team']) + get_extra_points(
                row_w['away_team1'], row_d['away_team'])

            # Check if home_team and away_team score is above 70, homeGoalCount, awayGoalCount match exactly and dates are the same
            if home_team_score > 50 and away_team_score > 50 and row_w['homeGoalCount1'] == row_d['homeGoalCount'] and \
                    row_w['awayGoalCount1'] == row_d['awayGoalCount'] and row_w['date1'] == row_d['date']:
                score = (home_team_score + away_team_score) / 2
                if score > best_score:
                    best_score = score
                    best_match_id = row_d['match_id']

        if best_match_id is not None:
            print(f"\nBest match for wyscout_df row {idx_w} is match_id {best_match_id} with score {best_score}")
            match_ids.append(best_match_id)
            wyscout_df.loc[idx_w, 'match_id'] = int(
                best_match_id)  # Assign the best match_id only to the row in wyscout_df with the best match

    # Print the matched match_ids
    print(f"\nMatched match_ids: {match_ids}")

    return wyscout_df  # Return wyscout_df with Match_ID


# Return wyscout_df with Match_ID


# Call the function
wyscout_df_with_matches = find_matches(wyscout_df, df)

# In[7]:


wyscout_df.to_csv("check.csv", index=False)

wyscout_df = wyscout_df.drop_duplicates(subset='match_id', keep='last')

wyscout_df

# In[8]:
#
#
# from sqlalchemy import create_engine
#
# database_connection_string = 'postgresql://postgres:@localhost:5432/FootyStats'
#
# # Create the database engine
# engine = create_engine(database_connection_string)
#
# # Write the DataFrame to the database
# wyscout_df.to_sql('wyscout_detailed_match', engine, if_exists='append', index=False)

# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:
