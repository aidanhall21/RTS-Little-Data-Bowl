####
## THIS NOTEBOOOK GOES THROUGH EACH OF THE GIVEN CONTEST FILES AND 
## PARSES CAPTAIN/FLEX OWNERSHIP AS WELL AS TOTAL DUPLICATIONS FOR EACH SUBMITTED LINEUP

import os
from os.path import isfile, join
import pandas as pd
import numpy as np
import re

train_or_test = input('Input 1 to parse training data, 2 for test data: ')

## IM USING DraftKings_Contest_Files_1 FOR TRAINING DATA AND DraftKings_Contest_Files_2 FOR TEST DATA
path = ''
if train_or_test == '1': path = os.getcwd() + '/DraftKings_Contest_Files_1'
elif train_or_test == '2': path = os.getcwd() + '/DraftKings_Contest_Files_2'
else: raise Exception("Invalid Input")

contest_files = [f for f in os.listdir(path) if f[-4:] == '.csv']


## THESE FILES HELP US MATCHUP PLAYER IDS AND NAMES
nfl_players = pd.read_csv('NFL_PLAYERS.csv')
nfl_teams = pd.read_csv('NFL_TEAMS.csv')

nfl_players = nfl_players[['id', 'draftkings_name']]
nfl_players = nfl_players.dropna()
nfl_players = nfl_players.rename(columns={'draftkings_name': 'name'})
nfl_players = nfl_players.replace({'Van Jefferson': 'Van Jefferson Jr.', 'John Kelly Jr.': 'John Kelly'})

nfl_teams = nfl_teams[['id', 'name']]
nfl_teams = nfl_teams.dropna()
nfl_teams = nfl_teams.replace({'Commanders': 'WAS Football Team'})

dk_name_ids_cpt = pd.concat([nfl_players, nfl_teams]).reset_index(drop=True)
dk_name_ids_cpt = dk_name_ids_cpt.rename(columns={'id': 'cpt_id', 'name': 'CPT'})
dk_name_ids_flex = pd.concat([nfl_players, nfl_teams]).reset_index(drop=True)
dk_name_ids_flex = dk_name_ids_flex.rename(columns={'id': 'flex_id', 'name': 'FLEX'})

showdown_links = pd.read_csv('Showdown_Links.csv')
showdown_projections = pd.read_csv('NFL_SHOWDOWN_PROJECTIONS.csv')
showdown_projections['full_name'] = showdown_projections.apply(lambda r: r['first_name'] + ' ' + r['last_name'] if r['position'] != 'DST' else r['last_name'], axis=1)
cpt_showdown_projections_merge_df = showdown_projections[['slate_id', 'player_id', 'position', 'salary', 'projection', 'team_id', 'team_name', 'opponent_id', 'opponent_name', 'home']]
cpt_showdown_projections_merge_df = cpt_showdown_projections_merge_df.rename(columns={
    'slate_id': 'SLATE ID',
    'player_id': 'CPT_PLAYER_ID',
    'position': 'CPT_POSITION',
    'salary': 'CPT_SALARY',
    'projection': 'CPT_BASE_PROJECTION',
    'team_id': 'CPT_TEAM_ID',
    'team_name': 'CPT_TEAM_NAME',
    'opponent_id': 'CPT_OPP_ID',
    'opponent_name': 'CPT_OPP_NAME',
    'home': 'CPT_HOME_AWAY'
})

flex_showdown_projections_merge_df = showdown_projections[['slate_id', 'player_id', 'position', 'salary', 'projection', 'team_id', 'team_name', 'opponent_id', 'opponent_name', 'home']]
flex_showdown_projections_merge_df = flex_showdown_projections_merge_df.rename(columns={
    'slate_id': 'SLATE ID',
    'player_id': 'FLEX_PLAYER_ID',
    'position': 'FLEX_POSITION',
    'salary': 'FLEX_SALARY',
    'projection': 'FLEX_BASE_PROJECTION',
    'team_id': 'FLEX_TEAM_ID',
    'team_name': 'FLEX_TEAM_NAME',
    'opponent_id': 'FLEX_OPP_ID',
    'opponent_name': 'FLEX_OPP_NAME',
    'home': 'FLEX_HOME_AWAY'
})

### GATHER GAME AND SLATE IDS FOR EACH CONTEST STANDINGS FILE
game_ids = {}
slate_ids = {}
for i in range(len(showdown_links.index)):
    l = showdown_links.loc[i, :].tolist()
    fid = str(l[4])
    gid = l[6]
    sid = l[7]
    
    if fid in game_ids: pass
    else: game_ids[fid] = gid
        
    if fid in slate_ids: pass
    else: slate_ids[fid] = sid

df_list = []
cpt_to_flex_df_list = []

for i in range(len(contest_files)):
    ## READ IN EACH CONTEST FILE CSV
    cs = pd.read_csv(path + '/' + contest_files[i])
    
    id_string = contest_files[i].replace('.', '-')
    id_string_split = id_string.split('-')
    contest_id = id_string_split[2]

    ## KEEPS TRACK OF TOTAL EXPOSURE FOR EACH PLAYER LISTED AS A CAPTAIN
    cpt_exp = {}
    
    ## KEEPS TRACK OF THE COUNTS OF EACH PLAYER PLAYED AS A FLEX GIVEN A SPECIFIC PLAYER AS CAPTAIN
    cpt_to_flex_dict = {}
    
    ## KEEPS TRACK OF TOTAL EXPOSURE FOR EACH PLAYER LISTED AS A CAPTAIN
    flex_exp = {}
    
    ## THIS DICTIONARY TRACKS THE COUNT OF EACH SUBMITTED LINEUP TO FIND ACTUAL LINEUP DUPLICATE NUMBERS IN THAT CONTEST
    lineup_counts = {}
    
    ## KEEPS TRACK OF THE NUMBER OF ALL NON BLANK SUBMITTED LINEUPS IN EACH CONTEST
    lineups_processed = 0

    ## GOES THROUGH EACH LINE IN THE FILE
    for i in range(len(cs.index)):
        lu = cs.loc[i, ['Lineup']].tolist()
        ## GETS RID OF ALL BLANK OR RESERVED ENTRIES
        if lu == [np.nan]: continue
        else: pass
        lu_string = lu[0]

        
        if lu_string in lineup_counts: lineup_counts[lu_string] += 1
        else: lineup_counts[lu_string] = 1

        ## THE FOLLOWING PARSES EACH LINEUP CELL IN THE CSV TO FIND THE CAPTAIN AND FLEX PLAYER
        ## ANNOYINGLY, SOMETIMES THE CAPTAIN IS LISTED AS THE LAST PLAYER AND SOMETIMES LISTED AS THE FIRST PLAYER
        lu_string = lu_string.replace('CPT', '|CPT|')
        lu_string = lu_string.replace('FLEX', '|FLEX|')
        lu_list = lu_string.split('|')

        cpt_index = lu_list.index('CPT')
        cpt = lu_list[cpt_index + 1]
        cpt = cpt.rstrip()
        cpt = cpt.lstrip()

        if cpt in cpt_exp: cpt_exp[cpt] += 1
        else: cpt_exp[cpt] = 1

        if cpt in cpt_to_flex_dict: pass
        else: cpt_to_flex_dict[cpt] = {}

        try:
            while True:
                lu_list.remove('FLEX')
        except ValueError:
            pass

        try:
            while True:
                lu_list.remove('CPT')
        except ValueError:
            pass

        try:
            while True:
                lu_list.remove('')
        except ValueError:
            pass

        for j in range(len(lu_list)):
            p = lu_list[j]
            if p == '': continue
            else: pass

            p = p.rstrip()
            p = p.lstrip()

            if p == cpt: continue
            else:
                if p in flex_exp: flex_exp[p] += 1
                else: flex_exp[p] = 1
                if p in cpt_to_flex_dict[cpt]: cpt_to_flex_dict[cpt][p] += 1
                else: cpt_to_flex_dict[cpt][p] = 1


        lineups_processed += 1

    ## UPDATE OUR DICTIONARIES TO SHOW PERCENTAGES RATHER THAN RAW COUNTS
    for k in cpt_exp:
        cpt_occurances = cpt_exp[k]
        cpt_exp[k] = cpt_exp[k] / lineups_processed

        for r in cpt_to_flex_dict[k]:
            cpt_to_flex_dict[k][r] = cpt_to_flex_dict[k][r] / cpt_occurances

    for k in flex_exp:
        flex_exp[k] = flex_exp[k] / lineups_processed
        
    ## THE FOLLOWING SIMPLY FINDS "EXPECTED" DUPLICATE NUMBERS FOR EACH LINEUP
    ## DEFINED SIMPLY AS THE PRODUCT OF EACH PROJECTED OWNERSHIP FIGURE MULTIPLIED BY TOTAL LINEUPS PLAYED IN THAT CONTEST

    lineup_dupes = {}

    for i in range(len(cs.index)):
        lu = cs.loc[i, ['Lineup']].tolist()
        if lu == [np.nan]: continue
        else: pass
        lu_string = lu[0]

        lu_string = lu_string.replace('CPT', '|CPT|')
        lu_string = lu_string.replace('FLEX', '|FLEX|')
        lu_list = lu_string.split('|')

        cpt_index = lu_list.index('CPT')
        cpt = lu_list[cpt_index + 1]
        cpt = cpt.rstrip()
        cpt = cpt.lstrip()

        try:
            while True:
                lu_list.remove('FLEX')
        except ValueError:
            pass

        try:
            while True:
                lu_list.remove('CPT')
        except ValueError:
            pass

        try:
            while True:
                lu_list.remove('')
        except ValueError:
            pass

        ownership_rates = []

        for j in range(len(lu_list)):
            p = lu_list[j]
            if p == '': continue
            else: pass

            p = p.rstrip()
            p = p.lstrip()

            if p == cpt: ownership_rates.append(cpt_exp[p])
            else: ownership_rates.append(flex_exp[p])

        expected_dupes = np.prod(ownership_rates) * lineups_processed

        if lu[0] in lineup_dupes: pass
        else: lineup_dupes[lu[0]] = expected_dupes
     
    ## GENERATE A DATAFRAME LISTING EACH LINEUP PLAYED IN A SLATE ALONG WITH ITS DUPLICATE NUMBERS AND EXPECTED DUPLICATES
    df = pd.DataFrame.from_dict(lineup_counts, orient='index')
    df = df.reset_index()
    df.columns = ['LINEUP', 'COUNT']
    df['EXPECTED DUPES'] = df.apply(lambda r: round(lineup_dupes[r['LINEUP']], 0), axis=1)
    df['SLATE ID'] = slate_ids[contest_id]
    
    df_list.append(df)
    
    df = pd.DataFrame.from_dict({(i,j): cpt_to_flex_dict[i][j] 
                           for i in cpt_to_flex_dict.keys() 
                           for j in cpt_to_flex_dict[i].keys()},
                       orient='index')

    ## GENERATES A DATAFRAME SHOWING EVERY PLAYER IN EACH SLATE PLAYED IN THE CAPTAIN SPOT
    ## ALONG WITH HOW OFTEN EACH PLAYER WAS PLAYED IN A FLEX POSITION ALONG WITH THAT CAPTAIN
    df = df.reset_index()
    df.columns = ['PAIR', 'PERC']
    df['CPT'] = df.apply(lambda r: r['PAIR'][0], axis=1)
    df['FLEX'] = df.apply(lambda r: r['PAIR'][1], axis=1)
    df['OVR FLEX'] = df.apply(lambda r: flex_exp[r['FLEX']], axis=1)
    df['FLEX EXP DIFF'] = df.apply(lambda r: r['PERC'] - r['OVR FLEX'], axis=1)
    df['OVR CPT'] = df.apply(lambda r: cpt_exp[r['CPT']], axis=1)
    df['CPT FREQ'] = df.apply(lambda r: cpt_exp[r['CPT']] * lineups_processed, axis=1)
    df['GAME ID'] = game_ids[contest_id]
    df['SLATE ID'] = slate_ids[contest_id]
    df = df[['CPT', 'FLEX', 'PERC', 'OVR FLEX', 'FLEX EXP DIFF', 'CPT FREQ', 'OVR CPT', 'GAME ID', 'SLATE ID']].reset_index(drop=True)
    
    df = df.merge(dk_name_ids_cpt, left_on='CPT', right_on='CPT', how='left')
    df = df.merge(dk_name_ids_flex, left_on='FLEX', right_on='FLEX', how='left')
    
    df = df.merge(cpt_showdown_projections_merge_df, left_on=['SLATE ID', 'cpt_id'], right_on=['SLATE ID', 'CPT_PLAYER_ID'])
    df = df.merge(flex_showdown_projections_merge_df, left_on=['SLATE ID', 'flex_id'], right_on=['SLATE ID', 'FLEX_PLAYER_ID'])
    
    cpt_to_flex_df_list.append(df)
    
all_contests = pd.concat(df_list)

if train_or_test == '1': all_contests.to_csv('slate_lineups_and_expected_dupes_TRAINING_DATA.csv', index=False)
else: all_contests.to_csv('slate_lineups_and_expected_dupes_TEST_DATA.csv', index=False)

    
cpt_to_flex_rel_df = pd.concat(cpt_to_flex_df_list)

if train_or_test == '1': cpt_to_flex_rel_df.to_csv('cpt_flex_relationship_regression_TRAINING_DATA.csv', index=False)
else: cpt_to_flex_rel_df.to_csv('cpt_flex_relationship_regression_TEST_DATA.csv', index=False)

###
## CORRELATION BETWEEN SIMPLE DUPLICATE PREDICTION METHOD AND ACTUAL OBSERVED LINEUP DUPES: .42-.45