#####
### THIS NOTEBOOK RUNS THE SLATE SIMULATIONS, GENERATING A SET OF LINEUPS THAT CAN 
### THEN BE COMPARED TO ANY HAND BUILT OR OPTIMIZED GROUP OF LINEUPS TO PREDICT HOW MANY 
### OTHER DUPLICATED LINEUPS THERE WOULD BE IN THE LARGE DRAFTKINGS SHOWDOWN CONTESTS

import os
from os.path import isfile, join
import pandas as pd
import numpy as np
import re
import math

path = os.getcwd() + '/DraftKings_Contest_Files_2'
contest_files = [f for f in os.listdir(path) if f[-4:] == '.csv']

### THIS FILE WAS COPY PASTED FORM THE SHOWDOWN LINKS GOOGLE SHEET PROVIDED TO US
showdown_links = pd.read_csv('Showdown_Links.csv')

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

### GRABS DATA FROM RTS PROJECTIONS FILES INCLUDING PLAYER SALARY, POSITION, AND TEAM FOR A PARTICULAR SLATE
showdown_projections = pd.read_csv('NFL_SHOWDOWN_PROJECTIONS.csv')

### THIS FILE CONTAINS THE COEFFICIENTS FOR EACH OF THE 72 POSITION TO POSITION RELATIONSHIPS
### THERE CAN BE BETWEEN THE PLAYER IN THE CAPTAIN SPOT AND A PLAYER IN A FLEX SPOT
position_codes_dict = {}
position_codes = pd.read_csv('position_codes.csv')
for i in range(len(position_codes.index)):
    r = position_codes.loc[i, :].tolist()
    position_codes_dict[r[0]] = r[1]
    
### INPUT THE SLATE ID YOU'RE WANTING TO SIM, IDEALLY AN OUT OF SAMPLE CONTEST FROM THE DraftKings_Contest_Files_2 FOLDER
### INPUT NUMBER OF LINEUPS TO SIM (PREFERABLY 150K +)

slate_to_sim = input('Slate ID to Sim: ')
num_sims = input('Number of lineups to sim: ')

contest_id = ''

if int(slate_to_sim) not in slate_ids.values():
    raise Exception("Slate ID does not exist")
else:
    for key, value in slate_ids.items():
        if int(slate_to_sim) == value:
            contest_id = key

df_list = []
cpt_to_flex_df_list = []
lineups_df = []

### YOU CAN RUN THIS SCRIPT FOR ALL CONTEST FILES IN THE FOLDER OR JUST ONE
### IF ALL, THEN UNCOMMENT LINE 8 AND COMMENT OUT LINE 9
### IF JUST ONE THEN THE NUMBER INSIDE THE RANGE() FUNCTION SHOULD BE THE INDEX OF THE FILE NAME IN THE CONTEST_FILES ARRAY

#for i in range(len(contest_files)):

### FROM NOW UNTIL LINE 102 IS BORROWED FROM THE Contest Data Parsing NOTEBOOK, YOU CAN SEE THE COMMENTS THERE

cs = pd.read_csv(path + '/contest-standings-' + contest_id + '.csv')

#id_string = contest_files[i].replace('.', '-')
#id_string_split = id_string.split('-')
#contest_id = id_string_split[2]

slate_projections = showdown_projections
slate_projections = slate_projections[slate_projections.slate_id == slate_ids[contest_id]].reset_index(drop=True)
slate_projections = slate_projections[['slate_id', 'player_id', 'first_name', 'last_name', 'salary', 'position', 'team_name']]
slate_projections['name'] = slate_projections.apply(lambda r: r['first_name'] + ' ' + r['last_name'] if r['position'] != 'DST' else r['last_name'], axis=1)

cpt_exp = {}
cpt_to_flex_dict = {}
flex_exp = {}
lineup_counts = {}

lineups_processed = 0

for i in range(len(cs.index)):
    lu = cs.loc[i, ['Lineup']].tolist()
    if lu == [np.nan]: continue
    else: pass
    lu_string = lu[0]

    if lu_string in lineup_counts: lineup_counts[lu_string] += 1
    else: lineup_counts[lu_string] = 1

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

for k in cpt_exp:
    cpt_occurances = cpt_exp[k]
    cpt_exp[k] = cpt_exp[k] / lineups_processed

    for r in cpt_to_flex_dict[k]:
        cpt_to_flex_dict[k][r] = cpt_to_flex_dict[k][r] / cpt_occurances

for k in flex_exp:
    flex_exp[k] = flex_exp[k] / lineups_processed


### AFTER PARSING THE ACTUAL CONTEST FILES WE HAVE OUR "PROJECTED" CPT/FLEX OWNERSHIP FOR EACH PLAYER ON THE SLATE
cpt_ownership_projected = cpt_exp

players = []

cpt_salaries = {}
flex_salaries = {}

cpt_positions = {}
flex_positions = {}

cpt_teams = {}
flex_teams = {}

players_not_projected = []
cumulative_cpt_ownership = []

cpt_own_counter = 0
for i in range(len(slate_projections.index)):

    ## USING THE SHOWDOWN PROJECTIONS FILE FOR INFO ON PLAYERS, NAMES, SALARIES, POSITIONS, TEAMS
    r = slate_projections.loc[i, :].tolist()
    p = r[7]
    sal = r[4]
    position = r[5]
    team = r[6]

    if p in cpt_salaries: pass
    else: cpt_salaries[p] = sal * 1.5

    if p in flex_salaries: pass
    else: flex_salaries[p] = sal

    if p in cpt_positions: pass
    else: cpt_positions[p] = position

    if p in flex_positions: pass
    else: flex_positions[p] = position

    if p in cpt_teams: pass
    else: cpt_teams[p] = team

    if p in flex_teams: pass
    else: flex_teams[p] = team

    ## ANY PLAYER NOT IN OUR PROJECTED OWNERSHIP VALUES
    ## ...MEANING THEY WERE NOT PLAYED AS A CAPTAIN IN ANY LINEUP ON THAT PARTICULAR SLATE 
    ## WILL JUST BE GIVEN THE MINIMUM CPT OWN PROJECTION FROM ANY OTHER PLAYER
    ## WE STILL WANT TO ACCOUNT FOR SOME TINY PROBABILITY THAT THE PLAYER WILL BE PLAYED AS A CAPTAIN IN 
    ## A NEW HYPOTHETICAL CONTEST RUN UNDER THE SAME PARAMETERS
    if p not in cpt_ownership_projected: cpt_ownership_projected[p] = min(cpt_ownership_projected.values())
    else: pass

    try:
        p_cpt_own = cpt_ownership_projected[p]
        players.append(p)
        cpt_own_counter += p_cpt_own
        cumulative_cpt_ownership.append(cpt_own_counter)
    except:
        players_not_projected.append(p)

for p in players_not_projected:
    players.append(p)
    min_cpt_own = min(cpt_ownership_projected.values())
    cpt_own_counter += min_cpt_own
    cumulative_cpt_ownership.append(cpt_own_counter)

## AN ADJUSTMENT TO MAKE SURE OUR CUMULATIVE PROJECTED CAPTAIN OWNERSHIP DOES NOT EXCEED 100%
cumulative_cpt_ownership = [j * (1 / max(cumulative_cpt_ownership)) for j in cumulative_cpt_ownership]

## NOW WE CAN START THE SIM!
all_lineups = []

print('Simming lineups...')
for s in range(int(num_sims)):

    ## GENERATES A RANDOM NUMBER SO WE CAN CHOOSE OUR CAPTAIN
    c = np.random.uniform()
    cpt_index = 0
    for i in range(len(cumulative_cpt_ownership)):
        if c < cumulative_cpt_ownership[i]:
            cpt_index = i
            break
        else: continue

    lineup_captain = players[cpt_index]

    ## UPDATE THE SALARY REMAINING FOR THE REST OF OUR FLEX PLAYERS
    salary_remaining = 50000
    salary_remaining -= cpt_salaries[lineup_captain]

    ## GET OUR BASE FLEX OWNERSHIP PROJECTIONS
    flex_ownership_projected = flex_exp

    flex_players = []
    cumulative_flex_ownership = []
    flex_own_counter = 0

    ## FROM NOW UNTIL LINE 240 UPDATES OUR BASE FLEX OWNERSHIP PROJECTIONS TO ACCOUNT FOR THE CAPTAIN WE'VE ALREADY CHOSEN
    ## THE PROCESS FOR THIS IS EXPLAINED MORE IN DETAIL THROUGHOUT THE REST OF MY SUBMISSION
    for i in range(len(slate_projections.index)):
        r = slate_projections.loc[i, :].tolist()
        p = r[7]
        ## MAKE SURE WE DON'T INCLUDE OUR ALREADY SELECTED CAPTAIN IN OUR UPDATE FLEX OWN PROJECTIONS
        if p == lineup_captain: continue
        else: pass
        same_team = 0

        cpt_team = cpt_teams[lineup_captain]
        p_team = flex_teams[p]

        if cpt_team == p_team: same_team = 1
        else: pass

        cpt_pos = cpt_positions[lineup_captain]
        flex_pos = flex_positions[p]

        position_team_code = cpt_pos + flex_pos + str(same_team)


        if p not in flex_ownership_projected: flex_ownership_projected[p] = min(flex_ownership_projected.values()) / 10
        else: pass

        p_flex_own = flex_ownership_projected[p]
        cpt_overall_own_proj = cpt_ownership_projected[lineup_captain]


        flex_own_given_captain = 1 / (1 + math.exp(-(-3.795) - (0.858 * (p_flex_own * 10)) - (0.021 * (10 * cpt_overall_own_proj)) - (0.050 * (flex_salaries[p] / 1000)) - (position_codes_dict[position_team_code])))

        ## THIS ADJUSTS OUR UPDATED FLEX OWN PROJECTIONS TO ENSURE THAT OVER 5 FLEX SELECTIONS IN OUR LINEUP THE PLAYERS
        ## TRUE PROBABILITY OF APPEARING IN THAT LINEUP MATCHES OUR EXPECTATION
        adj_flex_own = 1 - ((1 - flex_own_given_captain) ** (1 / 5))

        flex_players.append(p)
        flex_own_counter += adj_flex_own
        cumulative_flex_ownership.append(flex_own_counter)

    cumulative_flex_ownership = [j * (1 / max(cumulative_flex_ownership)) for j in cumulative_flex_ownership]

    ## AN ARRAY TO HOLD THE PLAYERS IN OUR LINEUP, THE CAPTAIN IS ADDED
    lineup = []
    lineup_teams = []
    lineup_teams.append(cpt_teams[lineup_captain])
    lineup.append(lineup_captain)

    prev_sal = [50000, salary_remaining]
    ## INTIALLY SET SO THAT A FULL LINEUP CAN'T HAVE MORE THAN 500 IN SALARY REMAINING
    ## THIS CONSTRAINT GETS SLOWLY LOOSENED
    max_sal_remaining = 500

    attempts = 0
    max_attempts = 0

    while len(lineup) < 6:
        flex_index = 0

        ## A RANDOM VARIABLE TO CHOOSE A PLAYER FOR A FLEX SLOT
        fr = np.random.uniform()
        for i in range(len(cumulative_flex_ownership)):
            if fr < cumulative_flex_ownership[i]:
                flex_index = i
                salary_remaining -= flex_salaries[flex_players[flex_index]]
                lineup_teams.append(flex_players[flex_index])

                ## IF THE PLAYER SELECTION RESULTS IN AN INVALID LINEUP WE TRY ANOTHER RANDOM VARIABLE
                ## IF ENOUGH INVALID SELECTIONS ARE MADE IN A ROW THAN THE PREVIOUS PLAYER ADDED GETS DELETED
                if salary_remaining < 0 or flex_players[flex_index] in lineup or (len(lineup) == 6 and len(set(lineup_teams)) < 2) or (len(lineup) == 5 and salary_remaining > max_sal_remaining):
                    salary_remaining = prev_sal[len(lineup)]
                    lineup_teams.pop()
                    attempts += 1
                    if max_attempts > 25 and len(lineup) > 1:
                        lineup = [lineup_captain]
                        salary_remaining = 50000
                        salary_remaining -= cpt_salaries[lineup_captain]
                        prev_sal = [50000, salary_remaining]
                        max_attempts = 0
                        max_sal_remaining = 500
                        attempts = 0
                        break
                    elif attempts > 5 and len(lineup) > 1: 
                        lineup.pop()
                        lineup_teams.pop()
                        prev_sal.pop()
                        salary_remaining = prev_sal[-1]
                        ## AFTER EACH SET OF 5 STRAIGHT INVALID SELECTIONS THE MAX SALARY CONSTRAINT GETS LOOSENED SLIGHTLY
                        max_sal_remaining *= 1.2
                        max_attempts += 1
                        attempts = 0
                        break
                    else: break
                else:
                    ## IF THE FLEX PLAYER SELECTION IS VALID THAT PLAYER GETS ADDED TO THE LINEUP
                    prev_sal.append(salary_remaining)
                    lineup_teams.append(flex_players[flex_index])
                    lineup.append(flex_players[flex_index])
                    break
            else: continue

    lineup.append(salary_remaining)
    lineup.append(slate_ids[contest_id])
    all_lineups.append(lineup)

## AFTER ALL LINEUPS ARE GENERATED FOR THAT SLATE A DATAFRAME IS GENERATED AND ADDED TO THE MASTER LIST
df = pd.DataFrame(all_lineups)
lineups_df.append(df)
    
## GENERATES A CSV

all_lineups = pd.concat(lineups_df)
all_lineups.columns = ['CPT', 'FLEX', 'FLEX', 'FLEX', 'FLEX', 'FLEX', 'SALARY REM', 'SLATE ID']
all_lineups.to_csv('simmed_lineups_slate_' + slate_to_sim + '.csv', index=False)

### WE CAN NOW TEST THE ACCURACY OF OUR SIM AGAINST OUR ACTUAL DATA

all_contests_folder_2 = pd.read_csv('slate_lineups_and_expected_dupes_TEST_DATA.csv')
all_contests_folder_2 = all_contests_folder_2[all_contests_folder_2['SLATE ID'] == int(slate_to_sim)].reset_index(drop=True)

## GET FLEX AND CAPTAIN PLAYERS FROM OUR SIMS
results = {}
for i in range(len(all_lineups.index)):
    r = all_lineups.loc[i, :].tolist()
    fr = r[1:6]
    sorted_fr = sorted(fr)
    if r[0] in results:
        if str(sorted_fr) in results[r[0]]: results[r[0]][str(sorted_fr)] += 1
        else: results[r[0]][str(sorted_fr)] = 1
    else: results[r[0]] = {str(sorted_fr): 0}
        
## PARSING THE ACTUAL CONTEST FILE TO MATCH FORMATTING WITH OUR SIMS OUTPUT FORMATTING
## DRAFTKINGS SORTS PLAYERS IN THEIR CONTEST FILES IN A SPECIFIC WAY
big_list = []

for i in range(len(all_contests_folder_2.index)):
    r = all_contests_folder_2.loc[i, :].tolist()
    
    lu_string = r[0]
    
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

    flex_list = []
    for j in range(len(lu_list)):
        p = lu_list[j]
        if p == '': continue
        else: pass

        p = p.rstrip()
        p = p.lstrip()

        if p == cpt: continue
        else: flex_list.append(p)
    
    sorted_flex_list = sorted(flex_list)
    
    if cpt not in results: r.append(0)
    elif str(sorted_flex_list) in results[cpt]: r.append(results[cpt][str(sorted_flex_list)])
    else: r.append(0)
    big_list.append(r)
    
bl = pd.DataFrame(big_list)
bl.columns = ['Lineup', 'Count', 'Expected Dupes (Simple Method)', 'Slate Id', 'Simmed Duplicates']

## MAKE SURE OUR DUPLICATE NUMBERS ARE ON THE SAME SCALE IN CASE OUR NUMBER OF SIMS DOES NOT MATCH ACTUAL NUMBER
## OF CONTEST ENTRIES

num_entries = sum(bl['Count'].tolist())
bl['Simmed Duplicates'] = bl.apply(lambda r: round((r['Simmed Duplicates'] / int(num_sims)) * num_entries, 0), axis=1)

test_corr = bl['Count'].corr(bl['Simmed Duplicates'])

print('Correlation between Simmed Dupe Counts and actual dupe counts: ', round(test_corr, 2))

bl.to_csv('simmed_dupes_results_slate_' + slate_to_sim + '.csv', index=False)