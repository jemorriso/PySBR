from pysbr.sports.sport import TeamSport


class NFL(TeamSport):
    def __init__(self):
        super().__init__("football", "nfl")

    # load yaml
    # teams
    # markets
    #

    # function for getting current season? But too many calls - better to just use some
    #  other call like league
