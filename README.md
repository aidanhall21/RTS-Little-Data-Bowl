# RTS-Little-Data-Bowl

This is my submission to the [Run The Sims Little Data Bowl](https://www.runthesims.com/littledatabowl/)

All simulation code and data processing was written and performed in Python with Special Thanks to the Excel Solver tool.

---

Below is a rundown of the relevant files in this repository.

1. Any .csv file that begins with "NFL" was provided to us at the start of the competition and contains game data, player projections, team information etc.
2. Inside the [DraftKings_Contest_Files_1](../master/DraftKings_Contest_Files_1) folder you'll find csv files from numerous DraftKings NFL showdown contests containing all submitted lineups for that contest. This data was used as the training data for my model/simulation.
3. The [DraftKings_Contest_Files_2](../master/DraftKings_Contest_Files_2) folder has DraftKings showdown contest files used to test my model/simulation.
4. [Contest Data Parsing.ipynb](../master/Contest%20Data%20Parsing.ipynb) and it's corresponding .py file [contest_data_parsing.py](../master/contest_data_parsing.py) is a jupyter notebook that will run through each csv in one of the folders from (2) or (3) and generate two additional files...
  * [slate_lineups_and_expected_dupes_TRAINING_DATA.csv](../master/slate_lineups_and_expected_dupes_TRAINING_DATA_raw.csv) (TRAINING will be replaced by TEST depending on which folder you're parsing) will provide you with the amount of duplicates for each submitted lineup as well as an "Expected Dupes" measure. 
  * [cpt_flex_relationship_regression_TRAINING_DATA.csv](../master/cpt_flex_relationship_regression_TEST_DATA_raw.csv) will show you exposure percentages for each CPT/FLEX pairing on any slate. There's a corresponding .xlsx file in which you can see the coefficients for the logistic regression predicting FLEX ownership given a chosen captain.
5. [Duplicate Simulations.ipynb](../master/Duplicate%20Simulations.ipynb) is another jupyter notebook that will allow you to input a Slate ID number and simulates a custom amount of lineups generated via the logistic regression model. This notebook should generate two more csvs, you'll be able to see all the outcome of the sim in simmed_lineups_slate_[Slate ID].csv and simmed_dupes_results_slate_[Slate ID].csv will compare actual duplicate counts to simulated duplicates for each submitted lineup

---


