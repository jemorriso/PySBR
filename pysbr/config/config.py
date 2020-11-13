from pysbr.utils import Utils


class Config:
    def __init__(self):
        self.translations = self._get_translation_dict()

    def _get_translation_dict(self):
        return Utils.load_yaml(Utils.build_yaml_path("dictionary"))

    # TODO: copy to utils
    def _translate_dict(self, d, t):
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
                    elif isinstance(v, str):
                        el[k] = v.lower()
            elif isinstance(el, list):
                for x in el:
                    _recurse(x)

        _recurse(d)
