# %%
import requests
import json
import random
import numpy as np

import pandas as pd

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

random.seed(743)

uri = 'http://api.football-data.org/v4/competitions/WC/teams'
headers = { 'X-Auth-Token': '704794d40b6a4f02a48fc0063c2674c9' }

response = requests.get(uri, headers=headers)

teams=[]
for team in response.json()['teams']:
  teams.append(team["name"])

random.shuffle(teams)

df = pd.DataFrame(data=teams, columns=["Team"])

owners = ["carlos","gaffer", "big man", "foggy", "killah", "ed", "millerman", "greg", "jaime"]

owners_expanded = []
for i in range(4):
  random.shuffle(owners)
  for owner in owners:
    owners_expanded.append(owner)

df["Owner"] = owners_expanded[:32]
df.set_index("Team", drop=True, inplace=True)

for col in ["Played", "Won", "Drawn", "Lost", "Points"]:
  df[col] = np.zeros(32, dtype=int)

uri = "http://api.football-data.org/v4/competitions/WC/standings"
headers = { 'X-Auth-Token': '704794d40b6a4f02a48fc0063c2674c9' }

response = requests.get(uri, headers=headers)

for group in response.json()['standings']:
  for position in group['table']:
    name = position['team']['name']
    df.loc[name, 'Played'] = position["playedGames"]
    df.loc[name, 'Won'] = position["won"]
    df.loc[name, 'Drawn'] = position["draw"]
    df.loc[name, 'Lost'] = position["lost"]
    df.loc[name, 'Points'] = position["points"]

df.sort_values("Owner", ascending=False, inplace=True)

df2 = df.groupby("Owner").sum()
df2["# Teams"] = df.groupby(['Owner'])['Played'].count()
df2["Points per team"] = df2["Points"] / df2["# Teams"]
df2.sort_values("Points per team", inplace=True, ascending=False)

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file('service-credentials.json', scopes=scopes)

gc = gspread.authorize(credentials)
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

spreadsheet_key = '1suPvKuZ1PyfS2g4eP6pMplpC9TNa44eVlkbtHnmF20c'

gs = gc.open_by_key(spreadsheet_key)

ws = gs.worksheet("teams_table")
ws.clear()
set_with_dataframe(worksheet=ws, dataframe=df, include_index=True,
include_column_header=True, resize=True)
ws.format('A1:G1', {'textFormat': {'bold': True}})

teams_through=["Senegal", "Netherlands", "France", "Portugal", "United States", "England", "Brazil", "Australia", "Poland", "Argentina"]
teams_out=["Ecuador", "Qatar", "Wales", "Iran", "Canada", "Tunisia", "Denmark", "Mexico", "Saudi Arabia"]

for team in teams_through:
  row_number = df.index.get_loc(team) 
  ws.format('A{0}:G{0}'.format(row_number+2), {'textFormat': {'bold': True}})

for team in teams_out:
  row_number = df.index.get_loc(team) 
  ws.format('A{0}:G{0}'.format(row_number+2), {'textFormat': {'foregroundColorStyle': {'rgbColor': {'red': 1.0, 'green': 0.1, 'blue': 0.1, 'alpha': 0.1}}}})

ws = gs.worksheet("owners_table")
ws.clear()
set_with_dataframe(worksheet=ws, dataframe=df2, include_index=True,
include_column_header=True, resize=True)
ws.format('A1:H1', {'textFormat': {'bold': True}})
ws.format('H2:H10', {'numberFormat': {'type': 'Number', 'pattern': '#0.0'}})
