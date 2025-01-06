WEIGHTED ELO MODEL:

In the notebook, run the last 7 cells in order to get training results (up to the 2023-24 season), testing results (on the 2023-24 season), and the new results (2024-25 up to Dec. 16).

To see the individual predictions, check out the "predictions_for_each_game_trained/test/new.csv" files after running the model.

WIN-LOSS + HOME-COURT-ADVANTAGE MODEL:

See the last columns of the output tables for predictions.

## Explanation of the Margin-Adjusted Elo Rating

Each team starts with a rating of 1200. The home team has a 114 Elo advantage, and teams playing the second night of a back-to-back have their Elo reduced by around 20 (there is a small variance depending on whether the back-to-backs were played at home or away). 

These parameters were fine tuned!

The formula for the new Elo rating after the game is:

$$E_{new} = E_{old} + P \times G \times (result - e_r),$$ where:

- $P = 15$ for regular season games, and $P = 10$ for playoff games. The ratio P_{regular season}/P_{playoffs} was tuned.
- $G = (1 + N_{game}/N_{median})^{1/3}$, where $N_{game}$ is the game's margin and $N_{median}$ the median margin of victory this season; or $G = 1$ if it's the first game of the season.
- $result = 1$ if the team won, $0$ if the team lost 
- $e_r = q_{team} / (q_{team} + q_{opponent})$, where $q_{team} = 10^{Elo_{team}/400}, q_{opponent} = 10^{Elo_{opponent}/400}$ (stands for "expected result")

I found this formula at https://www.aussportstipping.com/sports/nba/elo_ratings/. I tried to tune the $1/3$ parameter but this was more or less the best value.
