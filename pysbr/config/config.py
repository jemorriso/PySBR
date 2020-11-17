import pysbr.utils as utils


class Config:
    def __init__(self):
        self._translations = utils.load_yaml(utils.build_yaml_path("dictionary"))

    def _translate_dict(self, d):
        def _recurse(el):
            if isinstance(el, dict):
                # MUST cast to list to avoid RuntimeError because d.pop()
                for k in list(el.keys()):
                    try:
                        old_k = k
                        k = t[k]

                        el[k] = el.pop(old_k)
                    except KeyError:
                        pass
                    v = el[k]
                    if isinstance(v, dict) or isinstance(v, list):
                        _recurse(v)
            elif isinstance(el, list):
                for x in el:
                    _recurse(x)

        t = self._translations
        _recurse(d)
        return d

    def translations(self):
        return self._translations
