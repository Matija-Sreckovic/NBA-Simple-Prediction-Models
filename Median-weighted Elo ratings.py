import pandas as pd
import datetime
from pathlib import Path
import numpy as np

base_dir = Path(__file__).resolve().parent

games = pd.read_csv(base_dir / "all_games.csv")
games['game_date'] = pd.to_datetime(games['game_date'])
games_train = games[(games['game_date'] <= datetime.datetime(2023, 10, 1))]
games_test = games[
    (games['game_date'] >= datetime.datetime(2023, 10, 1)) & (games['game_date'] <= datetime.datetime(2024, 10, 1))]

prediction_list = []
correct_predictions_elo = 0
total_games_elo = 0
teams = games['team_name_home'].unique()
team_elos = {team: 1200 for team in teams}
median_margin = 0
margins_this_season = np.zeros(73, dtype=int)
# True for home, False for away
previous_game_dates = {team: [datetime.datetime(1, 1, 1), True] for team in teams}


def change_elo_G_cbrt(team_1_elo, team_2_elo, plus_minus_home, is_reg_seas, median_margin, btb_hh, btb_ha, btb_ah,
                      btb_aa):
    team_1_elo_factored = team_1_elo + 114
    team_2_elo_factored = team_2_elo
    if btb_hh:
        team_1_elo_factored -= 18.5
    if btb_ha:
        team_1_elo_factored -= 18.5 * 1.1
    if btb_ah:
        team_2_elo_factored -= 18.5 * 1.1
    if btb_aa:
        team_2_elo_factored -= 18.5 * 1.21
    first_score = 0
    if plus_minus_home > 0:
        first_score = 1
    G = 1
    if median_margin != 0:
        G = pow((1 + (abs(plus_minus_home) / median_margin)), 1.0 / 3)
    q_a = pow(10, team_1_elo_factored / 400)
    q_b = pow(10, team_2_elo_factored / 400)
    e_a = q_a / (q_a + q_b)
    if is_reg_seas:
        return team_1_elo + 15 * G * (first_score - e_a), team_2_elo + 15 * G * (e_a - first_score)
    else:
        return team_1_elo + 10 * G * (first_score - e_a), team_2_elo + 10 * G * (e_a - first_score)


def row_processing_G_cbrt(row, previous_row, margins_this_season, median_margin, team_elos, previous_game_dates,
                          total_games_elo, correct_predictions_elo, prediction_list):
    total_games_elo += 1
    date = row['game_date']
    home_team = row['team_name_home']
    away_team = row['team_name_away']
    home_elo = team_elos[home_team]
    away_elo = team_elos[away_team]
    btb_home_home = False
    btb_home_away = False
    btb_away_home = False
    btb_away_away = False
    home_previous_date = previous_game_dates[home_team]
    away_previous_date = previous_game_dates[away_team]
    home_elo_factored = home_elo + 114
    away_elo_factored = away_elo
    previous_date = previous_row['game_date']
    if (date.month >= 10 and previous_date.month <= 9) or (date.year == 1999 and previous_date.year == 1998):
        margins_this_season = np.zeros(73, dtype=int)
    game_margin = abs(row['plus_minus_home'])
    margins_this_season[int(game_margin) - 1] += 1
    median_margin = np.median(margins_this_season)
    if home_previous_date == [date - datetime.timedelta(days=1), True]:
        btb_home_home = True
        home_elo_factored -= 18.5
    elif home_previous_date == [date - datetime.timedelta(days=1), False]:
        btb_home_away = True
        home_elo_factored -= 18.5 * 1.1
    elif away_previous_date == [date - datetime.timedelta(days=1), True]:
        btb_away_home = True
        away_elo_factored -= 18.5 * 1.1
    elif away_previous_date == [date - datetime.timedelta(days=1), False]:
        btb_away_away = True
        away_elo_factored -= 18.5 * 1.21
    if home_elo_factored >= away_elo_factored:
        prediction_list.append(
            str(date) + ": " + str(home_team) + "-" + str(away_team) + ", predicted winner:" + str(home_team))
    else:
        prediction_list.append(
            str(date) + ": " + str(home_team) + "-" + str(away_team) + ", predicted winner:" + str(away_team))
    is_reg = True
    if row['season_type'] == 'Playoffs':
        is_reg = False
    if home_elo_factored >= away_elo_factored and row['wl_home'] == 'W':
        correct_predictions_elo += 1
    elif away_elo_factored > home_elo_factored and row['wl_home'] == 'L':
        correct_predictions_elo += 1
    team_elos[home_team], team_elos[away_team] = change_elo_G_cbrt(home_elo, away_elo, row['plus_minus_home'],
                                                                   median_margin,
                                                                   is_reg, btb_home_home, btb_home_away,
                                                                   btb_away_home, btb_away_away)
    previous_game_dates[home_team] = [date, True]
    previous_game_dates[away_team] = [date, False]
    return margins_this_season, median_margin, team_elos, previous_game_dates, total_games_elo, correct_predictions_elo, prediction_list


games_train.reset_index(drop=True, inplace=True)
for idx, row in games_train.iterrows():
    margins_this_season, median_margin, team_elos, previous_game_dates, total_games_elo, correct_predictions_elo, prediction_list = row_processing_G_cbrt(
        row, games_train.iloc[row.name - 1] if row.name > 0 else row, margins_this_season, median_margin, team_elos,
        previous_game_dates, total_games_elo, correct_predictions_elo, prediction_list)
prediction_series = pd.Series(prediction_list)
prediction_series.to_csv(base_dir / "predictions_for_each_game_train.csv")
prediction_list = []
precision = float(correct_predictions_elo) / float(total_games_elo)
print(str(correct_predictions_elo) + "/" + str(total_games_elo) + ", " + str(precision))
correct_predictions_elo = 0
total_games_elo = 0
team_elos_train = team_elos
print(team_elos)

margins_this_season = np.zeros(73, dtype=int)
median_margin = 0
games_test.reset_index(drop=True, inplace=True)
for idx, row in games_test.iterrows():
    margins_this_season, median_margin, team_elos, previous_game_dates, total_games_elo, correct_predictions_elo, prediction_list = row_processing_G_cbrt(
        row, games_test.iloc[row.name - 1] if row.name > 0 else games_train.iloc[-1], margins_this_season,
        median_margin, team_elos, previous_game_dates, total_games_elo, correct_predictions_elo, prediction_list)
precision = float(correct_predictions_elo) / float(total_games_elo)
prediction_series = pd.Series(prediction_list)
prediction_series.to_csv(base_dir / "predictions_for_each_game_test.csv")
prediction_list = []
print(str(correct_predictions_elo) + "/" + str(total_games_elo) + ", " + str(precision))
correct_predictions_elo = 0
total_games_elo = 0
team_elos_test = team_elos
print(team_elos)

games['plus_minus_home'] = games['pts_home'] - games['pts_away']
margins_this_season = np.zeros(73, dtype=int)
median_margin = 0
games_new = games[games['game_date'] >= datetime.datetime(2024, 10, 1)]
games_new.reset_index(drop=True, inplace=True)
for idx, row in games_new.iterrows():
    margins_this_season, median_margin, team_elos, previous_game_dates, total_games_elo, correct_predictions_elo, prediction_list = row_processing_G_cbrt(
        row, games_new.iloc[row.name - 1] if row.name > 0 else games_test.iloc[-1], margins_this_season, median_margin,
        team_elos, previous_game_dates, total_games_elo, correct_predictions_elo, prediction_list)
precision = float(correct_predictions_elo) / float(total_games_elo)
prediction_series = pd.Series(prediction_list)
prediction_series.to_csv(base_dir / "predictions_for_each_game_new.csv")
prediction_list = []
print(str(correct_predictions_elo) + "/" + str(total_games_elo) + ", " + str(precision))
correct_predictions_elo = 0
total_games_elo = 0
team_elos_new = team_elos
print(team_elos)
