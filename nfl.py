import json


class NFL:
    league_id = 16
    sport_id = 4
    current_season_id = 8582

    with open("json/nfl_teams.json") as f:
        teams = json.load(f)
