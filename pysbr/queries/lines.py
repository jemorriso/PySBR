import copy

from pysbr.queries.query import Query


class Lines(Query):
    def _clean_lines(self, data):
        to_remove = [
            "boid",
            "lineid",
            "sequence",
            "dp",
            "bs",
            "iof",
            "sbid",
            "sid",
            "fpd",
            "fpn",
            "sort",
        ]
        for term in to_remove:
            for line in data:
                try:
                    line.pop(term)
                except KeyError:
                    pass
        return data

    def _copy_and_translate_data(self):
        data = copy.deepcopy(self._find_data())
        self._clean_lines(data)
        return self._translate_dict(data)
