from pysbr.sports.sport import TeamSport


class NCAAF(TeamSport):
    def __init__(self):
        super().__init__("football", "ncaaf")
