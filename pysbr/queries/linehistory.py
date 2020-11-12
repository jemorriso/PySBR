from pysbr.queries.lines import Lines


class LineHistory(Lines):
    def __init__(self, event_id, market_id, sportsbook_id, participant_ids):
        # only need 1 participant id, it's dumb
        super().__init__()
        self.name = "lineHistory"
        self.arg_str = self._get_args("line_history")
        self.args = {
            "eid": event_id,
            "mtid": market_id,
            "paid": sportsbook_id,
            # partids is required by the lineHistory query
            "partids": participant_ids,
        }
        self.fields = self._get_fields("line_history")

        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

    def _find_data(self):
        lines = self._raw[self.name]
        cleaned_lines = []
        for el in lines:
            cleaned_lines.append(el["lines"][0])

        return cleaned_lines
