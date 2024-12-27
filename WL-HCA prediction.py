import pandas as pd
from pathlib import Path
import datetime


def add_predictions(games_table, hca = 0.0):
    games_table['home_total_games'] = games_table['record_home_wins'] + games_table['record_home_losses'] - 1
    games_table['away_total_games'] = games_table['record_away_wins'] + games_table['record_away_losses'] - 1
    games_table['home_win_pct'] = 0.5
    games_table['away_win_pct'] = 0.5
    games_table['will_home_win'] = 'L'
    games_table.loc[(games_table['home_total_games'] > 0) & (games_table['wl_home'] == 'W'), 'home_win_pct'] = (games_table['record_home_wins'].astype(float) - 1)/games_table['home_total_games'].astype(float)
    games_table.loc[(games_table['home_total_games'] > 0) & (games_table['wl_home'] == 'L'), 'home_win_pct'] = games_table['record_home_wins'].astype(float)/games_table['home_total_games'].astype(float)
    games_table.loc[(games_table['away_total_games'] > 0) & (games_table['wl_home'] == 'W'), 'away_win_pct'] = games_table['record_away_wins'].astype(float)/games_table['away_total_games'].astype(float)
    games_table.loc[(games_table['away_total_games'] > 0) & (games_table['wl_home'] == 'L'), 'away_win_pct'] = (games_table['record_away_wins'].astype(float) - 1)/games_table['away_total_games'].astype(float)
    games_table.loc[games_table['home_win_pct'] + hca >= games_table['away_win_pct'], 'will_home_win'] = 'W'
    return games_table


accuracy = 0
total_games = 0
correct_predictions = 0

#correct_prediction_list = []
base_dir = Path.cwd()
games = pd.read_csv(base_dir / "all_games.csv")
games['game_date'] = pd.to_datetime(games['game_date'])
games_train = games[(games['game_date'] <= datetime.datetime(2023,9,30))]
games_test = games[(games['game_date'] >= datetime.datetime(2023,10,1)) & (games['game_date'] <= datetime.datetime(2024,9,30))]
games_new = games[games['game_date'] >= datetime.datetime(2024,10,1)]
#hca_values = [0,0.02,0.04,0.06,0.08,0.1,0.12,0.14,0.16,0.18,0.2]
#for hca in hca_values:
#    for idx, row in games_train.iterrows():
#        total_games, correct_predictions, prediction_list = predict_row(row, total_games, correct_predictions, prediction_list, hca)
#    correct_prediction_list.append(correct_predictions)
#    correct_predictions = 0
#print(correct_prediction_list)
#The best hca parameter consistently turns out to be 0.06
hca = 0.06
games_train = add_predictions(games_train, hca)
total_games = len(games_train)
correct_predictions = len(games_train[games_train['wl_home'] == games_train['will_home_win']])
accuracy = float(correct_predictions)/float(total_games)
print("Training: " + str(correct_predictions) + "/" + str(total_games) + ", " + str(accuracy))
games_train.to_csv(base_dir / "games_trained.csv")

games_test = add_predictions(games_test, hca)
total_games = len(games_test)
correct_predictions = len(games_test[games_test['wl_home'] == games_test['will_home_win']])
accuracy = float(correct_predictions)/float(total_games)
print("Testing: " + str(correct_predictions) + "/" + str(total_games) + ", " + str(accuracy))
games_test.to_csv(base_dir / "games_tested.csv")

games_new = add_predictions(games_new, hca)
total_games = len(games_new)
correct_predictions = len(games_new[games_new['wl_home'] == games_new['will_home_win']])
accuracy = float(correct_predictions)/float(total_games)
print("New season: " + str(correct_predictions) + "/" + str(total_games) + ", " + str(accuracy))
games_new.to_csv(base_dir / "games_tested.csv")