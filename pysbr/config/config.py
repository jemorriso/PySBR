import pysbr.utils as utils
from typing import Dict


class Config:
    """Base config class to be subclassed by other config classes."""

    def __init__(self):
        self._translations = utils.load_yaml(utils.build_yaml_path("dictionary"))

    def _translate_dict(self, d: Dict) -> Dict:
        """Given a dict read from config file, make field names more readable.

        The field names in the config files are mostly abbreviations from SBR, which
        aren't nice to read, so translate all dictionary keys that are SBR abbrevations
        into English words.
        """

        def _recurse(el):
            """Recursive method used to iterate over all dict keys."""
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

    def translations(self) -> Dict[str, str]:
        """Get the dict containing translations from abbrevations into words.

        The keys are abbreviations are from SBR, and the values are their translations
        into words.
        """
        return self._translations
