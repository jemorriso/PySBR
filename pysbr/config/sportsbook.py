from pysbr.utils import Utils
from pysbr.config.config import Config


class Sportsbook(Config):
    def __init__(self):
        super().__init__()

        t = self._get_translation_dict()
        d = Utils.load_yaml(Utils.build_yaml_path("sportsbooks"))
        self._translate_dict(d, t)

        self._sportsbooks = self._build_sportsbooks(d["sportsbooks"])
        self._provider_accounts = self._build_provider_accounts(d["sportsbooks"])

        self.names = {v: k for k, v in self._provider_accounts["name"].items()}

    def _build_sportsbooks(self, s):
        sportsbooks = {}
        for k in ["name", "short name"]:
            sportsbooks[k] = {}
            for x in s:
                sportsbooks[k][x[k]] = x["sportsbook id"]

        return sportsbooks

    def _build_provider_accounts(self, s):
        sportsbooks = {}
        for k in ["name", "short name"]:
            sportsbooks[k] = {}
            for x in s:
                sportsbooks[k][x[k]] = x["provider account id"]

        return sportsbooks

    def sportsbooks(self):
        return self._sportsbooks

    def sportsbook_ids(self, terms):
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
                for k, v in self._sportsbooks.items():
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
