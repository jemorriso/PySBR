import pysbr.utils as utils
from pysbr.config.config import Config


class Sportsbook(Config):
    def __init__(self):
        super().__init__()

        self._sportsbooks = self._translate_dict(
            utils.load_yaml(utils.build_yaml_path("sportsbooks"))
        )

        self._sportsbook_ids = self._build_sportsbook_ids(
            self._sportsbooks["sportsbooks"]
        )

        self.names = {
            x["sportsbook id"]: x["name"] for x in self._sportsbooks["sportsbooks"]
        }

    def _build_sportsbook_ids(self, s):
        sportsbooks = {}
        for k in ["name", "short name"]:
            sportsbooks[k] = {}
            for x in s:
                sportsbooks[k][x[k].lower()] = x["sportsbook id"]

        return sportsbooks

    def sportsbook_config(self):
        return self._sportsbooks

    def ids(self, terms):
        ids = []
        for t in terms:
            if isinstance(t, int):
                ids.append(t)
            else:
                old_t = t
                t = t.lower()
                found = False
                # Pylance error 'id is possibly unbound' if I don't set id to None here
                id = None
                for k, v in self._sportsbook_ids.items():
                    if t in v:
                        if not found:
                            found = True
                            id = v[t]
                        else:
                            # TODO - could I raise a warning instead?
                            # raise ValueError(f"Search term {old_t} is ambiguous")
                            pass
                if not found:
                    raise ValueError(f"Could not find sportsbook {old_t}")
                else:
                    ids.append(id)

        return ids
